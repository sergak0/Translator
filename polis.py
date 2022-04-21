from typing import Union

from pydantic import BaseModel

from tid import TID
from utils import OperandType, VarType, Variable, copy_var
from typing import List


prior = {
    '++': 0, '--': 0, '~': 0,
    '*': 1, '/': 1, '%': 1,
    '+': 2, '-': 2,
    '>': 3, '<': 3, '>=': 3, '<=': 3,
    '==': 4, '!=': 4,
    '&': 5, '|': 5, '^': 5,
}

base_types = {
    'string': VarType(type_name='string', cnt=1),
    'double': VarType(type_name='double', cnt=0),
    'int': VarType(type_name='int', cnt=0)
}

default_value = {
    'string': '',
    'double': 0,
    'int': 0,
    'void': None,
}

all_TID: List[TID] = []


class ExpChecker:  # [int/double/string/void, cnt], [res, params], [op]
    def __init__(self, all_operands=[]):
        self.all_operands = all_operands
        self.currentTID = None
        self.stack = []

    def do(self, op) -> None:
        self.all_operands.append(op)

    def run_polis(self) -> Variable:
        self.stack = []
        idx = 0
        while idx < len(self.all_operands):
            el = self.all_operands[idx]
            # print(idx, el)
            if el[0] == OperandType.SET_TID:
                if el[1] == -1:
                    self.currentTID = self.currentTID.parent
                else:
                    self.currentTID = all_TID[el[1]]
            elif el[0] == OperandType.MOVE:
                idx = el[1]
                continue
            elif el[0] == OperandType.F_MOVE:
                if not self.get_val(self.stack.pop()).value:
                    idx = el[1]
                    continue
            elif el[0] == OperandType.VAR:
                self.stack.append(el[1])
            elif el[0] == OperandType.CONST:
                self.stack.append(el[1])
            elif el[0] == OperandType.FUNC:
                self.make_func(el[1])
            elif el[0] == OperandType.RETURN:
                return self.get_val(self.stack.pop())
            elif el[0] == OperandType.OP:
                self.make_operand(el[1])
            else:
                raise 'Something went wrong'
            idx += 1

        return Variable(type=VarType(type_name='void', cnt=0))

    def make_func(self, name: str) -> None:
        fn: Function = self.currentTID.get(name)
        if type(fn) != Function:
            raise Exception('variable cannot be used with ()')

        params = fn.params[::-1]

        last_version = []
        for el in fn.polis.all_operands:
            if el[0] == OperandType.SET_TID:
                now = all_TID[el[1]]
                x = TID(ind=now.ind, parent=now.parent)
                x.objects = now.objects.copy()
                last_version.append((el[1], x))

        fn.polis.currentTID = all_TID[fn.tid_ind]
        fn.polis.stack = []
        for i, el in enumerate(fn.polis.all_operands):
            print('fn {} {}'.format(i, el))

        for param in params:
            fn.polis.currentTID.set_value(param, self.get_val(self.stack.pop()))

        res = fn.polis.run_polis()
        print('Polis TID {}'.format(fn.polis.currentTID.objects))

        for ind, x in last_version:
            all_TID[ind] = x

        if res.type == fn.type:
            self.stack.append(res)
        else:
            raise Exception('function return incorrect type')

    def get_val(self, x: Union[str, Variable]) -> Variable:
        if type(x) == str:
            ans = self.currentTID.get(x)
        else:
            ans = x

        ans = copy_var(ans)
        if ans.value is None:
            ans.value = default_value[ans.type.type_name]
            for i in range(ans.type.cnt - (ans.type.type_name == 'string')):
                ans.value = [ans.value]

        if ans.type == base_types['int']:
            ans.value = int(ans.value)

        return ans

    def make_operand(self, op):
        if op == '[]':
            b = self.get_val(self.stack.pop())
            a = self.get_val(self.stack.pop())
            # print(a, b)
            if a.type.cnt == 0 or b.type != base_types['int']:
                raise Exception("You can't work with array this way")

            if b.value < 0 or b.value > 1e6:
                raise Exception('Index of array must be >= 0 and <= 1e6, yours is {}'.format(b.value))

            if len(a.value) <= b.value:
                d = default_value[a.type.type_name]
                for i in range(a.type.cnt - 1):
                    d = [d]
                a.value += [d] * (b.value - len(a.value) + 1)

            self.stack.append(Variable(type=VarType(type_name=a.type.type_name, cnt=a.type.cnt - 1),
                                       value=a.value[b.value],
                                       par=[a, b.value]))
            return

        if op in ['++', '--', '~']:
            a = self.get_val(self.stack.pop())
            if a.type in [base_types['int'], base_types['double']]:
                if op == '++':
                    a.value += 1
                elif op == '--':
                    a.value -= 1
                elif op == '~':
                    a.value = -a.value

                self.stack.append(a)
                if op in ['++', '--']:
                    self.currentTID.set_value(a.name, a)

                return
            raise Exception("You can't do " + str(op) + " to " + str(a))

        b: Variable = self.get_val(self.stack.pop())
        a: Variable = self.get_val(self.stack.pop())
        if op in ['+']:
            if (a.type == base_types['string'] and b.type == base_types['string']) or \
                    (a.type == base_types['int'] and b.type == base_types['int']):
                a.value += b.value
                self.stack.append(a)
                return

            if a.type in [base_types['int'], base_types['double']] and b.type in [base_types['int'], base_types['double']]:
                a.value += b.value
                a.type.type_name = 'double'
                self.stack.append(a)
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')

        if op in ['=']:
            if a.type == b.type:
                a.value = b.value
                while a.par is not None:
                    ind, val = a.par[1], a.value
                    a = a.par[0]
                    a.value[ind] = val

                self.currentTID.set_value(a.name, a)
                return

            if a.type.type_name in ['int', 'double'] and b.type.type_name in ['int', 'double'] and a.type.cnt == b.type.cnt:
                a.value = b.value

                while a.par is not None:
                    ind, val = a.par[1], a.value
                    a = a.par[0]
                    a.value[ind] = val

                self.currentTID.set_value(a.name, a)
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')

        if op in ['==', '!=', '>=', '>', '<=', '<']:
            if a.type.cnt == 0 and b.type.cnt == 0 and (b.type == a.type or a.type.type_name in ['int', 'double'] and b.type.type_name in ['int', 'double']):
                a.value = make_binary_op(a.value, b.value, op)
                a.type.type_name = 'int'
                self.stack.append(a)
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')

        if op in ['&', '|', '^']:
            if a.type == base_types['int'] and b.type == base_types['int']:
                a.value = make_binary_op(a.value, b.value, op)
                self.stack.append(a)
                return
            raise Exception('Operation {} available only for integers'.format(op))

        if op in ['-', '/', '%', '*']:
            if a.type in [base_types['int'], base_types['double']] and b.type in [base_types['int'], base_types['double']]:
                if a.type != b.type:
                    a.type = base_types['double']
                a.value = make_binary_op(a.value, b.value, op)
                self.stack.append(a)
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')

        raise Exception('Unknown operator {}'.format(op))


class Function(BaseModel):
    type: VarType
    params: List[str]
    polis: ExpChecker
    tid_ind: int

    class Config:
        arbitrary_types_allowed = True


# ['-', '*', '/', '%', '&', '|', '%', '^']:
def make_binary_op(a, b, op):
    if op == '==':
        return a == b
    if op == '!=':
        return a != b
    if op == '>=':
        return a >= b
    if op == '<=':
        return a <= b
    if op == '>':
        return a > b
    if op == '<':
        return a < b

    if op == '-':
        return a - b
    if op == '+':
        return a + b
    if op == '/':
        return a / b
    if op == '*':
        return a * b
    if op == '%':
        return a % b
    if op == '&':
        return a & b
    if op == '|':
        return a | b
    if op == '^':
        return a ^ b
