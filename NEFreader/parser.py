from __future__ import absolute_import, unicode_literals
__author__ = 'TJ Ragan'
__version__ = '0.1'

from collections import OrderedDict
from warnings import warn

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pass


# nef_file_name = '/Users/tjr22/Documents/NEF/NEF/specification/Commented_Example.nef'
# nef_file_name = '/Users/tjr22/Documents/NEF/NEF/data/CCPN_2l9r_Paris_155.nef'
nef_file_name = '/Users/tjr22/Documents/NEF/NEF/data/CCPN_2lci_Piscataway_179.nef'
# nef_file_name = '/Users/tjr22/Documents/NEF/NEF/data/CCPN_H1GI.nef'


class Tokenizer(object):

    def __init__(self, chars=None):
        self.chars = chars
        self.tokens = []


    def tokenize(self, chars=None):
        if chars is None:
            chars = self.chars

        self._state = 'start'
        self._newline = True

        self.tokens = []
        self._token = []

        for c in chars:

            ### Newline whitespace
            if c == '\n':
                self._newline_char( )

            ### Multi-line semicolon based strings
            elif (c == ';') and self._newline and (self._state == 'semicolon comment'):
                self._finish_semicolon_comment()
            elif (c == ';') and self._newline and (self._state != 'semicolon comment'):
                self._start_semicolon_comment()
            elif self._state == 'semicolon comment':
                self._continue_semicolon_comment(c)

            ### Comments
            elif c == '#':
                self._start_comment()
            elif self._state == 'comment':
                self._continue_comment(c)

            ### Quotes
            elif c in ('"', "'"):
                self._quote( c )
            ### Non-newline whitespace
            elif c in (' ', '\t'):
                self._whitespace( c )

            ### Actual characters
            else:
                self._actual_character( c )
        self._finish_token()

        return self.tokens

    def _quote( self, c ):
        if self._state is 'start':
            self._start_quote( c )
        elif self._state is 'quoted':
            self._continue_quote( c )

    def _newline_char( self ):
        self._newline = True
        if self._state != 'semicolon comment':
            self._uncommented_newline( )
        else:
            self._semicolon_commented_newline( )

    def _continue_quote( self, c ):
        self._token.append( c )
        if c == self._quote_char:
            self._state = 'potential unquote'

    def _start_quote( self, c ):
        self._quote_char = c
        self._state = 'quoted'

    def _actual_character( self, c ):
        self._newline = False
        if self._state == 'start':
            self._state = 'in token'
        elif self._state == 'potential unquote':
            self._state = 'quote'
        self._token.append( c )


    def _whitespace( self, c ):
        self._newline = False
        if self._state == 'quoted':
            self._quoted_whitespace( c )
        elif self._state == 'potential unquote':
            self._potential_unquote( )
        else:
            self._unquoted_whitespace( )


    def _unquoted_whitespace( self ):
        self._finish_token( )
        self._state = 'start'


    def _finish_token( self ):
        if len(self._token) > 0:
            self.tokens.append( ''.join( self._token ) )
            self._token = [ ]
        self._state = 'start'


    def _potential_unquote( self ):
        self._token = self._token[ :-1 ]
        self._finish_token( )
        self._state = 'start'


    def _quoted_whitespace( self, c ):
        self._token.append( c )


    def _continue_comment( self, c ):
        self._token.append( c )


    def _start_comment( self ):
        self._state = 'comment'
        self._newline = False
        self._token = [ '#' ]


    def _start_semicolon_comment( self ):
        self._state = 'semicolon comment'


    def _continue_semicolon_comment( self, c ):
        self._token.append( c )


    def _finish_semicolon_comment( self ):
        self._finish_token( )
        self._state = 'start'


    def _semicolon_commented_newline(self):
        self._token.append('\n')


    def _uncommented_newline( self ):
        if len( self._token ) > 0:
            if self._state == 'potential unquote':
                self._token = self._token[ :-1 ]
        self._finish_token()
        #self._state = 'start'
        self.tokens.append('\n')
        self._token = []



class Parser(object):

    def __init__(self, target = None, tokens=None, strict=True):
        self.tokens = tokens
        self.strict = strict
        if target is None:
            self.target = OrderedDict()
            self.no_target = True
        else:
            self.target = target
            self.no_target = False



    def parse(self, tokens=None):
        if tokens is None:
            tokens = self.tokens

        self._loop_key = None
        self._saveframe_name = None
        self._data_name = None

        for i, t in enumerate(tokens):
            ### Newlines
            if t == '\n':
                pass

            ### Comments
            elif t.startswith('#'):
                self._comment_token( t )

            ### Required datablock declaration
            elif t.lower().startswith('data_'):
                self._datablock_token(t)
            elif 'data block' not in self.target.keys():
                self._noncomment_token_outside_data_block( i )

            ### Globals (Are we using these?)
            elif t.lower().startswith('global_'):
                self._global_statement( t )

            ### Saveframes
            elif t.lower().startswith('save_'):
                self._save_token( i, t )

            ### Loops
            elif t.lower() == 'loop_':
                self._loop_token( i, t )
            elif t.lower() == 'stop_':
                self._stop_token( i, t )

            ### Data Names
            elif t.startswith('_'):
                self._data_name_token(i, t)

            ### Data Values
            else:
                self._data_value_token(i, t)

        if self.no_target:
            return self.target



    def _comment_token(self, t):
        if 'key:' in t.lower( ):
            self._loop_key = t


    def _datablock_token(self, t):
        if 'data block' not in self.target.keys():
            self.target['data block'] = t
            self._state = 'start'
        else:
            raise Exception('Multiple datablocks not allowed.')

    def _noncomment_token_outside_data_block(self, i):
        if self.strict:
            raise Exception('Token {}: NEF format requires all non-comments exist in a datablock.'
                            .format(i))
        else:
            self.target['data block'] = 'data_nef_default'


    def _global_statement(self, t):
        raise NotImplementedError('Globals not implemented.')


    def _save_token(self, i, t):
        if t.lower() == 'save_':
            self._end_saveframe_token( i, t )
        else:
            self._start_saveframe_token( i, t )

    def _loop_token(self, i, t):
        if self._state.startswith('in loop'):
            if self.strict:
                raise Exception('Token {}: Nested loops are not allowed.'.format( i ))
            else:
                self._finish_loop(i)
                self._start_loop(i)
        else:
            self._start_loop(i)

    def _stop_token(self, i, t):
        if self._state.startswith('in loop'):
            self._finish_loop(i)
        else:
            error_message = 'Token {}: Trying to close a loop without being in a loop.'.format(i)
            if self.strict:
                raise Exception(error_message)
            else:
                warn(error_message)


    def _data_name_token(self, i, t):
        self._data_name = t[1:]

        if self._state == 'in loop columns specification':
            self._loop_column_name_token( i )
        elif self._state == 'in loop data':
            self._finish_loop()


    def _data_value_token(self, i, t):

        if self._state == 'in loop columns specification':
            self._state = 'in loop data'

        if self._state == 'in saveframe':
            self._add_to_saveframe( i, t )
        elif self._state == 'in loop data':
            self._loop_data.append(t)

    def _add_to_saveframe( self, i, t ):
        if 'sf_category' in self.target[ self._saveframe_name ]:
            self._check_saveframe_category(i)
        self.target[ self._saveframe_name ][ self._data_name.split( '.' )[ 1 ] ] = t

    def _check_saveframe_category( self, i ):
        if self._data_name.split( '.' )[ 0 ] != self.target[ self._saveframe_name ][
            'sf_category' ]:
            error_message = 'Token {}: Mismatch data name type {} in saveframe {}' \
                .format( i, self._data_name, self._saveframe_name )
            if self.strict:
                raise Exception( error_message )
            else:
                warn( error_message )

    def _end_saveframe_token( self, i, t ):
        if self._state == 'in saveframe' or self._state.startswith( 'in loop' ):
            self._finish_saveframe(i)
        else:
            self._unnamed_saveframe(i)

    def _start_saveframe_token(self, i, t):
        if self._saveframe_name is not None:
                raise Exception( 'Token {}: Nested saveframes are not allowed.'.format( i ) )
        self._state = 'in saveframe'
        self._saveframe_name = t[5:]
        self.target[self._saveframe_name] = OrderedDict()


    def _start_loop(self, i):
        self._state = 'in loop columns specification'
        self._loop_name = None
        self._loop_columns = []
        self._loop_data = []


    def _finish_loop(self, i):
        number_of_columns = len(self._loop_columns)
        number_of_data_values = len(self._loop_data)
        if number_of_data_values % number_of_columns > 0:
            error_message = 'Token {}: Number of data values ({}) is not a multiple of number of '
            error_message += 'column names in loop {}'
            error_message = error_message.format(i,
                                                 number_of_data_values,
                                                 self._loop_name )
            if self.strict:
                raise Exception(error_message)
            else:
                warn(error_message)
                warn('Padding values to correct.')
                self._loop_data += ['.'] * (number_of_columns - (number_of_data_values %
                                                                 number_of_columns))

        self.target[self._saveframe_name][self._loop_name] = [self._loop_columns, self._loop_data]

        if self._saveframe_name is None:
            self._state = 'start'
        else:
            self._state = 'in saveframe'

        self._loop_name = None
        self._loop_columns = []


    def _loop_column_name_token(self, i):
        if self._loop_name is None:
            self._loop_name = self._data_name.split( '.' )[ 0 ]
        elif self._loop_name != self._data_name.split( '.' )[ 0 ]:
            error_message = 'Token {}: Mismatch column name {} in loop {}'.format( i,
                                                                           self._data_name,
                                                                           self._loop_name )
            if self.strict:
                raise Exception(error_message)
            else:
                warn( error_message )
        self._loop_columns.append( self._data_name.split( '.' )[ 1 ] )


    def _finish_saveframe(self, i):
        if self._state.startswith('in loop'):
            self._finish_loop(i)
        self._saveframe_name = None
        self._state = 'start'

    def _unnamed_saveframe(self, i):
        raise Exception( 'Token {}: Trying to declare saveframe without a name or close a saveframe without being in a saveframe.'
                         .format( i ) )


