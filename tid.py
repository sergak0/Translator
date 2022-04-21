from ctypes import Union

from utils import VarType, Variable


class TID:
    def __init__(self, ind, parent=None):
        self.parent = parent
        self.ind = ind
        self.objects = {}

    def check(self, name: str) -> int:
        if name in self.objects:
            return 2
        if self.parent is not None and self.parent.check(name):
            return 1
        return 0

    def get(self, name: str):
        assert type(name) == str
        if name in self.objects:
            return self.objects[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise Exception("The variable hasn't been declared in this scope")

    def set_value(self, name: str, value: Variable) -> None:
        if name in self.objects:
            if self.objects[name].type == value.type:
                self.objects[name].value = value.value
                # print(f'setted value {value.value} for {name}')
                return None
            else:
                raise Exception('Incompatible types')
        elif self.parent is not None:
            return self.parent.set_value(name, value)

        raise Exception("The variable hasn't been declared in this scope")

    def put(self, name: str, type: VarType) -> None:
        if self.check(name) == 2:
            raise Exception('Variable have already been declared in {} tid'.format(self.ind))
        self.objects[name] = Variable(type=type, value=None, name=name)
