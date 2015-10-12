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
    MAJOR_VERSION = '0'
    MINOR_VERSION = '8'
    VERSION = '.'.join((MAJOR_VERSION, MINOR_VERSION))

    MD_REQUIRED_FIELDS = ['sf_category',
                          'sf_framecode',
                          'format_name',
                          'format_version',
                          'program_name',
                          'program_version',
                          'creation_date',
                          'uuid']
    MD_REQUIRED_LOOPS = ['nef_sequence']
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
                           'sf_framecode']
    CSL_REQUIRED_LOOPS = ['nef_chemical_shift']
    CSL_CS_REQUIRED_FIELDS = ['chain_code',
                          'sequence_code',
                          'residue_type',
                          'atom_name',
                          'value']
    CSL_CS_OPTIONAL_FIELDS = ['value_uncertainty',]


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
        # for l in Nef.MD_REQUIRED_LOOPS:
        #     self['nef_nmr_meta_data'][l] = []

        self['nef_molecular_system'] = OrderedDict()
        self['nef_molecular_system'].update({k:'' for k in Nef.MS_REQUIRED_FIELDS})
        self['nef_molecular_system']['sf_category'] = 'nef_molecular_system'
        self['nef_molecular_system']['sf_framecode'] = 'nef_molecular_system'
        for l in Nef.MS_REQUIRED_LOOPS:
            self['nef_molecular_system'][l] = []

        self['nef_chemical_shift_list_1'] = OrderedDict()
        self['nef_chemical_shift_list_1'].update({k:'' for k in Nef.CSL_REQUIRED_FIELDS})
        self['nef_chemical_shift_list_1']['sf_category'] = 'nef_chemical_shift_list'
        self['nef_chemical_shift_list_1']['sf_framecode'] = 'nef_chemical_shift_list_1'
        for l in Nef.CSL_REQUIRED_LOOPS:
            self['nef_chemical_shift_list_1'][l] = []



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


    def isValid(self, nef=None):
        if nef is None:
            nef = self.nef
        self.validation_errors = dict()

        self.validation_errors.update(self._validate_datablock(nef))
        self.validation_errors.update(self._validate_required_saveframes(nef))
        self.validation_errors.update(self._validate_saveframe_fields(nef))
        self.validation_errors.update(self._validate_metadata(nef))
        self.validation_errors.update(self._validate_molecular_system(nef))
        self.validation_errors.update(self._validate_chemical_shift_lists(nef))

        v = list(self.validation_errors.values())
        return not any(v)


    def _validate_datablock(self, nef=None):
        if nef is None:
            nef = self.nef

        if not hasattr(nef, 'datablock'):
            return {'DATABLOCK': 'No data block specified'}
        return {'DATABLOCK': None}


    def _validate_saveframe_fields(self, nef=None):
        if nef is None:
            nef = self.nef
        errors = {'SAVEFRAMES': []}
        e = errors['SAVEFRAMES']

        for k,v in nef.items():
            if 'sf_framecode' not in v:
                e.append('No sf_framecode in {}'.format(k))
            else:
                if v['sf_framecode'] != k:
                    e.append('sf_framecode "{}" does not match framecode name "{}".'
                             .format(v['sf_framecode'], k))
            if 'sf_category' not in v:
                e.append('No sf_category in "{}"'.format(k))
        return errors


    def _validate_required_saveframes(self, nef=None):
        if nef is None:
            nef = self.nef
        errors = {'REQUIRED_SAVEFRAMES': []}
        e = errors['REQUIRED_SAVEFRAMES']

        if 'nef_nmr_meta_data' not in nef:
            e.append('No nef_nmr_meta_data saveframe')
        if 'nef_molecular_system' not in nef:
            e.append('No nef_molecular_system saveframe')
        found_csl = False
        for k,v in nef.items():
         if ('sf_category' in v) and (v['sf_category'] == 'nef_chemical_shift_list'):
                found_csl = True
                break
        if not found_csl:
            e.append('No nef_chemical_shift_list saveframe(s)')
        return errors


    def _validate_metadata(self, nef=None):
        if nef is None:
            nef = self.nef
        errors = {'METADATA': []}
        e = errors['METADATA']

        if 'nef_nmr_meta_data' not in nef:
            return {'METADATA': 'No nef_nmr_meta_data saveframe'}
        else:
            md = nef['nef_nmr_meta_data']
            if 'sf_framecode' not in md:
                e.append('No sf_framecode')
            elif md['sf_framecode'] != 'nef_nmr_meta_data':
                e.append('sf_framecode must be nef_nmr_meta_data')
            if 'sf_category' not in md:
                e.append('No sf_category')
            elif md['sf_category'] != 'nef_nmr_meta_data':
                e.append('sf_category must be nef_nmr_meta_data')
            [e.append('No {}'.format(i)) for i in Nef.MD_REQUIRED_FIELDS if i not in md]
            if 'nef_related_entries' in md:
                re = md['nef_related_entries']
                if len(re) == 0:
                    pass
                else:
                    for n, v in enumerate(re):
                        [e.append('nef_nmr_meta_data:related_entries entry {}: no {}'
                                  .format(n+1, i))
                            for i in Nef.MD_RE_REQUIRED_FIELDS if i not in re]
                        [e.append('nef_nmr_meta_data:related_entries entry {}: "{}" field not allowed.'
                                  .format(n+1, j))
                            for j in v if j not in Nef.MD_RE_REQUIRED_FIELDS]
            if 'nef_program_script' in md:
                ps = md['nef_program_script']
                if len(ps) == 0:
                    pass
                else:
                    for n, v in enumerate(ps):
                        [e.append('nef_nmr_meta_data:program_script entry {}: no {}'
                                  .format(n+1, i))
                            for i in Nef.MD_PS_REQUIRED_FIELDS if i not in ps]
            if 'nef_run_history' in md:
                rh = md['nef_run_history']
                if len(rh) == 0:
                    pass
                else:
                    for n, v in enumerate(rh):
                        [e.append('nef_nmr_meta_data:nef_run_history entry {}: no {}'.format(n+1, i))
                                for i in Nef.MD_RH_REQUIRED_FIELDS if i not in rh]
                        rh_allowed = Nef.MD_RH_REQUIRED_FIELDS + Nef.MD_RH_OPTIONAL_FIELDS
                        [e.append('nef_nmr_meta_data:nef_run_history entry {}: "{}" field not allowed.'
                                  .format(n+1, j)) for j in v if j not in rh_allowed]
            md_allowed = Nef.MD_REQUIRED_FIELDS
            md_allowed += Nef.MD_REQUIRED_LOOPS
            md_allowed += Nef.MD_OPTIONAL_FIELDS
            md_allowed += Nef.MD_OPTIONAL_LOOPS
            [e.append('"{}" field not allowed'.format(j)) for j in md if j not in md_allowed]
        return errors


    def _validate_molecular_system(self, nef=None):
        if nef is None:
            nef = self.nef
        errors = {'MOLECULAR_SYSTEM': []}
        e = errors['MOLECULAR_SYSTEM']

        if 'nef_molecular_system' not in nef:
            return {'MOLECULAR_SYSTEM': 'No nef_nmr_meta_data saveframe'}
        else:
            ms = nef['nef_molecular_system']
            if 'sf_framecode' not in ms:
                e.append('No sf_framecode')
            elif ms['sf_framecode'] != 'nef_molecular_system':
                e.append('sf_framecode must be nef_molecular_system')
            if 'sf_category' not in ms:
                e.append('No sf_category')
            elif ms['sf_category'] != 'nef_molecular_system':
                e.append('sf_category must be nef_molecular_system')
            if 'nef_sequence' not in ms:
                e.append('No nef_sequence loop')
            elif len(ms['nef_sequence']) == 0:
                e.append('empty nef_sequence')
            else:
                for n,s in enumerate(ms['nef_sequence']):
                    for i in Nef.MS_NS_REQUIRED_FIELDS:
                        if i not in s:
                            e.append('nef_seqence entry {}: missing {}'.format(n+1, i))
                if 'nef_covalent_links' in ms:
                    cl = ms['nef_covalent_links']
                    if len(cl) == 0:
                        pass
                    else:
                        for n, v in enumerate(cl):
                            [e.append('nef_molecular_system:nef_covalent_links entry {}: no {}'.format(n+1, i))
                                    for i in Nef.MS_CL_REQUIRED_FIELDS if i not in v]
                            [e.append('nef_molecular_system:nef_covalent_links entry {}: "{}" field not allowed.'
                                      .format(n+1, j)) for j in v if j not in Nef.MS_CL_REQUIRED_FIELDS]
        return errors


    def _validate_chemical_shift_lists(self, nef=None):
        if nef is None:
            nef = self.nef
        errors = {'CHEMICAL_SHIFT_LISTS': []}
        e = errors['CHEMICAL_SHIFT_LISTS']

        for k,v in nef.items():
            if (v['sf_category'] == 'nef_chemical_shift_list'):
                if 'sf_framecode' not in v:
                    e.append('{}: No sf_framecode'.format(k))
                if 'nef_chemical_shift' not in v:
                    e.append('{}: No nef_chemical_shift loop'.format(k))
                elif len(v['nef_chemical_shift']) > 0:
                    sl = v['nef_chemical_shift']
                    for n,s in enumerate(sl):
                        [e.append('{}:nef_chemical_shift_list entry {}: missing {}'
                                  .format(v['sf_framecode'], n+1, i))
                            for i in Nef.CSL_CS_REQUIRED_FIELDS if i not in s]
                        cs_allowed = Nef.CSL_CS_REQUIRED_FIELDS + Nef.CSL_CS_OPTIONAL_FIELDS
                        [e.append('nef_molecular_system:nef_covalent_links entry {}: "{}" field not allowed.'
                                      .format(n+1, j)) for j in s if j not in cs_allowed]
        return errors