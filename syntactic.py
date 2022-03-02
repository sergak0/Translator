from lexical import *
import ctypes
import re

tokens = []  # List of lexical/Token

special_tokens_inversed = {
    'operator': ['++', '--', '-', '*', '/', '%', '+', '>', '<', '>=', '<=', '==', '!=', '&', '|', '%', '=', '^'],
    'punctuation': [';', ',', '{', '}'],
    'reserved': ['for', 'while', 'if', 'int', 'double', 'string', 'fn', 'return'],
    '[]': ['[', ']'],
    '()': ['(', ')']
}

special_tokens = {}


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
        raise Exception('Unexpected symbol')
    return idx


def Func(idx):
    CheckToken(idx, 'fn')
    idx += 1
    idx = Type(idx)
    idx = Name(idx)
    if idx == len(tokens) or tokens[idx] != '(':
        raise Exception('Expect (')
    idx += 1
    idx = Params(idx)
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
    if idx == len(tokens) or (tokens[idx] != 'int' and tokens[idx] != 'double' and tokens[idx] != 'string'):
        return idx
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
        if tokens[idx] == '}':
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
    while idx != len(tokens) and tokens[idx] == ',':
        idx += 1
        idx = Exp(idx)
    return idx


def Prior1(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    if tokens[idx] == '(':
        idx = Exp(idx + 1)
        CheckToken(idx, ')')
        return idx + 1
    idx = Name(idx)
    if idx != len(tokens) and tokens[idx] == '(':
        idx += 1
        if idx != len(tokens) and tokens[idx] == ')':
            return idx + 1
        else:
            idx = Enumeration(idx)
            CheckToken(idx, ')')
            return idx + 1

    while idx != len(tokens) and tokens[idx] == '[':
        idx = Exp(idx + 1)
        CheckToken(idx, ']')
        idx += 1
    return idx


def Prior2(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    if tokens[idx] == '--':
        idx += 1
        return Prior2(idx)
    if tokens[idx] == '++':
        idx += 1
        return Prior2(idx)
    if tokens[idx] == '-':
        idx += 1
        return Prior2(idx)
    if tokens[idx].type == 'string_const' or tokens[idx].type == 'numeric_const':
        return idx + 1
    return Prior1(idx)


def Prior3(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior2(idx)
    if tokens[idx] == '*':
        idx += 1
        return Prior3(idx)
    if tokens[idx] == '/':
        idx += 1
        return Prior3(idx)
    if tokens[idx] == '%':
        idx += 1
        return Prior3(idx)
    return idx


def Prior4(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior3(idx)
    if tokens[idx] == '+':
        idx += 1
        return Prior4(idx)
    if tokens[idx] == '-':
        idx += 1
        return Prior4(idx)
    return idx


def Prior5(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior4(idx)
    if tokens[idx] == '>':
        idx += 1
        return Prior5(idx)
    if tokens[idx] == '<':
        idx += 1
        return Prior5(idx)
    if tokens[idx] == '>=':
        idx += 1
        return Prior5(idx)
    if tokens[idx] == '<=':
        idx += 1
        return Prior5(idx)
    return idx


def Prior6(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior5(idx)
    if tokens[idx] == '==':
        idx += 1
        return Prior6(idx)
    if tokens[idx] == '!=':
        idx += 1
        return Prior6(idx)
    return idx


def Prior7(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior6(idx)
    if tokens[idx] == '&':
        idx += 1
        return Prior7(idx)
    if tokens[idx] == '|':
        idx += 1
        return Prior7(idx)
    if tokens[idx] == '^':
        idx += 1
        return Prior7(idx)
    return idx


def Prior8(idx):
    if idx == len(tokens):
        raise Exception('Expression fault')
    idx = Prior7(idx)
    if tokens[idx] == '=':
        idx += 1
        return Prior8(idx)
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



