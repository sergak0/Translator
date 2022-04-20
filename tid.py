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
