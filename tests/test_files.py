from __future__ import absolute_import, print_function, unicode_literals
__author__ = 'TJ Ragan'

import unittest
from collections import OrderedDict

import NEFreader


class Test_files(unittest.TestCase):

    def setUp(self):
        self.d = OrderedDict()
        self.t = NEFreader.Lexer()
        self.p = NEFreader.Parser(target=self.d)

    def test_annotated(self):
        f_name = 'tests/test_files/Commented_Example.nef'


        with open(f_name, 'r') as f:
            nef = f.read()

        tokens = self.t.tokenize(nef)
        self.p.parse(tokens)



if __name__ == '__main__':
    unittest.main()