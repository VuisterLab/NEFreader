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


    def _test_full_validation(self):
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


    def test_missing_mandatory_saveframe__nef_nmr_meta_data(self):
        del(self.nef['nef_nmr_meta_data'])

        self.assertEqual(['Missing nef_nmr_meta_data label.'],
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])

    def test_missing_mandatory_saveframe__nef_molecular_system(self):
        del(self.nef['nef_molecular_system'])

        self.assertEqual(['Missing nef_molecular_system label.'],
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])

    def test_missing_mandatory_saveframe__nef_chemical_shift_list(self):
        del(self.nef['nef_chemical_shift_list_1'])

        self.assertEqual(['No saveframes with sf_category: nef_chemical_shift_list.'],
                      self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])



    # def test_inconsistent_saveframe_names(self):
    #     self.assertEqual(self.v._validate_saveframe_fields()['SAVEFRAMES'], [])
    #
    #     self.nef['generic_saveframe'] = {'sf_framecode': 'generic'}
    #
    #     self.assertIn('sf_framecode "generic" does not match framecode name "generic_saveframe"',
    #                   self.v._validate_saveframe_fields()['SAVEFRAMES'])



    def test_all_saveframes_have_mandatory_fields(self):
        self.nef['generic_saveframe'] = {'sf_framecode': 'generic_saveframe',
                                         'sf_category': 'generic'}

        self.assertEqual(self.v._validate_saveframe_fields()['SAVEFRAMES'], [])

    def test_all_saveframes_have_mandatory_fields__framecode_missing(self):
        self.nef['generic_saveframe'] = {'sf_category': 'generic'}

        self.assertEqual(['generic_saveframe: missing sf_framecode label.'],
                      self.v._validate_saveframe_fields()['SAVEFRAMES'])

    def test_all_saveframes_have_mandatory_fields__category_missing(self):
        self.nef['generic_saveframe'] = {'sf_framecode': 'generic_saveframe'}

        self.assertEqual(['generic_saveframe: missing sf_category label.'],
                      self.v._validate_saveframe_fields()['SAVEFRAMES'])


    def test_missing_mandatory_metadata__sf_framecode(self):
        del(self.nef['nef_nmr_meta_data'])

        self.assertEqual('No nef_nmr_meta_data saveframe.',
                         self.v._validate_metadata()['METADATA'])

    def test_mismatch_metadata__sf_framecode(self):
        self.nef['nef_nmr_meta_data']['sf_framecode'] = 'meta'

        self.assertEqual(['sf_framecode meta must match key nef_nmr_meta_data.'],
                         self.v._validate_metadata()['METADATA'])
        self.assertEqual(['sf_framecode meta must match key nef_nmr_meta_data.'],
                         self.v._validate_saveframe_fields()['SAVEFRAMES'])

    def test_missing_mandatory_metadata__sf_category(self):
        del(self.nef['nef_nmr_meta_data']['sf_category'])

        self.assertEqual(['Missing sf_category label.'],
                         self.v._validate_metadata()['METADATA'])

    def test_mismatch_metadata__sf_category(self):
        self.nef['nef_nmr_meta_data']['sf_category'] = 'category'

        self.assertEqual(['sf_category category must be nef_nmr_meta_data.'],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__format_name(self):
        del(self.nef['nef_nmr_meta_data']['format_name'])

        self.assertEqual(['Missing format_name label.'],
                         self.v._validate_metadata()['METADATA'])

    def test_mismatch_metadata__format_name(self):
        self.nef['nef_nmr_meta_data']['format_name'] = 'format'

        self.assertEqual(["format_name must be 'Nmr_Exchange_Format'."],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__format_version(self):
        del(self.nef['nef_nmr_meta_data']['format_version'])

        self.assertEqual(['Missing format_version label.'],
                         self.v._validate_metadata()['METADATA'])

    def test_mismatch_metadata__format_version(self):
        self.nef['nef_nmr_meta_data']['format_version'] = '999'

        self.assertEqual(["This reader does not support format version 999."],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__program_name(self):
        del(self.nef['nef_nmr_meta_data']['program_name'])

        self.assertEqual(['Missing program_name label.'],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__program_version(self):
        del(self.nef['nef_nmr_meta_data']['program_version'])

        self.assertEqual(['Missing program_version label.'],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__creation_date(self):
        del(self.nef['nef_nmr_meta_data']['creation_date'])

        self.assertEqual(['Missing creation_date label.'],
                         self.v._validate_metadata()['METADATA'])


    def test_missing_mandatory_metadata__uuid(self):
        del(self.nef['nef_nmr_meta_data']['uuid'])

        self.assertEqual(['Missing uuid label.'],
                         self.v._validate_metadata()['METADATA'])


    # def test_allowed_fields_in_metadata(self):
    #     self.nef['nef_nmr_meta_data']['coordinate_file_name'] = ''
    #     self.nef['nef_nmr_meta_data']['nef_related_entries'] = []
    #     self.nef['nef_nmr_meta_data']['nef_program_script'] = []
    #     self.nef['nef_nmr_meta_data']['nef_run_history'] = []
    #
    #     self.assertEqual([], self.v._validate_metadata()['METADATA'])

    def test_nonallowed_fields_in_metadata(self):
        self.nef['nef_nmr_meta_data']['test'] = ''

        self.assertEqual(["Field 'test' not allowed in nef_nmr_meta_data."],
                         self.v._validate_metadata()['METADATA'])


    def test_optional_coordinate_file_name_field_in_metadata(self):
        self.nef['nef_nmr_meta_data']['coordinate_file_name'] = ''
        self.assertEqual([], self.v._validate_metadata()['METADATA'])


    def test_optional_nef_related_entries_loop_in_metadata_missing_fields(self):
        self.nef['nef_nmr_meta_data']['nef_related_entries'] = [OrderedDict()]

        self.assertEqual(2, len(self.v._validate_metadata()['METADATA']))
        self.assertIn('nef_nmr_meta_data:nef_related_entries entry 1: missing database_name label.',
                         self.v._validate_metadata()['METADATA'])
        self.assertIn('nef_nmr_meta_data:nef_related_entries entry 1: missing database_accession_code label.',
                         self.v._validate_metadata()['METADATA'])

    def test_optional_nef_related_entries_loop_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_related_entries'] = [{'database_name':'test',
                                                                'database_accession_code':'1'},]

        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

    def test_optional_nef_related_entries_loop_nonallowed_field_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_related_entries'] = [{'database_name':'test',
                                                                'database_accession_code':'1',
                                                                'test':'test'}]

        self.assertEqual(["Field 'test' not allowed in nef_nmr_meta_data:nef_related_entries entry 1."],
                         self.v._validate_metadata()['METADATA'])


    def test_optional_nef_program_script_loop_in_metadata_missing_fields(self):
        self.nef['nef_nmr_meta_data']['nef_program_script'] = [OrderedDict()]

        self.assertEqual(['nef_nmr_meta_data:nef_program_script entry 1: missing program_name label.'],
                         self.v._validate_metadata()['METADATA'])

    def test_optional_nef_program_script_loop_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_program_script'] = [{'program_name':'test'},]

        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

    def test_optional_nef_program_script_loop_inconsistent_keys_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_program_script'] = [{'program_name':'test'},
                                                            {'program_name':'test',
                                                             'script_name':'test.script'}
                                                             ]

        self.assertEqual(['nef_nmr_meta_data:nef_program_script entry 1: missing script_name label.'],
                         self.v._validate_metadata()['METADATA'])


    def _test_optional_nef_run_history_loop_in_metadata_missing_fields(self):
        self.nef['nef_nmr_meta_data']['nef_run_history'] = [OrderedDict()]

        self.assertEqual(2, len(self.v._validate_metadata()['METADATA']))
        self.assertIn('nef_nmr_meta_data:nef_run_history entry 1: missing run_ordinal label.',
                         self.v._validate_metadata()['METADATA'])
        self.assertIn('nef_nmr_meta_data:nef_run_history entry 1: missing program_name label.',
                         self.v._validate_metadata()['METADATA'])

    def test_optional_nef_run_history_loop_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_run_history'] = [{'run_ordinal':'1',
                                                             'program_name':'test',
                                                             'program_version':'1',
                                                             'script_name':'test.script',
                                                             'script':"""do stuff"""}]

        self.assertEqual(self.v._validate_metadata()['METADATA'], [])

    def test_optional_nef_run_history_loop_nonallowed_field_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_run_history'] = [{'run_ordinal':'1',
                                                             'program_name':'test',
                                                             'test':'test'}]

        self.assertEqual(["Field 'test' not allowed in nef_nmr_meta_data:nef_run_history entry 1."],
                         self.v._validate_metadata()['METADATA'])

    def test_optional_nef_run_history_loop_inconsistent_keys_in_metadata(self):
        self.nef['nef_nmr_meta_data']['nef_run_history'] = [{'run_ordinal':'1',
                                                             'program_name':'test'},
                                                            {'run_ordinal':'2',
                                                             'program_name':'test',
                                                             'program_version':'1'}
                                                             ]

        self.assertEqual(['nef_nmr_meta_data:nef_run_history entry 1: missing program_version label.'],
                         self.v._validate_metadata()['METADATA'])



    def test_missing_mandatory_nef_molecular_system_category_label(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['Empty nef_sequence.'])

        del(self.nef['nef_molecular_system']['sf_category'])

        self.assertIn('Missing sf_category label.', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])

    def test_missing_mandatory_nef_molecular_system_framecode(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['Empty nef_sequence.'])

        del(self.nef['nef_molecular_system']['sf_framecode'])

        self.assertIn('Missing sf_framecode label.', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])

    def test_missing_mandatory_nef_molecular_system_nef_sequence(self):
        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],
                         ['Empty nef_sequence.'])

        del(self.nef['nef_molecular_system']['nef_sequence'])

        self.assertIn('Missing nef_sequence label.', self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])


    def test_missing_mandatory_nef_sequence_columns(self):
        seq = self.nef['nef_molecular_system']['nef_sequence']
        seq.append({})

        self.assertIn('nef_molecular_system:nef_sequence entry 1: missing chain_code label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_sequence entry 1: missing sequence_code label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_sequence entry 1: missing residue_type label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_sequence entry 1: missing linking label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_sequence entry 1: missing residue_variant label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])


    def test_mandatory_nef_sequence_in_molecular_system(self):
        nef_sequence_item = {'chain_code': 'A',
                             'sequence_code': '1',
                             'residue_type': 'ALA',
                             'linking': '.',
                             'residue_variant': '.'}
        self.nef['nef_molecular_system']['nef_sequence'].append(nef_sequence_item)

        self.assertEqual(self.v._validate_molecular_system()['MOLECULAR_SYSTEM'],[])


    def test_optional_cross_links_loop_in_molecular_system(self):
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

        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing chain_code_1 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing sequence_code_1 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing residue_type_1 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing atom_name_1 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing chain_code_2 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing sequence_code_2 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing residue_type_2 label.',
                      self.v._validate_molecular_system()['MOLECULAR_SYSTEM'])
        self.assertIn('nef_molecular_system:nef_covalent_links entry 1: missing atom_name_2 label.',
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



    def test_missing_mandatory_chemical_shift_lists(self):
        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        del(self.nef['nef_chemical_shift_list_1']['sf_category'])

        self.assertEqual(['No saveframes with sf_category: nef_chemical_shift_list.'],
            self.v._validate_required_saveframes()['REQUIRED_SAVEFRAMES'])
        self.assertEqual(['No nef_chemical_shift_list saveframes found.'],
            self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])


    def test_missing_mandatory_chemical_shift_loop_in_chemical_shift_lists_list(self):
        del(self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'])

        self.assertEqual(['nef_chemical_shift_list_1: missing nef_chemical_shift label.'],
            self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])

    def test_missing_mandatory_chemical_shift_loop_fields(self):
        self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'] = [{}]

        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing chain_code label.',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing sequence_code label.',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing residue_type label.',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing atom_name label.',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])
        self.assertIn('nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing value label.',
                      self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'])

    def test_mandatory_chemical_shift_loop_fields(self):
        nef_shift_item = {'chain_code': 'A',
                            'sequence_code': '1',
                            'residue_type': 'ALA',
                            'atom_name': 'HA',
                            'value': '5.0'}
        sl = self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'] = [nef_shift_item,]

        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])

        sl[0]['value_uncertainty'] = '0.2'

        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'], [])



    def test_mismatched_mandatory_chemical_shift_loop_fields(self):
        nef_shift_item_1 = {'chain_code': 'A',
                            'sequence_code': '1',
                            'residue_type': 'ALA',
                            'atom_name': 'HA',
                            'value': '5.0'}
        nef_shift_item_2 = {'chain_code': 'A',
                            'sequence_code': '1',
                            'residue_type': 'ALA',
                            'atom_name': 'N',
                            'value': '120',
                            'value_uncertainty': '0.2'}
        self.nef['nef_chemical_shift_list_1']['nef_chemical_shift'] = [nef_shift_item_1,
                                                                       nef_shift_item_2]

        self.assertEqual(self.v._validate_chemical_shift_lists()['CHEMICAL_SHIFT_LISTS'],
                         ['nef_chemical_shift_list_1:nef_chemical_shift entry 1: missing value_uncertainty label.'])


    #
    # def test_mandatory_nef_distance_restraint_list(self):
    #     self.assertEqual(self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'], [])
    #
    #     drl = self.nef['nef_distance_restraint_list_1'] = OrderedDict()
    #     drl['sf_category'] = 'nef_distance_restraint_list'
    #
    #     self.assertEqual(self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'],
    #                      ['nef_distance_restraint_list_1: missing sf_framecode',
    #                       'nef_distance_restraint_list_1: missing potential_type',
    #                       'nef_distance_restraint_list_1: missing nef_distance_restraint loop'])
    #
    #     drl['sf_framecode'] = 'nef_distance_restraint_list_1a'
    #     drl['potential_type'] = 'square-well-parabolic-linear'
    #     drl['nef_distance_restraint'] = []
    #     self.assertEqual(self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'],
    #                      ['nef_distance_restraint_list_1: Mismatched key and sf_framecode'])
    #
    #     drl['sf_framecode'] = 'nef_distance_restraint_list_1'
    #     self.assertEqual(self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'], [])
    #
    #     dr = drl['nef_distance_restraint']
    #     distance_restraint_1 = {'ordinal': '1',
    #                            'restraint_id': '1',
    #                            'chain_code_1': 'A',
    #                            'sequence_code_1': '21',
    #                            'residue_type_1': 'ALA',
    #                            'atom_name_1': 'HB%',
    #                            'chain_code_2': 'A',
    #                            'sequence_code_2': '17',
    #                            'residue_type_2': 'VAL',
    #                            'atom_name_2': 'H',
    #                            'weight': '1.00'}
    #     distance_restraint_2 = {'ordinal': '2',
    #                            'restraint_id': '1',
    #                            'chain_code_1': 'A',
    #                            'sequence_code_1': '21',
    #                            'residue_type_1': 'ALA',
    #                            'atom_name_1': 'HB%',
    #                            'chain_code_2': 'A',
    #                            'sequence_code_2': '18',
    #                            'residue_type_2': 'VAL',
    #                            'atom_name_2': 'H',
    #                            'weight': '1.00'}
    #     dr.append(distance_restraint_1)
    #     dr.append(distance_restraint_2)
    #
    #     self.assertEqual(self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'], [])
    #
    #     distance_restraint_3 = {'ordinal': '3',
    #                            'restraint_id': '1',
    #                            'chain_code_1': 'A',
    #                            'sequence_code_1': '21',
    #                            'residue_type_1': 'ALA',
    #                            'atom_name_1': 'HB%',
    #                            'chain_code_2': 'A',
    #                            'sequence_code_2': '18',
    #                            'residue_type_2': 'VAL',
    #                            'atom_name_2': 'H',
    #                            'weight': '1.00',
    #                            'restraint_combination_id': '.',
    #                            'target_value': '.',
    #                            'target_value_uncertainty': '.',
    #                            'lower_linear_limit': '.',
    #                            'lower_limit': '.',
    #                            'upper_limit': '.',
    #                            'upper_linear_limit': '.'}
    #     dr.append(distance_restraint_3)
    #
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing restraint_combination_id',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing target_value',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing target_value_uncertainty',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing lower_linear_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing lower_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing upper_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 1: missing upper_linear_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing restraint_combination_id',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing target_value',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing target_value_uncertainty',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing lower_linear_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing lower_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing upper_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])
    #     self.assertIn('nef_distance_restraint_list_1:nef_chemical_shift entry 2: missing upper_linear_limit',
    #                   self.v._validate_distance_restraint_lists()['DISTANCE_RESTRAINT_LISTS'])


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