from __future__ import unicode_literals, absolute_import, print_function
"""
Example usage of the Nef reader.

First, we'll use the conveniance function `open` to read one of the test files from disk.
Then, we'll explore the file and find some data.

"""
from NEFreader import Nef


nef_file = 'tests/test_files/CCPN_2l9r_Paris_155.nef'
paris = Nef()
paris.open(nef_file, strict=True)


# Get the data block name
print('Data Block name: {}'.format(paris.datablock))
print()

# List the saveframes and their categories
print ('Saveframes : categories')
for k in paris.keys():
    category = paris[k]['sf_category']
    print(k, ':', category)
print()


# List the information available in the `sequence` loop of the nef_molecular_system saveframe
print('nef_molecular_system;sequence columns')
print(paris['nef_molecular_system']['nef_sequence'][0])
print()


# List the 3 letter codes for the sequence
nef_sequence_loop = paris['nef_molecular_system']['nef_sequence']
number_of_columns = len(nef_sequence_loop[0])
sequence_column = nef_sequence_loop[0].index('residue_type')
print('Sequence')
print(nef_sequence_loop[1][sequence_column::number_of_columns])
print()


# Get the H, N shifts
# This code can be simplified, but is here to demonstrate access rather than production code
cs_loop = paris['nef_chemical_shift_list_bmrb21.str']['nef_chemical_shift']
number_of_columns = len(cs_loop[0])
aa_number_column = cs_loop[0].index('sequence_code')
aa_type_column = cs_loop[0].index('residue_type')
atom_name_column = cs_loop[0].index('atom_name')
cs_column = cs_loop[0].index('value')
rows = zip(cs_loop[1][aa_number_column::number_of_columns],
           cs_loop[1][aa_type_column::number_of_columns],
           cs_loop[1][atom_name_column::number_of_columns],
           cs_loop[1][cs_column::number_of_columns])

h_or_n_shifts = [row for row in rows if row[aa_type_column] in ('H','N')]

first_aa = int(rows[0][0])
last_aa = int(rows[-1][0])

shifts = {i:['.', '.','.'] for i in range(first_aa, last_aa+1)}

for shift in h_or_n_shifts:
    k = int(shift[0])
    shifts[k][0] = shift[1]
    if shift[2] == 'H':
        shifts[k][1] = float(shift[3])
    elif shift[2] == 'N':
        shifts[k][2] = float(shift[3])

print('#  | Type |   H   |   N   |')
fmt = '{:<4} {:<4}  {:<3}   {:>4}'
for k,v in shifts.items():
    print(fmt.format(k,*v))
print()


# Get the H, N shifts, but using pandas
try:
    import numpy as np
    import pandas as pd

    cs_loop = paris['nef_chemical_shift_list_bmrb21.str']['nef_chemical_shift']
    number_of_columns = len(cs_loop[0])

    # reshape the list of data values to a list of lists using numpy...
    ld = np.array(cs_loop[1]).reshape(-1, number_of_columns)
    # then create the dataframe
    df = pd.DataFrame(ld, columns=cs_loop[0])
    df.replace({'.': np.NAN, 'true': True, 'false': False}, inplace=True)
    atom_names_to_use = list(df['atom_name'].unique())

    first_aa = int(df['sequence_code'].min())
    last_aa = int(df['sequence_code'].max())

    # make an empty dataframe with the correct column names
    df_merged = pd.DataFrame(index=range(first_aa, last_aa+1),
                             columns=['type']+atom_names_to_use)
    df_merged.index = df_merged.index.astype(str) # NEF sequence_codes are strings

    # now fill in our empty data frame
    for atom_name in atom_names_to_use:
        df_atom_type = df[df['atom_name']==atom_name]
        df_atom_type = df_atom_type.set_index('sequence_code')
        df_atom_type = df_atom_type.rename(columns={'residue_type':'type', 'value':atom_name})
        df_merged.update(df_atom_type)

    print(df_merged[['type', 'H', 'N']])
    print()
    # Optionally you can replace the NA values with `.`
    print(df_merged[['type', 'H', 'N']].fillna('.'))
    print()

except ImportError:
    pass








