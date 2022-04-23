import re

prior = {
    '++': 0,
    '--': 0,
    'u-': 0,
    '*': 1,
    '/': 1,
    '%': 1,
    '+': 2,
    '-': 2,
    '>': 3,
    '<': 3,
    '>=': 3,
    '<=': 3,
    '==': 4,
    '!=': 4,
    '&': 5,
    '|': 5,
    '^': 5,
}

brace_pair = {
    '(': ')',
    ')': '(',
    '[': ']',
    ']': '['
}


def find_end_of_expression(text):
    cnt_open = {'(': 0, '[': 0}
    for i, el in enumerate(text):
        if el == ';' or el == ',' or el == '{':
            if cnt_open['('] != 0 or cnt_open['['] != 0:
                raise 'brace balance is incorrect'
            return i
        if el == '(' or el == '[':
            cnt_open[el] += 1
        if el == ')' or el == ']':
            if cnt_open[brace_pair[el]] == 0:
                return i
            else:
                cnt_open[brace_pair[el]] -= 1

    return len(text)


def build_polis(text):
    st = []
    res = []
    text.append('#')
    for i, el in enumerate(text[:-1]):
        if re.fullmatch('[0-9]+', el):
            res.append(el)
        elif re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', el) or el in prior.keys() and prior[el] == 0:
            if text[i + 1] == '(':
                st.append(el + '#')
            elif text[i + 1] == '[':
                st.append(el + '$')
            elif el in prior.keys():
                st.append(el)
            else:
                res.append(el)
        elif el == '(' or el == '[':
            st.append(el)
        elif el == ')' or el == ']':
            while len(st) and st[-1] != brace_pair[el]:
                if st[-1] in brace_pair.keys():
                    raise Exception('brace does not match each other')

                res.append(st[-1])
                st.pop()
            st.pop()
        else:
            while len(st) and (st[-1][-1] in ['#', '$'] or st[-1] in prior.keys() and prior[st[-1]] <= prior[el]):
                res.append(st[-1])
                st.pop()

            st.append(el)

    st = st[::-1]
    res += st
    return res


if __name__ == '__main__':
    s = input()
    print(build_polis(s.split()))

#  5 * 6 + 3 - 4 + x / a [ ind ]
#  a * 3 / sin ( x ) + ( d / ( x + d ) )
# u- d + ++ f ( x ) * 9
