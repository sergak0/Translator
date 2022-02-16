


if __name__ == '__main__':
    text = open('test_code.txt').readlines()

    for line in text:
        splitted = line.split()
        if splitted[0] == 'def':
            parse_func(''.join(splitted[1:]))
