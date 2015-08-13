__author__ = 'tjr22'

import NEFreader

file_name='/Users/tjr22/Documents/NEF/NEF/specification/Commented_Example.nef'

tokenizer = NEFreader.tokenizer()

with open(file_name, 'r') as f:
    nef_file = f.read()
    tokenizer.tokenize(nef_file)