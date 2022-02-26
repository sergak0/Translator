from lexical import *
import ctypes


tokens = []


def Program(idx):
    if tokens[idx] == 'fn':  # <Func><Program> | <Func>
        idx = Func(idx)
        if idx != len(tokens):
            idx = Program(idx)
    else:  # <Definition><Program> | <Definition>
        idx = Definition(idx)
        if idx == len(tokens) and tokens[idx] != ';':
            raise Exception('Excepted ;')
        idx += 1
        if idx != len(tokens):
            idx = Program(idx)
    return idx


def Func(idx):
    return idx


def EType(idx):
    return idx


def Name(idx):
    return idx


def Params(idx):
    return idx


def Block(idx):
    return idx


def Operator(idx):
    return idx


def For(idx):
    return idx


def Definition(idx):
    return idx


def If(idx):
    return idx


def While(idx):
    return idx


def Return(idx):
    return idx


def Exp(idx):
    return idx


def Enumeration(idx):
    return idx




if __name__ == "__main__":
    Program(0)


