
def tokenize(text: str, unique=False):
    tokens = set() if unique else list()
    for line in text.splitlines():
        i = 0
        while i < len(line):
            j = 1
            token = line[i : i + j]
            if not token.isalnum():
                i += 1
                continue
            while line[i : i + j + 1].isalnum() and i + j < len(line):
                j += 1
                token = line[i : i + j]
            token = token.lower()
            if token not in stopwords:
                if unique:
                    tokens.add(token)
                else:
                    tokens.append(token)
            i = i + j
    return tokens

def computeWordFrequencies(tokens):
    freqs = dict()
    for i in range(len(tokens)):
        if tokens[i] in freqs:
            continue
        freqs[tokens[i]] = 1
        for j in range(i + 1, len(tokens)):
            if tokens[j] == tokens[i]:
                freqs[tokens[i]] += 1
    return freqs