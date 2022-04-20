from tid import TID
from utils import OperandType
from typing import List


prior = {
    '++': 0, '--': 0, '~': 0,
    '*': 1, '/': 1, '%': 1,
    '+': 2, '-': 2,
    '>': 3, '<': 3, '>=': 3, '<=': 3,
    '==': 4, '!=': 4,
    '&': 5, '|': 5, '^': 5,
}

class ExpChecker: # [int/double/string/void, cnt], [res, params], [op]
    def __init__(self):
        self.all_operands = []
        self.currentTID = None
        self.stack = []

    def do(self, op):
        self.all_operands.append(op)

    def run_polis(self, all_tid: List[TID]):
        self.stack = []
        idx = 0
        while idx < len(self.all_operands):
            el = self.all_operands[idx]
            if el[0] == OperandType.SET_TID:
                self.currentTID = all_tid[el[1]]
            elif el[0] == OperandType.MOVE:
                idx = el[1]
                continue
            elif el[0] == OperandType.F_MOVE:
                if not self.stack[-1]:
                    idx = el[1]
                    continue
            elif el[0] == OperandType.VAR:
                self.stack.append(el[1])
            elif el[0] == OperandType.OP:
                self.make_operand(el[1])
            else:
                raise 'Something went wrong'
            idx += 1

    def make_operand(self, op):
        if len(op) == 2:
            res = op[0]
            params = op[1]
            params = params[::-1]
            for param in params:
                type = self.stack.pop()
                if type != param:
                    raise Exception('function got unexpected parameter')
            self.stack.append(res)
            return

        op = op[0]
        if op == '[]':
            b = self.stack.pop()
            a = self.stack.pop()
            if a[1] == 0 or b != ['int', 0]:
                raise Exception("You can't work with array this way")
            self.stack.append([a[0], a[1] - 1])
            return
        if op == ';':
            self.clear()
            return
        if op in ['++', '--', '~']:
            a = self.stack.pop()
            if a in [['int', 0], ['double', 0]]:
                self.stack.append(a)
                return
            raise Exception("You can't do " + str(op) + " to " + str(a))
        b = self.stack.pop()
        a = self.stack.pop()
        if op in ['+']:
            if a == ['string', 0] and b == ['string', 0]:
                self.stack.append(['string', 0])
                return
            if a == ['int', 0] and b == ['int', 0]:
                self.stack.append(['int', 0])
                return
            if a in [['int', 0], ['double', 0]] and b in [['int', 0], ['double', 0]]:
                self.stack.append(['double', 0])
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')
        if op in ['=']:
            if a[0] == 'string' and b[0] == 'string' and a[1] == b[1]:
                self.stack.append(a)
                return
            if a[0] in ['int', 'double'] and b[0] in ['int', 'double'] and a[1] == b[1]:
                self.stack.append(a)
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')
        if op in ['==', '!=', '>=', '>', '<=', '<']:
            if a[1] == b[1] and (a[0] == b[0] or (a[0] in ['int', 'double'] and b[0] in ['int', 'double'])):
                self.stack.append(['int', 0])
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')
        if op in ['-', '*', '/', '%', '&', '|', '%', '^']:
            if a in [['int', 0], ['double', 0]] and b in [['int', 0], ['double', 0]]:
                if a == b:
                    self.stack.append(a)
                else:
                    self.stack.append(['double', 0])
                return
            raise Exception(str(a) + ' ' + str(op) + ' ' + str(b) + ' is not available')

        raise Exception('Unknown operator')

