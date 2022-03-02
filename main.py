if __name__ == '__main__':
    text = open('examples/test_code.txt').readlines()

    for line in text:
        splitted = line.split()
        if splitted[0] == 'def':
            pass
            #parse_func(''.join(splitted[1:]))
