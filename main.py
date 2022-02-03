import re


def parse_func(s):
    name = s[:s.find('(')]
    if s.find('(') == -1 or s.find(')') == -1:
        print('Error, there is an error in brace')

    variables = s[s.find('(') + 1:s.rfind(')')].split(',')
    if s[-1] != '{':
        print('Error, there is no {')
    return name, variables


if __name__ == '__main__':
    text = open('test_code.txt').readlines()

    for line in text:
        splitted = line.split()
        if splitted[0] == 'def':
            parse_func(''.join(splitted[1:]))
