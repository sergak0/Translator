import string


class Token:
    def __init__(self, text, type):
        self.text = text
        self.type = type

    def __str__(self):
        return self.text + " - " + self.type

    def __eq__(self, other):
        return self.text == other


class Node:
    def __init__(self, node_type="no_type"):
        self.go = [None for i in range(256)]
        self.type = node_type


class FSM:
    def __init__(self, special_tokens):
        lines = open('FSMEdges', 'r').readlines()
        self.special_tokens = special_tokens
        self.states = int(lines[0])
        self.nodes = []
        for state in lines[1].split(' '):
            self.nodes.append(Node(state))
        self.posible_symbols = set(lines[2])
        for edges in lines[3:]:
            v, u, symbols = int(edges[0]), int(edges[2]), edges[11:-8]
            for symbol in symbols:
                self.nodes[v].go[ord(symbol)] = u

    def process(self, text):
        tokens = []
        current_id = 0
        current_token = ''
        idx = 0
        while idx < len(text):
            symbol = text[idx]
            if symbol not in self.posible_symbols:
                raise Exception("Unknown symbol met")
            edge_id = ord(symbol)
            if self.nodes[current_id].go[edge_id] is None:
                if self.nodes[current_id].type == 'error':
                    raise Exception("Syntax error")
                if self.nodes[current_id].type == 'special_symbol' and current_token not in self.special_tokens:
                    raise Exception("Syntax error")
                if current_token in self.special_tokens:
                    tokens.append(Token(current_token, self.special_tokens[current_token]))
                elif self.nodes[current_id].type != 'space':
                    tokens.append(Token(current_token, self.nodes[current_id].type))
                current_token = ''
                current_id = 0
            else:
                current_id = self.nodes[current_id].go[edge_id]
                current_token += symbol
                idx += 1
        return tokens


# read file
text = open('examples/text.txt', 'r').readlines()
text = ' '.join(text)
text = [i for i in text if i != '\n']

special_tokens_inversed = {
    'operator': ['++', '+', '-', '=', '-', '<', '>'],
    'reserved': ['for', 'while', 'if', 'int'],
    '[]': ['[', ']'],
    '()': ['(', ')']
}

special_tokens = {}
for key, values in special_tokens_inversed.items():
    for value in values:
        special_tokens[value] = key

fsm = FSM(special_tokens)
[print(i) for i in fsm.process(text)]

