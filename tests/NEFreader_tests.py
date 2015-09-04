from __future__ import absolute_import, print_function, unicode_literals
__author__ = 'TJ Ragan'

import unittest
import NEFreader
from collections import OrderedDict


class Test_Tokenizer_util_functions(unittest.TestCase):
 
    def setUp(self):
        self.t = NEFreader.Tokenizer()

    def test_uncommented_newline_reset_state(self):
        self.t._state = 'invalid state for testing only'
        self.t._token = ''
        self.t._uncommented_newline()
        self.assertEquals( self.t._state, 'start' )

    def test_uncommented_newline_empty_token(self):
        self.t._token = ''
        self.t._uncommented_newline()
        self.assertEquals( self.t.tokens, ['\n'] )

    def test_uncommented_newline_nonempty_token(self):
        self.t._state = 'in token'
        self.t._token = ['t','e','s','t']
        self.t._uncommented_newline()
        self.assertEquals( self.t.tokens, ['test','\n'] )


class Test_Tokenizer_tokenize(unittest.TestCase):

    def setUp(self):
        self.t = NEFreader.Tokenizer()

    def test_tokenizer_setup_with_chars(self):
        t = NEFreader.Tokenizer('test')
        self.assertEquals(t.chars, 'test')

    def test_tokenizer_tokenize_with_predefined_chars(self):
        t = NEFreader.Tokenizer('test')
        tokens = t.tokenize()
        self.assertEquals(tokens, ['test'])

    def test_tokenize_noncomment_without_newline(self):
        self.t.tokenize('5.324')
        self.assertEquals( self.t.tokens, ['5.324'] )

    def test_tokenize_noncomment2_without_newline(self):
        self.t.tokenize('light_blue')
        self.assertEquals( self.t.tokens, ['light_blue'] )

    def test_tokenize_noncomment_with_newline(self):
        self.t.tokenize('test\n')
        self.assertEquals( self.t.tokens, ['test','\n'] )


    def test_tokenize_quoted_string(self):
        self.t.tokenize("""'low melting point' """)
        self.assertEquals( self.t.tokens, ['low melting point'] )

    def test_tokenize_quoted_string_with_internal_quote(self):
        self.t.tokenize("""'classed as 'unknown' """)
        self.assertEquals( self.t.tokens, ["classed as 'unknown"] )

    def test_tokenize_quoted_string(self):
        self.t.tokenize("""'test string'\t""")
        self.assertEquals( self.t.tokens, ['test string'] )

    def test_tokenize_quoted_string(self):
        self.t.tokenize("""'test string'\n""")
        self.assertEquals( self.t.tokens, ['test string', '\n'] )


    def test_tokenize_double_quoted_string(self):
        self.t.tokenize('''"low melting point" ''')
        self.assertEquals( self.t.tokens, ['low melting point'] )

    def test_tokenize_double_quoted_string_with_internal_quote(self):
        self.t.tokenize('''"classed as 'unknown" ''')
        self.assertEquals( self.t.tokens, ["classed as 'unknown"] )

    def test_tokenize_double_quoted_string(self):
        self.t.tokenize('''"test string"\t''')
        self.assertEquals( self.t.tokens, ['test string'] )

    def test_tokenize_double_quoted_string(self):
        self.t.tokenize('''"test string"\n''')
        self.assertEquals( self.t.tokens, ['test string', '\n'] )


    def test_tokenize_semicolon_quoted_string(self):
        s = """;\nDepartment of Computer Science\nUniversity of Western Australia\n;"""
        t_s = """\nDepartment of Computer Science\nUniversity of Western Australia\n"""
        self.t.tokenize(s)
        self.assertEquals(self.t.tokens, [t_s] )

    def test_tokenize_semicolon_quoted_string2(self):
        s = """;Department of Computer Science\nUniversity of Western Australia\n;"""
        t_s = """Department of Computer Science\nUniversity of Western Australia\n"""
        self.t.tokenize(s)
        self.assertEquals(self.t.tokens, [t_s] )

    def test_tokenize_semicolon_quoted_string3(self):
        s = """;\nDepartment of Computer Science\nUniversity of Western Australia\n;test"""
        t_s = """\nDepartment of Computer Science\nUniversity of Western Australia\n"""
        self.t.tokenize(s)
        self.assertEquals(self.t.tokens, [t_s, 'test'] )

    def test_tokenize_string_with_semicolon(self):
        s = """Department of Computer Science;University of\nWestern Australia"""
        self.t.tokenize(s)
        self.assertEquals(self.t.tokens, ['Department', 'of', 'Computer', 'Science;University',
                                          'of', '\n', 'Western', 'Australia'] )

    def test_tokenize_general_string(self):
        self.t.tokenize('nef_nmr_meta_data')
        self.assertEquals( self.t.tokens, ['nef_nmr_meta_data'] )

    def test_tokenize_string_with_period(self):
        self.t.tokenize('_nef_nmr_meta_data.sf_category')
        self.assertEquals( self.t.tokens, ['_nef_nmr_meta_data.sf_category'] )

    def test_tokenize_string_with_leading_underscore(self):
        self.t.tokenize('_nef_nmr_meta_data.sf_category')
        self.assertEquals( self.t.tokens, ['_nef_nmr_meta_data.sf_category'] )


    def test_tokenize_bare_newline(self):
        self.t.tokenize('\n')
        self.assertEquals( self.t.tokens, ['\n'] )

    def test_tokenize_bare_newlines(self):
        self.t.tokenize('\n\n\n')
        self.assertEquals( self.t.tokens, ['\n']*3 )


    def test_tokenize_tab(self):
        self.t.tokenize('\t')
        self.assertEquals( self.t.tokens, [] )


    def test_tokenize_space(self):
        self.t.tokenize(' ')
        self.assertEquals( self.t.tokens, [] )


    def test_tokenize_comment_with_newline(self):
        self.t.tokenize('#=\n')
        self.assertEquals( self.t.tokens, ['#=','\n'] )

    def test_tokenize_comment_without_newline(self):
        self.t.tokenize('#=')
        self.assertEquals( self.t.tokens, ['#='] )


class Test_Parser_parse(unittest.TestCase):

    def setUp(self):
        self.d = OrderedDict()
        self.p = NEFreader.Parser(target=self.d)


    def test_parser_setup_without_target(self):
        p = NEFreader.Parser()
        self.assertEqual(type(p.target), OrderedDict)

    def test_parser_parse_with_predefined_tokens(self):
        p = NEFreader.Parser(tokens=['data_nef_my_nmr_project'])
        d = p.parse()
        self.assertEquals(d.datablock, 'data_nef_my_nmr_project')

    def test_parse_whitespace(self):
        self.p.parse(['\n'])
        self.assertEquals(self.d, dict())


    def test_parse_comments(self):
        self.p.parse(['#  Nmr Exchange Format\n'])
        self.assertEquals(self.d, dict())

    def test_parse_comments_with_key(self):
        self.p.parse(['# key: d'])
        self.assertEquals(self.p._loop_key, '# key: d')


    def test_parse_data_block_declaration(self):
        self.p.parse(['data_nef_my_nmr_project'])
        self.assertTrue(hasattr(self.d, 'datablock'))

    def test_parse_multiple_data_blocks(self):
        self.assertRaises(Exception, self.p.parse,
                          ['data_nef_my_nmr_project','data_nef_my_nmr_project_2'])

    def test_parse_without_data_block_declaration(self):
        self.assertRaises(Exception, self.p.parse, ['save_nef_nmr_meta_data'])


    def test_parse_saveframe(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertTrue('nef_nmr_meta_data' in self.p.target.keys())
        self.assertEquals(type(self.p.target['nef_nmr_meta_data']), OrderedDict)

    def test_parse_saveframes(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('save_')
        tokens.append('save_cyana_additional_data_1')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertTrue('nef_nmr_meta_data' in self.p.target.keys())
        self.assertEquals(type(self.p.target['nef_nmr_meta_data']), OrderedDict)
        self.assertTrue('cyana_additional_data_1' in self.p.target.keys())
        self.assertEquals(type(self.p.target['cyana_additional_data_1']), OrderedDict)


    def test_parse_nested_saveframes(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('save_cyana_additional_data_1')
        tokens.append('save_')
        tokens.append('save_')

        self.assertRaises(Exception, self.p.parse, tokens)

    def test_parse_unnamed_saveframes(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_')

        self.assertRaises(Exception, self.p.parse, tokens)

    def test_parse_loop(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')
        tokens.append('stop_')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][0], ['database_name'])

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][1]
                                       ['database_name'], 'BMRB')

    def test_parse_loops(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')
        tokens.append('stop_')
        tokens.append('loop_')
        tokens.append('_nef_program_script.program_name')
        tokens.append('CYANA')
        tokens.append('stop_')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][0], ['database_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][1]
                                       ['database_name'], 'BMRB')

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][0], ['program_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][1]
                                       ['program_name'], 'CYANA')


    def test_parse_loop_without_stop(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][0], ['database_name'])

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][1]
                                       ['database_name'], 'BMRB')


    def test_parse_loops_last_without_stop(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')
        tokens.append('stop_')
        tokens.append('loop_')
        tokens.append('_nef_program_script.program_name')
        tokens.append('CYANA')
        tokens.append('save_')

        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][0], ['database_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][1]
                                       ['database_name'], 'BMRB')

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][0], ['program_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][1]
                                       ['program_name'], 'CYANA')

    def test_parse_loops_without_stop(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')

        tokens.append('loop_')
        tokens.append('_nef_program_script.program_name')
        tokens.append('CYANA')
        tokens.append('save_')

        self.assertRaises(Exception, self.p.parse, tokens)

    def test_parse_loops_without_stop_non_strict(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')

        tokens.append('loop_')
        tokens.append('_nef_program_script.program_name')
        tokens.append('CYANA')
        tokens.append('save_')

        self.p.strict = False
        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][0], ['database_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries'][1]
                                       ['database_name'], 'BMRB')

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][0], ['program_name'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script'][1]
                                       ['program_name'], 'CYANA')


    def test_parse_close_loop_without_opening_loop_first(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('stop_')

        self.assertRaises(Exception, self.p.parse, tokens)


    def test_parse_loops_mismatched_column_names(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('_nef_related_entrie.database_accession_code')
        tokens.append('BMRB')
        tokens.append('12345')
        tokens.append('stop_')
        tokens.append('save_')

        self.assertRaises(Exception, self.p.parse, tokens)

    def _test_parse_loops_mismatched_column_names_non_strict(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('_nef_related_entrie.database_accession_code')
        tokens.append('BMRB')
        tokens.append('12345')
        tokens.append('stop_')
        tokens.append('save_')

        self.p.strict = False
        self.p.parse(tokens)

        self.assertEquals(self.p.target['nef_nmr_meta_data']['nef_related_entries'][0],
                                       ['database_name', 'database_accession_code'])
        self.assertEquals(self.p.target['nef_nmr_meta_data']['nef_related_entries'][1],
                                       ['BMRB', '12345'])


class Test_files(unittest.TestCase):

    def setUp(self):
        self.d = OrderedDict()
        self.t = NEFreader.Tokenizer()
        self.p = NEFreader.Parser(target=self.d)

    def _test_annotated(self):
        f_name = '/Users/tjr22/Documents/NEF/NEF/specification/Commented_Example.nef'

        with open(f_name, 'r') as f:
            nef = f.read()

        tokens = self.t.tokenize(nef)
        self.p.parse(tokens)

        print(self.d.keys())


class Test_nef(unittest.TestCase):

    def setUp(self):
        self.nef = NEFreader.Nef()


    def _test_bare_nef(self):

        print(self.nef.keys())


    def _test_read_annotated_file(self):
        f_name = 'test_files/Commented_Example.nef'

        self.nef.open(f_name, strict=False)
        print(self.nef)
        for k,v in self.nef.items():
            print(k)
            print(v)
            print()


if __name__ == '__main__':
    unittest.main()