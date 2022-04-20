from lexical import *
from polis import *
from utils import OperandType, VarType
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
all_TID = [currentTID]
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
    CheckToken(idx, 'fn')
    idx += 1
    idx, dtype, cnt = FuncType(idx, 1)
    idx, name = Name(idx, 1)
    if idx == len(tokens) or tokens[idx] != '(':
        raise Exception('Expect (')
    idx += 1
    idx, params, names = Params(idx, 1)
    currentTID.put(name, ['fn', [VarType(name=dtype, cnt=cnt), params]])
    func_type = VarType(name=dtype, cnt=cnt)
    if idx == len(tokens) or tokens[idx] != ')':
        raise Exception('Expect )')
    idx += 1

    stack_cp = polis.stack.copy()
    polis.stack.clear()
    idx = Block(idx, names=names, types=params)
    currentTID.objects[name] = ['fn', [VarType(name=dtype, cnt=cnt), params, polis.stack.copy()]]
    if name == 'main':
        polis.stack = stack_cp + polis.stack
    else:
        polis.stack = stack_cp

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
    params.append(VarType(name=dtype, cnt=cnt))
    idx, name = Name(idx, 1)
    names.append(name)
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx, dtype, cnt = Type(idx, 1)
        params.append(VarType(name=dtype, cnt=cnt))
        idx, name = Name(idx, 1)
        names.append(name)
    if ask:
        return idx, params, names
    return idx


def Block(idx, need_new_TID=1, names=[], types=[]):
    global currentTID
    CheckToken(idx, '{')
    idx += 1
    if need_new_TID:
        currentTID = TID(currentTID)
        polis.do([OperandType.SET_TID, len(all_TID)])
        all_TID.append(currentTID)

    for name, type in zip(names, types):
        currentTID.put(name, type)

    while True:
        if idx == len(tokens):
            raise Exception('Expect }')
        if tokens[idx] == '}':
            idx += 1
            break
        idx = Operator(idx)

    if need_new_TID:
        currentTID = currentTID.parent
    return idx


def Operator(idx):
    global currentTID
    if idx == len(tokens):
        raise Exception('Expect operator definition')
    if tokens[idx] == 'for':
        currentTID = TID(currentTID)
        idx = For(idx)
        currentTID = currentTID.parent
    elif tokens[idx] == 'while':
        currentTID = TID(currentTID)
        idx = While(idx)
        currentTID = currentTID.parent
    elif tokens[idx] == 'if':
        currentTID = TID(currentTID)
        idx = If(idx)
        currentTID = currentTID.parent
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

    start_exp = len(polis.stack)
    idx = Exp(idx)
    CheckToken(idx, ';')
    idx += 1

    move_ind = len(polis.stack)
    polis.do([OperandType.F_MOVE, -1])
    stack_cp = polis.stack.copy()

    expr_begin = idx
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1

    polis.stack = stack_cp
    idx, x = Block(idx, 0)
    _ = Exp(expr_begin)
    polis.do([OperandType.MOVE, start_exp])
    polis.stack[move_ind][1] = len(polis.stack)
    return idx


def Definition(idx):
    idx, dtype, cnt = Type(idx, 1)
    idx, name = Name(idx, 1)
    currentTID.put(name, VarType(name=dtype, cnt=cnt))
    if idx != len(tokens) and tokens[idx] == '=':
        polis.do([OperandType.VAR, name])
        idx += 1
        idx = Exp(idx)
        polis.do([OperandType.OP, '='])

    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx, name = Name(idx, 1)
        currentTID.put(name, VarType(name=dtype, cnt=cnt))
        if idx != len(tokens) and tokens[idx] == '=':
            polis.do([OperandType.VAR, name])
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

    move_ind = len(polis.stack)
    polis.do([OperandType.F_MOVE, -1])

    idx = Block(idx)

    polis.stack[move_ind][1] = len(polis.stack) + 1
    move_ind = len(polis.stack)
    polis.do([OperandType.MOVE, len(polis.stack)])

    if idx != len(tokens) and tokens[idx] == 'else':
        idx += 1
        idx = Block(idx)
        polis.stack[move_ind][1] = len(polis.stack)

    return idx


def While(idx):
    CheckToken(idx, 'while')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    exp_ind = len(polis.stack)
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1

    move_ind = len(polis.stack)
    polis.do([OperandType.F_MOVE, -1])
    idx = Block(idx)
    polis.do([OperandType.MOVE, exp_ind])
    polis.stack[move_ind] = len(polis.stack)

    return idx


def Return(idx):
    CheckToken(idx, 'return')
    idx += 1
    idx = Exp(idx)
    polis.do([OperandType.OP, 'return'])
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
    dtype = currentTID.get(name)

    if idx != len(tokens) and tokens[idx] == '(':
        idx += 1
        if idx != len(tokens) and tokens[idx] == ')':
            if len(dtype[1][1]):
                raise Exception('Wrong count of parameters')
            polis.do([OperandType.VAR, name])
            return idx + 1
        else:
            idx, cnt = Enumeration(idx, 1)
            if len(dtype[1][1]) != cnt:
                raise Exception('Wrong count of parameters')
            polis.do([OperandType.VAR, name])
            CheckToken(idx, ')')
            return idx + 1

    polis.do([OperandType.VAR, name])
    while idx != len(tokens) and tokens[idx] == '[':
        idx = Exp(idx + 1)
        CheckToken(idx, ']')
        idx += 1
        polis.do([OperandType.OP, '[]'])
    return idx


def Prior2(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    if tokens[idx] in ['--', '++']:
        idx += 1
        idx = Prior2(idx)
        polis.do([OperandType.OP, tokens[idx]])
        return idx

    if tokens[idx] == '-':
        idx += 1
        idx = Prior2(idx)
        polis.do([OperandType.OP, '~'])
        return idx

    if tokens[idx].type == 'string_const':
        name = str(randint(0, 1e9))
        currentTID.put(name, VarType(name='string', cnt=1, value=tokens[idx].text))
        polis.do([OperandType.VAR, name])
        return idx + 1

    if tokens[idx].type == 'numeric_const':
        name = str(randint(0, 1e9))
        currentTID.put(name, VarType(name='int', cnt=0, value=int(tokens[idx].text)))
        polis.do([OperandType.VAR, name])
        return idx + 1

    if tokens[idx].type == 'double_const':
        name = str(randint(0, 1e9))
        currentTID.put(name, VarType(name='double', cnt=0, value=float(tokens[idx].text)))
        polis.do([OperandType.VAR, name])
        return idx + 1

    return Prior1(idx)


def Prior3(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior2(idx)
    if tokens[idx] in ['*', '/', '%']:
        idx += 1
        idx = Prior3(idx)
        polis.do([OperandType.OP, tokens[idx]])
        return idx
    return idx


def Prior4(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior3(idx)
    if tokens[idx] in ['+', '-']:
        idx += 1
        idx = Prior4(idx)
        polis.do([OperandType.OP, tokens[idx]])
        return idx

    return idx


def Prior5(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior4(idx)

    if tokens[idx] in ['>', '<', '>=', '<=']:
        idx += 1
        idx = Prior5(idx)
        polis.do([OperandType.OP, tokens[idx]])
        return idx

    return idx


def Prior6(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior5(idx)
    if tokens[idx] in ['!=', '==']:
        idx += 1
        idx = Prior6(idx)
        polis.do([OperandType.OP, tokens[idx]])
        return idx
    return idx


def Prior7(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior6(idx)

    if tokens[idx] in ['&', '|', '^']:
        idx += 1
        idx = Prior7(idx)
        polis.do([OperandType.OP, tokens[idx]])
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
    print(polis.stack)

    currentTID.objects['main'][1][-1] = []
    if 'main' not in currentTID.objects or currentTID.objects['main'] != ['fn', [['void', 0], [], []]]:
        raise Exception("Expect fn int main() in program")
