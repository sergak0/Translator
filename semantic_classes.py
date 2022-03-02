class TID:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def check_id(self, name):
        current = self
        while current is not None:
            if name in current.vars:
                return 1
            current = current.parent
        return 0

    def put_id(self, name, type, value):
        if self.check_id(name):
            raise Exception('Variable has been already declared in this scope')
        self.vars[name] = VarInformation(name, type, value)


class VarInformation:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value


class ExpChecker:
    def __init__(self):
        self.stack = []

    def push_op(self, op):
        self.stack += op

    def push_type(self, type): # int, double, string
        self.stack += type

    def check_op(self, op):
        pass

    def check_uno(self, op):
        pass
