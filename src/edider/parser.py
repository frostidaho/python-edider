#!/usr/bin/env python3

from itertools import zip_longest
from collections import namedtuple
import string
import struct

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def bytes_to_bits(bstr):
    return ['{:08b}'.format(x) for x in bstr]

def bytes_to_printable(bstr):
    bstr = bstr.decode('ascii', errors='ignore')
    return ''.join([x for x in bstr if x in string.printable])

def parse_descriptor(desc):
    # EDID Other Monitor Descriptors
    # Bytes	Description
    # 0–1	Zero, indicates not a detailed timing descriptor
    # 2	Zero
    # 3	Descriptor type. FA–FF currently defined. 00–0F reserved for vendors.
    # 4	Zero
    # 5–17	Defined by descriptor type. If text, code page 437 text
    GENERAL_TXT = 254
    if desc[0] != 0:
        return ''
    header = struct.unpack('5c', desc[0:5])
    descr_type = header[3][0]

    rest = desc[5:]
    if descr_type == GENERAL_TXT:
        return bytes_to_printable(rest)
    print('Unexpected Descriptor type:', f'{descr_type:02X}')
    print(rest)
    return bytes_to_printable(rest)



class EDIDSegmenter:
    def __init__(self, edid_bytes):
        "Pass the EDID as a bytes string"
        self._edid = edid_bytes

    def _get_bytes(self, offset, length):
        return self._edid[offset : offset+length]

    @property
    def fixed_header(self):
        return self._get_bytes(0, 8)

    @property
    def manufacturer_id(self):
        return self._get_bytes(8, 2)

    @property
    def product_code(self):
        return self._get_bytes(10, 2)

    @property
    def serial_number(self):
        return self._get_bytes(12, 4)

    @property
    def manufacture_week(self):
        return self._get_bytes(16, 1)

    @property
    def manufacture_year(self):
        return self._get_bytes(17, 1)

    @property
    def edid_version(self):
        return self._get_bytes(18, 1)

    @property
    def edid_revision(self):
        return self._get_bytes(19, 1)

    @property
    def horizontal_size(self):
        return self._get_bytes(21, 1)

    @property
    def vertical_size(self):
        return self._get_bytes(22, 1)

    @property
    def descriptor1(self):
        return self._get_bytes(54, 18)

    @property
    def descriptor2(self):
        return self._get_bytes(72, 18)

    @property
    def descriptor3(self):
        return self._get_bytes(90, 18)

    @property
    def descriptor4(self):
        return self._get_bytes(108, 18)

    def __repr__(self):
        cname = self.__class__.__name__
        return f'{cname}({self._edid!r})'
    

class EDIDParser(EDIDSegmenter):
    @property
    def manufacturer_id(self):
        alphabet = ' abcdefghijklmnopqrstuvwxyz'
        mid = super().manufacturer_id
        bits = bytes_to_bits(mid)
        bits = ''.join(bits)
        bits = bits[1:]         # remove header zero
        letters = [int(''.join(x), 2) for x in grouper(bits, 5)]
        letters = [alphabet[i] for i in letters]
        return ''.join(letters).upper()

    @property
    def manufacture_year(self):
        year = super().manufacture_year[0]
        return 1990 + year

    @property
    def edid_version(self):
        return super().edid_version[0]

    @property
    def edid_revision(self):
        return super().edid_revision[0]

    @property
    def horizontal_size(self):
        "Horizontal size in cm"
        return super().horizontal_size[0]

    @property
    def vertical_size(self):
        "Vertical size in cm"
        return super().vertical_size[0]

    @property
    def descriptor1(self):
        desc = parse_descriptor(super().descriptor1)
        return desc.strip()

    @property
    def descriptor2(self):
        desc = parse_descriptor(super().descriptor2)
        return desc.strip()

    @property
    def descriptor3(self):
        desc = parse_descriptor(super().descriptor3)
        return desc.strip()

    @property
    def descriptor4(self):
        desc = parse_descriptor(super().descriptor4)
        return desc.strip()


MonInfo = namedtuple('MonInfo', ('mfg', 'year', 'horizontal_size', 'vertical_size', 'descriptor'))

def monitor_info(edid_bytes):
    edp = EDIDParser(edid_bytes)
    desc = [edp.descriptor1, edp.descriptor2, edp.descriptor3, edp.descriptor4]
    desc = [x for x in desc if x]
    desc = '; '.join(desc)
    return MonInfo(
        edp.manufacturer_id,
        edp.manufacture_year,
        edp.horizontal_size,
        edp.vertical_size,
        desc,
    )


if __name__ == '__main__':
    import x11read
    EXAMPL_EDID = x11read.get_output_edid(i_screen=0)
    x = monitor_info(EXAMPL_EDID)
    print(x)
    
