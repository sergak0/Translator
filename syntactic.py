from lexical import *
import ctypes


tokens = []  # List of lexical/Token


def CheckToken(idx, token):
    if idx == len(tokens) or tokens[idx] != token:
        raise Exception('Expect ' + token)


def Program(idx):
    if tokens[idx] == 'fn':  # <Func><Program> | <Func>
        idx = Func(idx)
        if idx != len(tokens):
            idx = Program(idx)
    else:  # <Definition>;<Program> | <Definition>;
        idx = Definition(idx)
        CheckToken(idx, ';')
        idx += 1
        if idx != len(tokens):
            idx = Program(idx)
    return idx


def Func(idx):
    CheckToken(idx, 'fn')
    idx += 1
    idx = Type(idx)
    idx = Name(idx)
    if idx == len(tokens) or tokens[idx] != '(':
        raise Exception('Expect (')
    idx += 1
    if idx == len(tokens) or tokens[idx] != ')':
        raise Exception('Expect )')
    idx += 1
    idx = Block(idx)
    return idx


def Type(idx):
    if idx == len(tokens):
        raise Exception('Expect variable type')
    if tokens[idx] != 'int' and tokens[idx] != 'double' and tokens[idx] != 'string':
        raise Exception('Unknown type encountered')
    idx += 1
    while idx != len(tokens) and tokens[idx] == '[':
        idx += 1
        CheckToken(idx, ']')
        idx += 1
    return idx


def Name(idx):
    if idx == len(tokens) or tokens[idx].type != 'name':
        raise Exception('Expect variable name')
    idx += 1
    return idx


def Params(idx):
    if idx == len(tokens):
        raise Exception('Expect params list')
    idx = Type(idx)
    idx = Name(idx)
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx = Params(idx)
    return idx


def Block(idx):
    CheckToken(idx, '{')
    idx += 1
    while True:
        if idx == len(tokens):
            raise Exception('Expect }')
        if idx == '}':
            idx += 1
            break
        idx = Operator(idx)
    return idx


def Operator(idx):
    if idx == len(tokens):
        raise Exception('Expect operator definition')
    if tokens[idx] == 'for':
        idx = For(idx)
    elif tokens[idx] == 'while':
        idx = While(idx)
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
    idx = Exp(idx)
    CheckToken(idx, ';')
    idx += 1
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1
    idx = Block(idx)
    return idx


def Definition(idx):
    idx = Type(idx)
    idx = Name(idx)
    if idx != len(tokens) and tokens[idx] == '=':
        idx += 1
        idx = Exp(idx)
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx = Name(idx)
        if idx != len(tokens) and tokens[idx] == '=':
            idx += 1
            idx = Exp(idx)
    return idx


def If(idx):
    CheckToken(idx, 'if')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1
    idx = Block(idx)
    if idx != len(tokens) and tokens[idx] == 'else':
        idx += 1
        idx = Block(idx)
    return idx


def While(idx):
    CheckToken(idx, 'while')
    idx += 1
    CheckToken(idx, '(')
    idx += 1
    idx = Exp(idx)
    CheckToken(idx, ')')
    idx += 1
    idx = Block(idx)
    return idx


def Return(idx):
    CheckToken(idx, 'return')
    idx = Exp(idx)
    return idx


def Enumeration(idx):
    idx = Exp(idx)
    while idx != len(tokens) and idx == ',':
        idx += 1
        idx = Exp(idx)
    return idx


def Exp(idx):
    # TODO
    return idx





if __name__ == "__main__":
    Program(0)


