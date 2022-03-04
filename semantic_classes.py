class TID:
    def __init__(self, parent=None):
        self.parent = parent
        self.objects = {}

    def check(self, name):
        if name in self.objects:
            return 2
        if self.parent is not None and self.parent.check(name):
            return 1
        return 0

    def get(self, name):
        if name in self.objects:
            return self.objects[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise Exception("The variable hasn't been declared in this scope")

    def put(self, name, type):
        if self.check(name) == 2:
            raise Exception('Variable have already been declared')
        self.objects[name] = type


class ExpChecker: # [int/double/string/void, cnt], [res, params], [op]
    def __init__(self):
        self.stack = []

    def push_type(self, type):
        self.stack.append(type)

    def do(self, op):
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

    def clear(self):
        self.stack = []