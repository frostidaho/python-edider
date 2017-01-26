#!/usr/bin/env python3

from itertools import zip_longest
import string
import struct
from collections import namedtuple

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def bytes_to_bits(bstr):
    return ['{:08b}'.format(x) for x in bstr]

def bytes_to_printable(bstr):
    bstr = bstr.decode('ascii', errors='ignore')
    out = ''.join([x for x in bstr if x in string.printable])
    return out.strip()


EDIDDescriptor = namedtuple('EDIDDescriptor', ('dtype', 'value'))
def parse_descriptor(desc):
    # Take a look at the following page
    # for the descriptor spec
    # https://en.wikipedia.org/wiki/Extended_Display_Identification_Data
    dtypes = {
        255: 'serial_no',
        254: 'text',
        253: 'mon_range_lim',
        252: 'name',
        251: 'white_pt_data',
        250: 'std_timing',
    }
    text_dtypes = ('serial_no', 'text', 'name')

    if desc[0] != 0:
        return EDIDDescriptor('detailed_timing', None)
    header = struct.unpack('5c', desc[0:5])
    descr_type = header[3][0]

    rest = desc[5:]
    dtype = dtypes[descr_type]
    if dtype in text_dtypes:
        return EDIDDescriptor(dtype, bytes_to_printable(rest))
    else:
        return EDIDDescriptor(dtype, None)


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
        return desc

    @property
    def descriptor2(self):
        desc = parse_descriptor(super().descriptor2)
        return desc

    @property
    def descriptor3(self):
        desc = parse_descriptor(super().descriptor3)
        return desc

    @property
    def descriptor4(self):
        desc = parse_descriptor(super().descriptor4)
        return desc


class BaseScreen(object):
    "An abstract class for showing information about connected screens"
    def __init__(self, identifier):
        self._id = identifier

    @property
    def edid(self):
        try:
            return self._edid
        except AttributeError:
            edid = self._get_output_edid()
            self._edid = edid
            return edid

    def _get_output_edid(self):
        raise NotImplementedError

    def _dflt_resolution(self):
        "Set self._width_in_pixels & self._height_in_pixels"
        raise NotImplementedError

    @property
    def height_in_pixels(self):
        try:
            return self._height_in_pixels
        except AttributeError:
            self._dflt_resolution()
            return self._height_in_pixels

    @property
    def width_in_pixels(self):
        try:
            return self._width_in_pixels
        except AttributeError:
            self._dflt_resolution()
            return self._width_in_pixels

    @property
    def manufacturer_id(self):
        return EDIDParser(self.edid).manufacturer_id

    @property
    def manufacture_year(self):
        return EDIDParser(self.edid).manufacture_year

    @property
    def width_in_cm(self):
        return EDIDParser(self.edid).horizontal_size

    @property
    def height_in_cm(self):
        return EDIDParser(self.edid).vertical_size

    @property
    def output_name(self):
        raise NotImplementedError

    def _get_descriptors(self):
        try:
            return self._descriptors
        except AttributeError:
            edp = EDIDParser(self.edid)
            self._descriptors = [
                edp.descriptor1,
                edp.descriptor2,
                edp.descriptor3,
                edp.descriptor4,
            ]
            return self._descriptors

    @property
    def name(self):
        desc = self._get_descriptors()
        try:
            return [x.value for x in desc if x.dtype == 'name'][0]
        except IndexError:
            return ''

    @property
    def serial_no(self):
        desc = self._get_descriptors()
        try:
            return [x.value for x in desc if x.dtype == 'serial_no'][0]
        except IndexError:
            return ''


    def __repr__(self):
        cname = self.__class__.__name__
        return cname + '({})'.format(self._id)

    def __str__(self):
        cname = self.__class__.__name__
        return cname + '({})'.format(self._id)



if __name__ == '__main__':
    from collections import namedtuple
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

    
    from edider import x11read
    EXAMPL_EDID = x11read.get_output_edid(i_screen=0)
    x = monitor_info(EXAMPL_EDID)
    print(x)
    

