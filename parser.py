import re

from expression import ExpressionParser


class Variable:
    def __init__(self, name, space_name, value):
        self.name = name
        self.space_name = space_name
        self.value = value

class Function:
    def __init__(self, name, parameters, start):
        self.name = name
        self.parameters = parameters
        self.start = start


class Parser:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.expression_parser = ExpressionParser()

    def parse_func(self, s):
        name = s[:s.find('(')]
        if len(re.findall('[()]', s)) != 2 or s.find('(') == -1 or s.find(')') == -1:
            raise 'Error, there is an error in brace'

        variables = s[s.find('(') + 1:s.rfind(')')].split(',')
        for var in variables:
            var = self.get_variable_name(var)


        if s[-1] != '{':
            raise 'Error, there is no {'

        return name, variables

    def get_variable_name(self, var):
        if len(var.split()) != 1:
            raise 'There is must be only one var before assignment symbol'

        var = var.split()
        if len(re.findall('[0-9]', var[0])):
            raise 'Error in variable name'

        if len(re.findall('[a-zA-Z_0-9]', var)) != len(var):
            raise 'Error in variable name'

        return var

    def get_variables_in_space(self, space_name):
        return {k: v for k, v in self.variables if v.space_name == space_name}

    def parse_assignment(self, s, space_name):
        x = s.find('=')
        if x == -1:
            raise 'Error, there is not assignment symbol'

        var = self.get_variable_name(s[:x])
        return self.expression_parser(s[x + 1:], self.get_variables_in_space(space_name))

    def parse_block(self, text, space_name):
        pass

