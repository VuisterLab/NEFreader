__author__ = 'tjr22'

from collections import OrderedDict
from .parser import Tokenizer, Parser


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

    ms_required = ['chain_code',
                   'sequence_code',
                   'residue_type',
                   'linking',
                   'residue_variant']

    csl_required = ['chain_code',
                    'sequence_code',
                    'residue_type',
                    'atom_name',
                    'value']

    def __init__(self, input_filename=None, initialize=True):
        super(Nef, self).__init__()

        self.input_filename = input_filename

        self.datablock = None

        if initialize:
            self.initialize()

    def initialize(self):
        self['nef_nmr_meta_data'] = OrderedDict()
        self['nef_nmr_meta_data']['sf_category'] = 'nef_nmr_meta_data'
        self['nef_nmr_meta_data']['sf_framecode'] = 'nef_nmr_meta_data'
        # TODO: other required data

        self['nef_molecular_system'] = OrderedDict()
        self['nef_molecular_system']['sf_category'] = 'nef_molecular_system'
        self['nef_molecular_system']['sf_framecode'] = 'nef_molecular_system'
        self['nef_molecular_system']['nef_sequence'] = []
        self['nef_molecular_system']['nef_sequence'].append(Nef.ms_required)

        self['nef_chemical_shift_list'] = OrderedDict()
        self['nef_chemical_shift_list']['sf_category'] = 'nef_chemical_shift_list'
        self['nef_chemical_shift_list']['sf_framecode'] = 'nef_chemical_shift_list'
        self['nef_chemical_shift_list']['nef_chemical_shift'] = []
        self['nef_chemical_shift_list']['nef_chemical_shift'].append(Nef.csl_required)


    def read(self, file_like, strict=True):
        """
        Populate the NEF object from a file-like object

        :param file_like:
        :param strict: bool
        """
        tokenizer = Tokenizer()
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


    def open(self, filename=None, strict=True):
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

    def validate(self, nef=None):
        if nef is None:
            nef = self.nef

        invalid = []
        invalid += self.validate_datablock(nef)
        invalid += self.validate_nmr_meta_data(nef)
        invalid += self.validate_molecular_system(nef)
        invalid += self.validate_shift_list(nef)
        invalid += self.validate_general_saveframe_required(nef)
        return invalid

    def validate_general_saveframe_required(self, nef=None):
        if nef is None:
            nef = self.nef

        invalid = []
        for k, v in nef.items():
            if k == 'data block':
                continue
            for required in ['sf_category', 'sf_framecode']:
                if required not in v:
                    invalid.append('{} not found in saveframe {}.'.format(required, k))
        return invalid


    def validate_shift_list(self, nef=None):
        if nef is None:
            nef = self.nef

        invalid = []
        found_shift_list = False
        for k, v in nef.items():
            if k == 'data block':
                continue
            if v['sf_category'] == 'nef_chemical_shift_list':
                found_shift_list = True
                for required in Nef.csl_required:
                    if required not in v['nef_chemical_shift'][0]:
                        invalid.append('{} not found in {}.'.format(required, k))
        if not found_shift_list:
            invalid.append('No saveframe of type nef_chemical_shift_list found')
        return invalid


    def validate_molecular_system(self, nef=None):
        if nef is None:
            nef = self.nef

        invalid = []
        if 'nef_molecular_system' not in nef.keys():
            invalid.append('No nef_molecular_system saveframe')
        else:
            if 'nef_sequence' in nef['nef_molecular_system']:
                for required in Nef.ms_required:
                    if required not in nef['nef_molecular_system']['nef_sequence'][0]:
                        invalid.append('{} not found in nef_molecular_system; nef_sequence.'
                                       .format(required))
            else:
                invalid.append('No nef_sequence loop found in nef_molecular_system')
        return invalid


    def validate_nmr_meta_data(self, nef=None):
        if nef is None:
            nef = self.nef

        if 'nef_nmr_meta_data' not in nef.keys():
            return ['No nef_nmr_meta_data saveframe']
        return []


    def validate_datablock(self, nef=None):
        if nef is None:
            nef = self.nef

        if not hasattr(nef, 'datablock'):
            return ['No data block specified']
        return []
