__author__ = 'tjr22'

from collections import OrderedDict
from .parser import Lexer, Parser

MAJOR_VERSION = '0'
MINOR_VERSION = '8'
__version__ = '.'.join((MAJOR_VERSION, MINOR_VERSION))

class Nef(OrderedDict):
    """
    An in-memory representation of the NEF format

    Notes:
    Saveframes are modeled as OrderedDict's
    Loops are modeled as a size 2 list of lists (potentially to become pandas saveframes).  The
    first list is a list of loop 'column' names, and the second is a list of values.  This can then
    be accessed by setting the stepsize to the length of the 'column'.
    ie: for a list of all the values in the third column do: l[1][2::len(l[0])]

    """
    NEF_REQUIRED_SAVEFRAME_BY_FRAMECODE = ['nef_nmr_meta_data',
                                           'nef_molecular_system']
    NEF_REQUIRED_SAVEFRAME_BY_CATEGORY = ['nef_chemical_shift_list',]

    NEF_ALL_SAVEFRAME_REQUIRED_FIELDS = ['sf_category',
                                         'sf_framecode',]

    MD_REQUIRED_FIELDS = ['sf_category',
                          'sf_framecode',
                          'format_name',
                          'format_version',
                          'program_name',
                          'program_version',
                          'creation_date',
                          'uuid']
    MD_OPTIONAL_FIELDS = ['coordinate_file_name',]
    MD_OPTIONAL_LOOPS = ['nef_related_entries',
                         'nef_program_script',
                         'nef_run_history']
    MD_RE_REQUIRED_FIELDS = ['database_name',
                             'database_accession_code']
    MD_PS_REQUIRED_FIELDS = ['program_name',]
    MD_RH_REQUIRED_FIELDS = ['run_ordinal',
                             'program_name']
    MD_RH_OPTIONAL_FIELDS = ['program_version',
                             'script_name',
                             'script']

    MS_REQUIRED_FIELDS = ['sf_category',
                          'sf_framecode']
    MS_REQUIRED_LOOPS = ['nef_sequence']
    MS_OPTIONAL_LOOPS = ['nef_covalent_links']
    MS_NS_REQUIRED_FIELDS = ['chain_code',
                             'sequence_code',
                             'residue_type',
                             'linking',
                             'residue_variant']
    MS_CL_REQUIRED_FIELDS = ['chain_code_1',
                             'sequence_code_1',
                             'residue_type_1',
                             'atom_name_1',
                             'chain_code_2',
                             'sequence_code_2',
                             'residue_type_2',
                             'atom_name_2']

    CSL_REQUIRED_FIELDS = ['sf_category',
                           'sf_framecode',]
    CSL_REQUIRED_LOOPS = ['nef_chemical_shift']
    CSL_CS_REQUIRED_FIELDS = ['chain_code',
                              'sequence_code',
                              'residue_type',
                              'atom_name',
                              'value']
    CSL_CS_OPTIONAL_FIELDS = ['value_uncertainty',]

    DRL_REQUIRED_FIELDS = ['sf_category',
                           'sf_framecode',
                           'potential_type']
    DRL_REQUIRED_LOOPS = ['nef_distance_restraint']
    DRL_OPTIONAL_FIELDS = ['restraint_origin',]
    DRL_DR_REQUIRED_FIELDS = ['ordinal',
                              'restraint_id',
                              'chain_code_1',
                              'sequence_code_1',
                              'residue_type_1',
                              'atom_name_1',
                              'chain_code_2',
                              'sequence_code_2',
                              'residue_type_2',
                              'atom_name_2',
                              'weight']
    DRL_DR_OPTIONAL_FIELDS = ['restraint_combination_id',
                              'target_value',
                              'target_value_uncertainty',
                              'lower_linear_limit',
                              'lower_limit',
                              'upper_limit',
                              'upper_linear_limit',]

    DIHRL_REQUIRED_FIELDS = ['sf_category',
                           'sf_framecode',
                           'potential_type']
    DIHRL_REQUIRED_LOOPS = ['nef_dihedral_restraint']
    DIHRL_OPTIONAL_FIELDS = ['restraint_origin',]
    DIHRL_DIHR_REQUIRED_FIELDS = ['ordinal',
                              'restraint_id',
                              'chain_code_1',
                              'sequence_code_1',
                              'residue_type_1',
                              'atom_name_1',
                              'chain_code_2',
                              'sequence_code_2',
                              'residue_type_2',
                              'atom_name_2',
                              'chain_code_3',
                              'sequence_code_3',
                              'residue_type_3',
                              'atom_name_3',
                              'chain_code_4',
                              'sequence_code_4',
                              'residue_type_4',
                              'atom_name_4',
                              'weight']
    DIHRL_DIHR_OPTIONAL_FIELDS = ['restraint_combination_id',
                              'target_value',
                              'target_value_uncertainty',
                              'lower_linear_limit',
                              'lower_limit',
                              'upper_limit',
                              'upper_linear_limit',]

    RRL_REQUIRED_FIELDS = ['sf_category',
                           'sf_framecode',
                           'potential_type']
    RRL_REQUIRED_LOOPS = ['nef_rdc_restraint']
    RRL_OPTIONAL_FIELDS = ['restraint_origin',
                           'tensor_magnitude',
                           'tensor_rhombicity',
                           'tensor_chain_code',
                           'tensor_sequence_code',
                           'tensor_residue_type',]
    RRL_RR_REQUIRED_FIELDS = ['ordinal',
                              'restraint_id',
                              'chain_code_1',
                              'sequence_code_1',
                              'residue_type_1',
                              'atom_name_1',
                              'chain_code_2',
                              'sequence_code_2',
                              'residue_type_2',
                              'atom_name_2',
                              'weight']
    RRL_RR_OPTIONAL_FIELDS = ['restraint_combination_id',
                              'target_value',
                              'target_value_uncertainty',
                              'lower_linear_limit',
                              'lower_limit',
                              'upper_limit',
                              'upper_linear_limit',
                              'scale',
                              'distance_dependent',]

    PL_REQUIRED_FIELDS = ['sf_category',
                           'sf_framecode',
                           'num_dimensions',
                           'chemical_shift_list']
    PL_REQUIRED_LOOPS = ['nef_spectrum_dimension',
                          'nef_spectrum_dimension_transfer',
                          'nef_peak']
    PL_OPTIONAL_FIELDS = ['experiment_classification',
                           'experiment_type']
    PL_SD_REQUIRED_FIELDS = ['dimension_id',
                              'axis_unit',
                              'axis_code']
    PL_SD_OPTIONAL_FIELDS = ['spectrometer_frequency',
                              'spectral_width',
                              'value_first_point',
                              'folding',
                              'absolute_peak_positions',
                              'is_acquisition',]
    PL_SDT_REQUIRED_FIELDS = ['dimension_1',
                              'dimension_2',
                              'transfer_type']
    PL_SDT_OPTIONAL_FIELDS = ['is_indirect',]
    PL_P_REQUIRED_FIELDS = ['ordinal',
                            'peak_id',
                            'volume']
    PL_P_REQUIRED_ALTERNATE_FIELDS = [['height','volume'],]
    PL_P_REQUIRED_FIELDS_PATTERN = ['position_{%}',
                                    'chain_code_{%}',
                                    'sequence_code_{%}',
                                    'residue_type_{%}',
                                    'atom_name_{%}',]

    PL_P_OPTIONAL_FIELDS_PATTERN = ['position_uncertainty_{%}',]



    def __init__(self, input_filename=None, initialize=True):
        super(Nef, self).__init__()

        self.input_filename = input_filename

        self.datablock = 'DEFAULT'

        if initialize:
            self.initialize()


    def initialize(self):
        self['nef_nmr_meta_data'] = OrderedDict()
        self['nef_nmr_meta_data'].update({k:'' for k in Nef.MD_REQUIRED_FIELDS})
        self['nef_nmr_meta_data']['sf_category'] = 'nef_nmr_meta_data'
        self['nef_nmr_meta_data']['sf_framecode'] = 'nef_nmr_meta_data'
        self['nef_nmr_meta_data']['format_name'] = 'Nmr_Exchange_Format'
        self['nef_nmr_meta_data']['format_version'] = __version__
        # for l in Nef.MD_REQUIRED_LOOPS:
        #     self['nef_nmr_meta_data'][l] = []

        self['nef_molecular_system'] = OrderedDict()
        self['nef_molecular_system'].update({k:'' for k in Nef.MS_REQUIRED_FIELDS})
        self['nef_molecular_system']['sf_category'] = 'nef_molecular_system'
        self['nef_molecular_system']['sf_framecode'] = 'nef_molecular_system'
        for l in Nef.MS_REQUIRED_LOOPS:
            self['nef_molecular_system'][l] = []

        self.add_nef_chemical_shift_list('nef_chemical_shift_list_1')


    def add_nef_chemical_shift_list(self, name):
        self[name] = OrderedDict( )
        self[name].update( { k: '' for k in Nef.CSL_REQUIRED_FIELDS } )
        self[name][ 'sf_category' ] = 'nef_chemical_shift_list'
        self[name][ 'sf_framecode' ] = 'nef_chemical_shift_list_1'
        for l in Nef.CSL_REQUIRED_LOOPS:
            self[name][ l ] = [ ]
        return self[name]

    def read(self, file_like, strict=True):
        """
        Populate the NEF object from a file-like object

        :param file_like:
        :param strict: bool
        """
        tokenizer = Lexer()
        parser = Parser(self)

        parser.strict = strict

        del self.datablock
        del self['nef_nmr_meta_data']
        del self['nef_molecular_system']
        del self['nef_chemical_shift_list']

        parser.parse(tokenizer.tokenize(file_like))

        validator = Validator()
        validation_problems = validator.validate(self)
        if len(validation_problems) > 0:
            print(validation_problems)


    def load(self, filename=None, strict=True):
        """
        Open a file on disk and use it to populate the NEF object.

        :param filename: str
        :param strict: bool
        """

        if filename is None:
            filename = self.input_filename
        else:
            self.input_filename = filename

        with open(filename, 'r') as f:
            self.read(f.read(), strict=strict)


class Validator(object):

    def __init__(self, nef=None):
        self.nef = nef
        self.validation_errors = []


    def __dict_missing_keys(self, dct, required_keys, label=None):
        if label is None:
            return ['Missing {} label.'.format(key) for key in required_keys if key not in dct]
        return ['{}: missing {} label.'.format(label, key) for key in required_keys if key not in dct]

    def __dict_missing_value_with_key(self, dct, keys):
        errors = []
        for key in keys:
            found_key = False
            for k,v in dct.items():
                if ('sf_category' in v) and (v['sf_category'] == key):
                    found_key = True
            if not found_key:
                errors.append('No saveframes with sf_category: {}.'.format(key))
        return errors

    def  __sf_framecode_name_mismatch(self, dct, sf_framecode):
        if 'sf_framecode' in dct:
            if dct['sf_framecode'] != sf_framecode:
                return ["sf_framecode {} must match key {}.".format(dct['sf_framecode'], sf_framecode)]
        return []

    def  __sf_category_name_mismatch(self, dct, sf_category):
        if 'sf_category' in dct:
            if dct['sf_category'] != sf_category:
                return ["sf_category {} must be {}.".format(dct['sf_category'], sf_category)]
        # else:
        #     return ["No sf_category.",]
        return []


    def __loop_entries_inconsistent_keys(self, loop, label):
        errors = []
        if len(loop) > 0:
            fields = list(loop[0].keys())
            fields_count = len(fields)
            finished = False
            while not finished:
                finished = True
                for i, entry in enumerate(loop):
                    for field in entry:
                        if field not in fields:
                            fields.append(field)
                            errors.append('{} entry {}: missing {} label.'.format(label, i, field))
                            break
                    if len(fields) > fields_count:
                        fields_count = len(fields)
                        finished = False
                        break
        return errors



    def isValid(self, nef=None):
        if nef is None:
            nef = self.nef
        self.validation_errors = dict()

        # self.validation_errors.update(self._validate_datablock(nef))
        # self.validation_errors.update(self._validate_required_saveframes(nef))
        self.validation_errors.update(self._validate_saveframe_fields(nef))
        # self.validation_errors.update(self._validate_metadata(nef))
        # self.validation_errors.update(self._validate_molecular_system(nef))
        # self.validation_errors.update(self._validate_chemical_shift_lists(nef))

        v = list(self.validation_errors.values())
        return not any(v)


    def _validate_datablock(self, nef=None):
        if nef is None:
            nef = self.nef

        if not hasattr(nef, 'datablock'):
            return {'DATABLOCK': 'No data block specified'}
        return {'DATABLOCK': None}


    def _validate_saveframe_fields(self, nef=None):
        ERROR_KEY = 'SAVEFRAMES'

        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        for sf_name, saveframe in nef.items():
            e += self.__dict_missing_keys(saveframe,
                                          Nef.NEF_ALL_SAVEFRAME_REQUIRED_FIELDS,
                                          label=sf_name)
            e += self.__sf_framecode_name_mismatch(saveframe, sf_name)
        return errors


    def _validate_required_saveframes(self, nef=None):
        ERROR_KEY = 'REQUIRED_SAVEFRAMES'

        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        e += self.__dict_missing_keys(nef, Nef.NEF_REQUIRED_SAVEFRAME_BY_FRAMECODE)
        e += self.__dict_missing_value_with_key(nef, Nef.NEF_REQUIRED_SAVEFRAME_BY_CATEGORY)
        return errors

    def __dict_nonallowed_keys(self, dct, allowed_keys, label=None):
        if label is None:
            return ["Field '{}' not allowed.".format(key)
                    for key in dct.keys() if key not in allowed_keys]
        return ["Field '{}' not allowed in {}.".format(key, label)
                for key in dct.keys() if key not in allowed_keys]


    def _validate_metadata(self, nef=None):
        ERROR_KEY = 'METADATA'
        DICT_KEY = 'nef_nmr_meta_data'

        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        if DICT_KEY not in nef:
            return {ERROR_KEY: 'No {} saveframe.'.format(DICT_KEY)}
        else:
            md = nef[DICT_KEY]
            e += self.__dict_missing_keys(md, Nef.MD_REQUIRED_FIELDS)
            e += self.__sf_framecode_name_mismatch(md, DICT_KEY)
            e += self.__sf_category_name_mismatch(md, DICT_KEY)
            e += self.__dict_nonallowed_keys(md, (Nef.MD_REQUIRED_FIELDS +
                                                  Nef.MD_OPTIONAL_FIELDS +
                                                  Nef.MD_OPTIONAL_LOOPS),
                                             label = DICT_KEY)

            if 'format_name' in md:
                if md['format_name'] != 'Nmr_Exchange_Format':
                    e.append("format_name must be 'Nmr_Exchange_Format'.")
            if 'format_version' in md:
                major_version = md['format_version'].split('.')[0]
                if major_version != __version__.split('.')[0]:
                    e.append('This reader does not support format version {}.'.format(major_version))
            if 'creation_date' in md:
                pass # TODO: How to validate the creation date?
            if 'uuid' in md:
                pass # TODO: How to validate the uuid?

            if 'nef_related_entries' in md:
                for i, entry in enumerate(md['nef_related_entries']):
                    label = '{}:nef_related_entries entry {}'.format(DICT_KEY, i+1)
                    e += self.__dict_missing_keys(entry, Nef.MD_RE_REQUIRED_FIELDS, label = label)
                    e += self.__dict_nonallowed_keys(entry, Nef.MD_RE_REQUIRED_FIELDS, label = label)

            if 'nef_program_script' in md:
                for i, entry in enumerate(md['nef_program_script']):
                    label = '{}:nef_program_script entry {}'.format(DICT_KEY, i+1)
                    e += self.__dict_missing_keys(entry, Nef.MD_PS_REQUIRED_FIELDS, label = label)
                    # Note: Because program specific parameters are allowed, there are not restrictions
                    # on what fields can be in this loop
                e += self.__loop_entries_inconsistent_keys(md['nef_program_script'],
                                                           label='{}:nef_program_script'.format(DICT_KEY))

            if 'nef_run_history' in md:
                for i, entry in enumerate(md['nef_run_history']):
                    label = '{}:nef_run_history entry {}'.format(DICT_KEY, i+1)
                    e += self.__dict_missing_keys(entry, Nef.MD_RH_REQUIRED_FIELDS, label = label)
                    e += self.__dict_nonallowed_keys(entry,
                                                     (Nef.MD_RH_REQUIRED_FIELDS +
                                                      Nef.MD_RH_OPTIONAL_FIELDS),
                                                     label = label)
                e += self.__loop_entries_inconsistent_keys(md['nef_run_history'],
                                                           label='{}:nef_run_history'.format(DICT_KEY))

        return errors


    def _validate_molecular_system(self, nef=None):
        ERROR_KEY = 'MOLECULAR_SYSTEM'
        DICT_KEY = 'nef_molecular_system'
        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        if 'nef_molecular_system' not in nef:
            return {ERROR_KEY: 'No {} saveframe.'.format(DICT_KEY)}
        else:
            ms = nef[DICT_KEY]
            e += self.__dict_missing_keys(ms, Nef.MS_REQUIRED_FIELDS + Nef.MS_REQUIRED_LOOPS)
            e += self.__dict_nonallowed_keys(ms, (Nef.MS_REQUIRED_FIELDS +
                                                  Nef.MS_REQUIRED_LOOPS +
                                                  Nef.MS_OPTIONAL_LOOPS),
                                             label = DICT_KEY)
            e += self.__sf_framecode_name_mismatch(ms, DICT_KEY)
            e += self.__sf_category_name_mismatch(ms, DICT_KEY)

            if 'nef_sequence' in ms:
                if len(ms['nef_sequence']) == 0:
                    e.append('Empty nef_sequence.')
                else:
                    for i, entry in enumerate(ms['nef_sequence']):
                        label = '{}:nef_sequence entry {}'.format(DICT_KEY, i+1)
                        e += self.__dict_missing_keys(entry, Nef.MS_NS_REQUIRED_FIELDS, label = label)
                        e += self.__dict_nonallowed_keys(entry, Nef.MS_NS_REQUIRED_FIELDS, label = label)

            if 'nef_covalent_links' in ms:
                for i, entry in enumerate(ms['nef_covalent_links']):
                    label = '{}:nef_covalent_links entry {}'.format(DICT_KEY, i+1)
                    e += self.__dict_missing_keys(entry, Nef.MS_CL_REQUIRED_FIELDS, label = label)
                    e += self.__dict_nonallowed_keys(entry, Nef.MS_CL_REQUIRED_FIELDS, label = label)
        return errors


    def _validate_chemical_shift_lists(self, nef=None):
        ERROR_KEY = 'CHEMICAL_SHIFT_LISTS'

        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        found_csl = False
        for saveframe_name, saveframe in nef.items():
            if 'sf_category' in saveframe:
                if saveframe['sf_category'] == 'nef_chemical_shift_list':
                    found_csl = True
                    e += self.__dict_missing_keys(saveframe,
                                                  (Nef.CSL_REQUIRED_FIELDS +
                                                   Nef.CSL_REQUIRED_LOOPS),
                                                  label = saveframe_name)
                    e += self.__dict_nonallowed_keys(saveframe, (Nef.CSL_REQUIRED_FIELDS +
                                                                 Nef.CSL_REQUIRED_LOOPS),
                                                                 label = saveframe_name)

                    if 'nef_chemical_shift' in saveframe:
                        for i, entry in enumerate(saveframe['nef_chemical_shift']):
                            label = '{}:nef_chemical_shift entry {}'.format(saveframe_name, i+1)
                            e += self.__dict_missing_keys(entry, Nef.CSL_CS_REQUIRED_FIELDS, label = label)
                            e += self.__dict_nonallowed_keys(entry,
                                                             (Nef.CSL_CS_REQUIRED_FIELDS +
                                                              Nef.CSL_CS_OPTIONAL_FIELDS),
                                                             label = label)
                        e += self.__loop_entries_inconsistent_keys(saveframe['nef_chemical_shift'],
                                                                   label='{}:nef_chemical_shift'.format(saveframe_name))
        if not found_csl:
            e.append('No nef_chemical_shift_list saveframes found.')
        return errors


    def _validate_distance_restraint_lists(self, nef=None):
        ERROR_KEY = 'DISTANCE_RESTRAINT_LISTS'

        if nef is None:
            nef = self.nef
        errors = {ERROR_KEY: []}
        e = errors[ERROR_KEY]

        for saveframe_name, saveframe in nef.items():
            if 'sf_category' in saveframe:
                if saveframe['sf_category'] == 'nef_distance_restraint_list':
                    e += self.__dict_missing_keys(saveframe,
                                                  (Nef.DRL_REQUIRED_FIELDS +
                                                   Nef.DRL_REQUIRED_LOOPS),
                                                  label = saveframe_name)
                    e += self.__dict_nonallowed_keys(saveframe, (Nef.DRL_REQUIRED_FIELDS +
                                                                 Nef.DRL_REQUIRED_LOOPS +
                                                                 Nef.DRL_OPTIONAL_FIELDS),
                                                                 label = saveframe_name)

                    if 'nef_distance_restraint' in saveframe:
                        for i, entry in enumerate(saveframe['nef_distance_restraint']):
                            label = '{}:nef_distance_restraint entry {}'.format(saveframe_name, i+1)
                            e += self.__dict_missing_keys(entry, Nef.DRL_DR_REQUIRED_FIELDS, label = label)
                            e += self.__dict_nonallowed_keys(entry,
                                                             (Nef.DRL_DR_REQUIRED_FIELDS +
                                                              Nef.DRL_DR_OPTIONAL_FIELDS),
                                                             label = label)
                        e += self.__loop_entries_inconsistent_keys(saveframe['nef_distance_restraint'],
                                                                   label='{}:nef_distance_restraint'.format(saveframe_name))
        return errors


    # def _validate_distance_restraint_lists(self, nef=None):
    #     ERROR_KEY = 'DISTANCE_RESTRAINT_LISTS'
    #
    #     if nef is None:
    #         nef = self.nef
    #     errors = {ERROR_KEY: []}
    #     e = errors[ERROR_KEY]
    #
    #     for k,v in nef.items():
    #         if (v['sf_category'] == 'nef_distance_restraint_list'):
    #             if 'sf_framecode' not in v:
    #                 e.append('{}: missing sf_framecode'.format(k))
    #             elif v['sf_framecode'] != k:
    #                 e.append('{}: Mismatched key and sf_framecode'.format(k))
    #             if 'potential_type' not in v:
    #                 e.append('{}: missing potential_type'.format(k))
    #             if 'nef_distance_restraint' not in v:
    #                 e.append('{}: missing nef_distance_restraint loop'.format(k))
    #             elif len(v['nef_distance_restraint']) > 0:
    #                 dr = v['nef_distance_restraint']
    #                 required_fields = Nef.DRL_DR_REQUIRED_FIELDS
    #                 rf_count = len(required_fields)
    #                 finished = False
    #                 while not finished:
    #                     finished = True
    #                     for n, s in enumerate(dr):
    #                         for field in s:
    #                             if field not in required_fields:
    #                                 if field in Nef.DRL_DR_OPTIONAL_FIELDS:
    #                                     required_fields.append(field)
    #                                     break
    #                                 else:
    #                                     e.append('{}:nef_distance_restraint entry {}: "{}" field not allowed'
    #                                              .format(v['sf_framecode'], n+1, field))
    #                         if len(required_fields) > rf_count:
    #                             rf_count = len(required_fields)
    #                             finished = False
    #                             break
    #                         [e.append('{}:nef_chemical_shift entry {}: missing {}'
    #                                   .format(v['sf_framecode'], n+1, req))
    #                                   for req in required_fields if req not in s]
    #             drl_allowed = Nef.DRL_REQUIRED_FIELDS
    #             drl_allowed += Nef.DRL_REQUIRED_LOOPS
    #             drl_allowed += Nef.DRL_OPTIONAL_FIELDS
    #             [e.append('{}: "{}" field not allowed'.format(v['sf_category'], f))
    #              for f in v if f not in drl_allowed]
    #     return errors