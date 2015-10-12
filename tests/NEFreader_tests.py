from __future__ import absolute_import, print_function, unicode_literals
__author__ = 'TJ Ragan'

import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import NEFreader
from collections import OrderedDict


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
                                       ['nef_related_entries']
                                       [0]['database_name'], 'BMRB')

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
                                       ['nef_related_entries']
                                       [0]['database_name'], 'BMRB')

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script']
                                       [0]['program_name'], 'CYANA')


    def test_parse_loop_without_stop(self):
        tokens = ['data_nef_my_nmr_project']
        tokens.append('save_nef_nmr_meta_data')
        tokens.append('loop_')
        tokens.append('_nef_related_entries.database_name')
        tokens.append('BMRB')
        tokens.append('save_')

        self.p.parse(tokens)


        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_related_entries']
                                       [0]['database_name'], 'BMRB')


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
                                       ['nef_related_entries']
                                       [0]['database_name'], 'BMRB')


        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script']
                                       [0]['program_name'], 'CYANA')

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
                                       ['nef_related_entries']
                                       [0]['database_name'], 'BMRB')

        self.assertEquals(self.p.target['nef_nmr_meta_data']
                                       ['nef_program_script']
                                       [0]['program_name'], 'CYANA')


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
        tokens.append('_nef_related_entrys.database_accession_code')
        tokens.append('BMRB')
        tokens.append('12345')
        tokens.append('stop_')
        tokens.append('save_')

        self.assertRaises(Exception, self.p.parse, tokens)

    def test_parse_loops_mismatched_column_names_non_strict(self):
        with patch('NEFreader.parser.logger') as l:
            tokens = ['data_nef_my_nmr_project']
            tokens.append('save_nef_nmr_meta_data')
            tokens.append('loop_')
            tokens.append('_nef_related_entries.database_name')
            tokens.append('_nef_related_entrys.database_accession_code')
            tokens.append('BMRB')
            tokens.append('12345')
            tokens.append('stop_')
            tokens.append('save_')

            self.p.strict = False
            self.p.parse(tokens)

            self.assertTrue(l.warning.called)
            self.assertEquals(self.p.target['nef_nmr_meta_data']['nef_related_entries']
                                           [0]['database_name'], 'BMRB')
            self.assertEquals(self.p.target['nef_nmr_meta_data']['nef_related_entries']
                                           [0]['database_accession_code'], '12345')

class Test_bare_nef(unittest.TestCase):

    def setUp(self):
        self.nef = NEFreader.Nef()


    def test_bare_nef_data_block(self):
        self.assertEqual(self.nef.datablock, 'DEFAULT')

    def test_bare_nef_metadata_structure(self):
        metadata = self.nef['nef_nmr_meta_data']
        self.assertIn('sf_category', metadata)
        self.assertIn('sf_framecode', metadata)
        self.assertEqual(metadata['sf_category'], metadata['sf_framecode'])
        self.assertIn('format_name', metadata)
        self.assertIn('format_version', metadata)
        self.assertIn('program_name', metadata)
        self.assertIn('program_version', metadata)
        self.assertIn('creation_date', metadata)
        self.assertIn('uuid', metadata)

    def test_bare_nef_molecular_system_structure(self):
        molecularSystem = self.nef['nef_molecular_system']
        self.assertIn('sf_category', molecularSystem)
        self.assertIn('sf_framecode', molecularSystem)
        self.assertEqual(molecularSystem['sf_category'], molecularSystem['sf_framecode'])

    def test_bare_nef_molecular_system_structure(self):
        chemicalShiftList = self.nef['nef_chemical_shift_list_1']
        self.assertIn('sf_category', chemicalShiftList)
        self.assertIn('sf_framecode', chemicalShiftList)
        self.assertEqual(chemicalShiftList['sf_category']+'_1',
                         chemicalShiftList['sf_framecode'])


class Test_nef_validators(unittest.TestCase):

    def setUp(self):
        self.nef = NEFreader.Nef()
        self.v = NEFreader.Validator(self.nef)


    def test_full_validation(self):
        self.assertFalse(self.v.isValid())

        nef_sequence_item = {'chain_code': 'A',
                             'sequence_code': '1',
                             'residue_type': 'ALA',
                             'linking': '.',
                             'residue_variant': '.'}
        self.nef['nef_molecular_system']['nef_sequence'].append(nef_sequence_item)

        self.assertTrue(self.v.isValid())


    def test_missing_mandatory_datablock_label(self):
        self.assertIsNone(self.v._validate_datablock()['DATABLOCK'])

        del(self.nef.datablock)

        self.assertIsNotNone(self.v._validate_datablock()['DATABLOCK'])


    def test_missing_mandatory_saveframes(self):
        self.assertEqual(self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'], [])

        del(self.nef['nef_nmr_meta_data'])
        del(self.nef['nef_molecular_system'])
        del(self.nef['nef_chemical_shift_list_1'])

        self.assertIn('No nef_nmr_meta_data saveframe',
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])
        self.assertIn('No nef_molecular_system saveframe',
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])
        self.assertIn('No nef_chemical_shift_list saveframe(s)',
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])


    def test_missing_mandatory_metadata(self):
        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

        del(self.nef['nef_nmr_meta_data']['sf_category'])
        del(self.nef['nef_nmr_meta_data']['sf_framecode'])
        del(self.nef['nef_nmr_meta_data']['format_name'])
        del(self.nef['nef_nmr_meta_data']['format_version'])
        del(self.nef['nef_nmr_meta_data']['program_name'])
        del(self.nef['nef_nmr_meta_data']['program_version'])
        del(self.nef['nef_nmr_meta_data']['creation_date'])
        del(self.nef['nef_nmr_meta_data']['uuid'])

        self.assertIn('No sf_category', self.v._validate_metadata()['METADATA'])
        self.assertIn('No sf_framecode', self.v._validate_metadata()['METADATA'])
        self.assertIn('No format_name', self.v._validate_metadata()['METADATA'])
        self.assertIn('No format_version', self.v._validate_metadata()['METADATA'])
        self.assertIn('No program_name', self.v._validate_metadata()['METADATA'])
        self.assertIn('No program_version', self.v._validate_metadata()['METADATA'])
        self.assertIn('No creation_date', self.v._validate_metadata()['METADATA'])
        self.assertIn('No uuid', self.v._validate_metadata()['METADATA'])


    def test_allowed_fields_in_metadata(self):
        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

        self.nef['nef_nmr_meta_data']['test'] = None

        self.assertIn('"test" field not allowed',
                      self.v._validate_metadata()['METADATA'])


    def test_optional_related_database_entries_loop_in_metadata(self):
        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

        self.nef['nef_nmr_meta_data']['nef_related_entries'] = [{'test': 'invalid'}]

        self.assertIn('nef_nmr_meta_data:related_entries entry 1: no database_name',
                      self.v._validate_metadata()['METADATA'])
        self.assertIn('nef_nmr_meta_data:related_entries entry 1: no database_accession_code',
                      self.v._validate_metadata()['METADATA'])
        self.assertIn('nef_nmr_meta_data:related_entries entry 1: "test" field not allowed.',
                      self.v._validate_metadata()['METADATA'])


    def test_optional_program_script_loop_in_metadata(self):
        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

        self.nef['nef_nmr_meta_data']['nef_program_script'] = [{'test': 'invalid'}]

        self.assertIn('nef_nmr_meta_data:program_script entry 1: no program_name',
                      self.v._validate_metadata()['METADATA'])


    def test_optional_run_history_loop_in_metadata(self):
        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

        self.nef['nef_nmr_meta_data']['nef_program_script'] = [{'test': 'invalid'}]

        self.assertIn('nef_nmr_meta_data:program_script entry 1: no program_name',
                      self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_nef_molecular_system(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['empty nef_sequence'])

        del(self.nef['nef_molecular_system']['sf_category'])
        del(self.nef['nef_molecular_system']['sf_framecode'])
        del(self.nef['nef_molecular_system']['nef_sequence'])

        self.assertIn('No sf_category', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('No sf_framecode', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('No nef_sequence loop', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])


    def test_missing_mandatory_nef_sequence_columns(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['empty nef_sequence'])

        seq = self.nef['nef_molecular_system']['nef_sequence']
        seq.append({})

        self.assertIn('nef_seqence entry 1: missing chain_code',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_seqence entry 1: missing sequence_code',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_seqence entry 1: missing residue_type',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_seqence entry 1: missing linking',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_seqence entry 1: missing residue_variant',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])


    def test_mandatory_nef_sequence_in_molecular_system(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['empty nef_sequence'])
        nef_sequence_item = {'chain_code': 'A',
                             'sequence_code': '1',
                             'residue_type': 'ALA',
                             'linking': '.',
                             'residue_variant': '.'}
        self.nef['nef_molecular_system']['nef_sequence'].append(nef_sequence_item)

        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],[])


    def test_optional_cross_links_loop_in_molecular_system(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['empty nef_sequence'])
        nef_sequence_item_1 = {'chain_code': 'A',
                               'sequence_code': '1',
                               'residue_type': 'ALA',
                               'linking': '.',
                               'residue_variant': '.'}
        self.nef['nef_molecular_system']['nef_sequence'].append(nef_sequence_item_1)
        nef_sequence_item_2 = {'chain_code': 'B',
                               'sequence_code': '2',
                               'residue_type': 'CYS',
                               'linking': '.',
                               'residue_variant': '.'}
        self.nef['nef_molecular_system']['nef_sequence'].append(nef_sequence_item_2)

        self.nef['nef_molecular_system']['nef_covalent_links'] = [{},]
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no chain_code_1',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no sequence_code_1',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no residue_type_1',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no atom_name_1',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no chain_code_2',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no sequence_code_2',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no residue_type_2',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: no atom_name_2',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])

        nef_covalent_link = {'chain_code_1': 'A',
                             'sequence_code_1': '1',
                             'residue_type_1': 'ALA',
                             'atom_name_1': 'N',
                             'chain_code_2': 'B',
                             'sequence_code_2': '2',
                             'residue_type_2': 'CYS',
                             'atom_name_2': 'SD',
                             }
        self.nef['nef_molecular_system']['nef_covalent_links'] = [nef_covalent_link,]

        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],[])



    def test_missing_mandatory_chemical_shift_list(self):
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        sfc = self.nef['nef_chemical_shift_list_1']['sf_category']
        del(self.nef['nef_chemical_shift_list_1']['sf_category'])
        self.assertIn('No nef_chemical_shift_list saveframe(s)',
            self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])
        self.nef['nef_chemical_shift_list_1']['sf_category'] = sfc

        del(self.nef['nef_chemical_shift_list_1']['sf_framecode'])
        del(self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'])

        self.assertIn('nef_chemical_shift_list_1: No sf_framecode',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1: No nef_chemical_shift loop',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])


    def test_missing_mandatory_nef_chemical_shift_list(self):
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        sl = self.nef['nef_chemical_shift_list_1']['nef_chemical_shift']
        sl.append({})

        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift_list entry 1: missing chain_code',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift_list entry 1: missing sequence_code',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift_list entry 1: missing residue_type',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift_list entry 1: missing atom_name',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift_list entry 1: missing value',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])


    def test_full_nef_chemical_shift_in_chemical_shift_list(self):
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])
        nef_shift_item = {'chain_code': 'A',
                          'sequence_code': '1',
                          'residue_type': 'ALA',
                          'atom_name': 'HA',
                          'value': '5.0'}
        sl = self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'] = [nef_shift_item]

        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        sl[0]['value_uncertainty'] = '0.2'
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        sl[0]['test'] = '0.2'
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'],
                         ['nef_molecular_system:nef_covalent_links entry 1: "test" field not allowed.'])

    def test_missing_mandatory_saveframe_fields(self):
        self.assertEqual(self.v._validate_saveframe_fields()['SAVEFRAMES'], [])

        self.nef['generic_saveframe'] = {'sf_framecode': 'generic_saveframe',
                                         'sf_category': 'generic'}
        g = self.nef['generic_saveframe']
        self.assertEqual(self.v._validate_saveframe_fields()['SAVEFRAMES'], [])

        del g['sf_framecode']
        self.assertIn('No sf_framecode in generic_saveframe',
                      self.v._validate_saveframe_fields()['SAVEFRAMES'])

        del g['sf_category']
        self.assertIn('No sf_category in "generic_saveframe"',
                      self.v._validate_saveframe_fields()['SAVEFRAMES'])


    def test_inconsistent_saveframe_names(self):
        self.assertEqual(self.v._validate_saveframe_fields()['SAVEFRAMES'], [])

        self.nef['generic_saveframe'] = {'sf_framecode': 'generic'}

        self.assertIn('sf_framecode "generic" does not match framecode name "generic_saveframe".',
                      self.v._validate_saveframe_fields()['SAVEFRAMES'])


class Test_files(unittest.TestCase):

    def setUp(self):
        self.d = OrderedDict()
        self.t = NEFreader.Tokenizer()
        self.p = NEFreader.Parser(target=self.d)

    def test_annotated(self):
        f_name = 'tests/test_files/Commented_Example.nef'


        with open(f_name, 'r') as f:
            nef = f.read()

        tokens = self.t.tokenize(nef)
        self.p.parse(tokens)





if __name__ == '__main__':
    unittest.main()