from lexical import *
from polis import *
from utils import OperandType, VarType, Variable
from tid import TID
from random import randint

tokens = []  # List of lexical/Token

special_tokens_inversed = {
    'operator': ['++', '--', '-', '*', '/', '%', '+', '>', '<', '>=', '<=', '==', '!=', '&', '|', '%', '=', '^'],
    'punctuation': [';', ',', '{', '}'],
    'reserved': ['for', 'while', 'if', 'void', 'int', 'double', 'string', 'fn', 'return'],
    '[]': ['[', ']'],
    '()': ['(', ')']
}

special_tokens = {}

currentTID = TID()
polis = ExpChecker()
func_type = None


def CheckToken(idx, token):
    if idx == len(tokens) or tokens[idx] != token:
        raise Exception('Expect ' + token)


def Program(idx):
    if idx != len(tokens) and tokens[idx] == 'fn':  # <Func><Program> | <Func>
        idx = Func(idx)
        if idx != len(tokens):
            idx = Program(idx)
    elif idx != len(tokens) and (tokens[idx] == 'int' or tokens[idx] == 'double' or tokens[idx] == 'string'):  # <Definition>;<Program> | <Definition>;
        idx = Definition(idx)
        CheckToken(idx, ';')
        idx += 1
        if idx != len(tokens):
            idx = Program(idx)
    elif idx != len(tokens):
        raise Exception('Expect fn or variable type')
    return idx


def Func(idx):
    global currentTID
    global func_type

    stack_cp = polis.all_operands.copy()
    polis.all_operands.clear()

    CheckToken(idx, 'fn')
    idx += 1
    idx, dtype, cnt = FuncType(idx, 1)
    idx, name = Name(idx, 1)

    if name == 'main':
        polis.do([OperandType.SET_TID, 1])

    if idx == len(tokens) or tokens[idx] != '(':
        raise Exception('Expect (')
    idx += 1
    idx, params, names = Params(idx, 1)

    if idx == len(tokens) or tokens[idx] != ')':
        raise Exception('Expect )')
    idx += 1

    currentTID.objects[name] = Function(type=VarType(type_name=dtype, cnt=cnt),
                                       params=names,
                                       polis=ExpChecker([]))

    idx = Block(idx, need_new_TID=False)

    if name == 'main':
        polis.do([OperandType.SET_TID, -1])

    currentTID.objects[name].polis.all_operands = polis.all_operands.copy()

    print('put func {}'.format(name))
    if name == 'main':
        x = polis.all_operands.copy()
        for i in range(len(x)):
            if x[i][0] == OperandType.F_MOVE or x[i][0] == OperandType.MOVE:
                x[i][1] += len(stack_cp)

        polis.all_operands = stack_cp + x
        if len(names) or dtype != 'int' or cnt != 0:
            raise Exception('incorrect main func')
    else:
        polis.all_operands = stack_cp

    return idx


def FuncType(idx, ask=0):
    if idx == len(tokens):
        raise Exception('Expect variable type')
    if tokens[idx] == 'void':
        if ask:
            return idx + 1, 'void', 0
        return idx + 1
    if tokens[idx] != 'int' and tokens[idx] != 'double' and tokens[idx] != 'string':
        raise Exception('Unknown type encountered')
    dtype = tokens[idx].text
    idx += 1
    cnt = 0
    while idx != len(tokens) and tokens[idx] == '[':
        idx += 1
        CheckToken(idx, ']')
        idx += 1
        cnt += 1
    if ask:
        if dtype == 'string':
            cnt += 1
        return idx, dtype, cnt
    return idx


def Type(idx, ask_type=0):
    if idx == len(tokens):
        raise Exception('Expect variable type')
    if tokens[idx] != 'int' and tokens[idx] != 'double' and tokens[idx] != 'string':
        raise Exception('Unknown type encountered')
    dtype = tokens[idx].text
    idx += 1
    cnt = 0
    while idx != len(tokens) and tokens[idx] == '[':
        idx += 1
        CheckToken(idx, ']')
        idx += 1
        cnt += 1
    if ask_type:
        if dtype == 'string':
            cnt += 1
        return idx, dtype, cnt
    return idx


def Name(idx, ask=0):
    if idx == len(tokens) or tokens[idx].type != 'name':
        raise Exception('Expect variable name')
    name = tokens[idx].text

    idx += 1
    if ask:
        return idx, name
    return idx


def Params(idx, ask=0):
    if idx == len(tokens) or (tokens[idx] != 'int' and tokens[idx] != 'double' and tokens[idx] != 'string'):
        if ask:
            return idx, [], []
        return idx
    params = []
    names = []
    idx, dtype, cnt = Type(idx, 1)
    params.append(VarType(type_name=dtype, cnt=cnt))
    idx, name = Name(idx, 1)
    names.append(name)
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx, dtype, cnt = Type(idx, 1)
        params.append(VarType(type_name=dtype, cnt=cnt))
        idx, name = Name(idx, 1)
        names.append(name)
    if ask:
        return idx, params, names
    return idx


def Block(idx, need_new_TID=True):
    global currentTID
    CheckToken(idx, '{')
    idx += 1

    if need_new_TID:
        polis.do([OperandType.SET_TID, 1])

    while True:
        if idx == len(tokens):
            raise Exception('Expect }')
        if tokens[idx] == '}':
            idx += 1
            break
        idx = Operator(idx)

    if need_new_TID:
        polis.do([OperandType.SET_TID, -1])

    return idx


def Operator(idx):
    global currentTID
    if idx == len(tokens):
        raise Exception('Expect operator definition')
    if tokens[idx] == 'for':
        polis.do([OperandType.SET_TID, 1])
        idx = For(idx)
        polis.do([OperandType.SET_TID, -1])
    elif tokens[idx] == 'while':
        polis.do([OperandType.SET_TID, 1])
        idx = While(idx)
        polis.do([OperandType.SET_TID, -1])
    elif tokens[idx] == 'if':
        idx = If(idx)
    elif tokens[idx] == 'return':
        idx = Return(idx)
    elif tokens[idx] == 'int' or tokens[idx] == 'double' or tokens[idx] == 'string':
        idx = Definition(idx)
        CheckToken(idx, ';')
        idx += 1
    else:
        idx = Enumeration(idx)
        CheckToken(idx, ';')
        idx += 1
    return idx


def For(idx):
    CheckToken(idx, 'for')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    idx = Definition(idx)
    CheckToken(idx, ';')
    idx += 1

    start_exp = len(polis.all_operands)
    idx = Exp(idx)
    CheckToken(idx, ';')
    idx += 1

    move_id = len(polis.all_operands)
    polis.do([OperandType.F_MOVE, -1])
    stack_cp = polis.all_operands.copy()

    expr_begin = idx
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1

    polis.all_operands = stack_cp
    idx = Block(idx, False)
    _ = Exp(expr_begin)
    polis.do([OperandType.MOVE, start_exp])

    polis.all_operands[move_id][1] = len(polis.all_operands)
    return idx


def Definition(idx):
    idx, dtype, cnt = Type(idx, 1)
    idx, name = Name(idx, 1)
    polis.do([OperandType.DEFINE, Variable(name=name, type=VarType(type_name=dtype, cnt=cnt))])
    polis.do([OperandType.VAR, name])

    if idx != len(tokens) and tokens[idx].text == '=':
        idx += 1
        idx = Exp(idx)
        polis.do([OperandType.OP, '='])

    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx, name = Name(idx, 1)
        polis.do([OperandType.DEFINE, Variable(name=name, type=VarType(type_name=dtype, cnt=cnt))])
        polis.do([OperandType.VAR, name])

        if idx != len(tokens) and tokens[idx].text == '=':
            idx += 1
            idx = Exp(idx)
            polis.do([OperandType.OP, '='])
    return idx


def If(idx):
    CheckToken(idx, 'if')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1

    move_ind = len(polis.all_operands)
    polis.do([OperandType.F_MOVE, -1])

    idx = Block(idx)

    polis.all_operands[move_ind][1] = len(polis.all_operands) + 1
    move_ind = len(polis.all_operands)
    polis.do([OperandType.MOVE, len(polis.all_operands) + 1])

    if idx != len(tokens) and tokens[idx] == 'else':
        idx += 1
        idx = Block(idx)
        polis.all_operands[move_ind][1] = len(polis.all_operands)

    return idx


def While(idx):
    CheckToken(idx, 'while')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    exp_ind = len(polis.all_operands)
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1

    move_ind = len(polis.all_operands)
    polis.do([OperandType.F_MOVE, -1])
    idx = Block(idx, False)
    polis.do([OperandType.MOVE, exp_ind])
    polis.all_operands[move_ind][1] = len(polis.all_operands)

    return idx


def Return(idx):
    CheckToken(idx, 'return')
    idx += 1
    idx = Exp(idx)
    polis.do([OperandType.RETURN, 'return'])
    CheckToken(idx, ';')
    idx += 1
    return idx


def Enumeration(idx, ask=0):
    idx = Exp(idx)
    cnt = 0
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx = Exp(idx)
        cnt += 1
    if ask:
        return idx, cnt + 1
    return idx


def Prior1(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    if tokens[idx] == '(':
        idx = Exp(idx + 1)
        CheckToken(idx, ')')
        return idx + 1

    idx, name = Name(idx, 1)

    if idx != len(tokens) and tokens[idx] == '(':
        dtype = currentTID.get(name)
        idx += 1
        if idx != len(tokens) and tokens[idx] == ')':
            if len(dtype.params):
                raise Exception('Wrong count of parameters')
            polis.do([OperandType.FUNC, name])
            return idx + 1
        else:
            idx, cnt = Enumeration(idx, 1)
            if len(dtype.params) != cnt:
                raise Exception('Wrong count of parameters')
            polis.do([OperandType.FUNC, name])
            CheckToken(idx, ')')
            return idx + 1

    polis.do([OperandType.VAR, name])
    while idx != len(tokens) and tokens[idx].text == '[':
        idx = Exp(idx + 1)
        CheckToken(idx, ']')
        idx += 1
        polis.do([OperandType.OP, '[]'])
    return idx


def Prior2(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    if tokens[idx].text in ['--', '++']:
        token = tokens[idx].text
        idx += 1
        idx = Prior2(idx)
        polis.do([OperandType.OP, token])
        return idx

    if tokens[idx].text == '-':
        idx += 1
        idx = Prior2(idx)
        polis.do([OperandType.OP, '~'])
        return idx

    if tokens[idx].type == 'string_const':
        polis.do([OperandType.CONST, Variable(type=VarType(type_name='string', cnt=1),
                                              value=tokens[idx].text[1:-1])])
        return idx + 1

    if tokens[idx].type == 'numeric_const':
        polis.do([OperandType.CONST, Variable(type=VarType(type_name='int', cnt=0),
                                              value=int(tokens[idx].text))])
        return idx + 1

    if tokens[idx].type == 'double_const':
        polis.do([OperandType.CONST, Variable(type=VarType(type_name='double', cnt=0),
                                              value=float(tokens[idx].text))])
        return idx + 1

    return Prior1(idx)


def Prior3(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior2(idx)
    if tokens[idx].text in ['*', '/', '%']:
        token = tokens[idx].text
        idx += 1
        idx = Prior3(idx)
        polis.do([OperandType.OP, token])
        return idx
    return idx


def Prior4(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior3(idx)
    if tokens[idx].text in ['+', '-']:
        token = tokens[idx].text
        idx += 1
        idx = Prior4(idx)
        polis.do([OperandType.OP, token])
        return idx

    return idx


def Prior5(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior4(idx)

    if tokens[idx].text in ['>', '<', '>=', '<=']:
        token = tokens[idx].text
        idx += 1
        idx = Prior5(idx)
        polis.do([OperandType.OP, token])
        return idx

    return idx


def Prior6(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior5(idx)
    if tokens[idx].text in ['!=', '==']:
        token = tokens[idx].text
        idx += 1
        idx = Prior6(idx)
        polis.do([OperandType.OP, token])
        return idx
    return idx


def Prior7(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior6(idx)

    if tokens[idx].text in ['&', '|', '^']:
        token = tokens[idx].text
        idx += 1
        idx = Prior7(idx)
        polis.do([OperandType.OP, token])
        return idx

    return idx


def Prior8(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior7(idx)
    if tokens[idx] == '=':
        idx += 1
        idx = Prior8(idx)
        polis.do([OperandType.OP, '='])
        return idx
    return idx


def Exp(idx):
    return Prior8(idx)


if __name__ == "__main__":
    text = open('examples/text.txt', 'r').readlines()
    text = ' '.join(text)
    text = [i for i in text if i != '\n']

    print("Text: ")
    print(text)

    for key, values in special_tokens_inversed.items():
        for value in values:
            special_tokens[value] = key

    fsm = FSM(special_tokens)
    print('Lexical: ')
    tokens = fsm.process(text)
    for token in tokens:
        print(token)
    print('Syntactic and Semantic: ')
    Program(0)

    if 'main' not in currentTID.objects:
        raise Exception("Expect fn int main() in program")

    polis.run_polis(currentTID, currentTID)

    for name, el in currentTID.objects.items():
        if type(el) != Function:
            print(el)
            continue
        print(name)
        for i, el in enumerate(el.polis.all_operands):
            print(i, el)

