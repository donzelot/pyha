import collections

import numpy as np


def is_power2(num):
    # Author: A.Polino
    'states if a number is a power of two'
    return num != 0 and ((num & (num - 1)) == 0)


def get_iterable(x):
    if isinstance(x, collections.Iterable):
        return x
    else:
        return [x]


def is_constant(name):
    return True if name.replace('_', '').isupper() else False


def tabber(str):
    TAB = '    '
    """ Add tab infront of every line """
    # if x is '' then dont add tabs, because much used textwrap.dedent deletes empty tabs...so unit tests will be unhappy
    return '\n'.join([f'{TAB}{x}' if x != '' else x for x in str.splitlines()])


def formatter(xl):
    return '\n'.join(tabber(x) for x in xl if x != '')


def hex_to_bitstr(hstr):
    """ http://stackoverflow.com/questions/1425493/convert-hex-to-binary """
    if isinstance(hstr, int):
        hstr = hex(hstr)
    if hstr[0:2] in ('0x', '0X'):
        hstr = hstr[2:]
    my_hexdata = hstr
    scale = 16  ## equals to hexadecimal
    num_of_bits = int(len(my_hexdata) * np.log2(scale))
    return bin(int(my_hexdata, scale))[2:].zfill(num_of_bits)


def hex_to_bool_list(hstr):
    return [bool(int(x)) for x in hex_to_bitstr(hstr)]


def int_to_bool_list(hstr):
    return [bool(int(x)) for x in hex_to_bitstr(hstr)]


def bools_to_hex(bl):
    bitstr = bools_to_bitstr(bl)
    return hex(int(bitstr, 2))


def bools_to_bitstr(bl):
    return ''.join(str(int(x)) for x in bl)


def np_to_py(array):
    """ Convert numpy to python recursively.
    For example float32 to float and ndarray to []
    """
    # https://github.com/numpy/numpy/issues/8052
    if isinstance(array, np.ndarray):
        if isinstance(array[0], complex):
            array = array.astype(complex)
        elif isinstance(array[0], np.floating):
            array = array.astype(float)

        return np_to_py(array.tolist())
    elif isinstance(array, list):
        return [np_to_py(item) for item in array]
    elif isinstance(array, tuple):
        return tuple(np_to_py(item) for item in array)
    elif isinstance(array, np.float):
        return float(array)
    else:
        return array
