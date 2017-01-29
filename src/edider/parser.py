#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import struct
import sys
try:
    from itertools import zip_longest
except ImportError:             # for python2 compatibility
    from itertools import izip_longest as zip_longest
from collections import namedtuple
from builtins import bytes

def _grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def _bytes_to_bits(bstr):
    return ['{:08b}'.format(x) for x in bstr]

def _bytes_to_printable(bstr):
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
    if sys.version_info <= (3,0): # for python2 compatibility
        descr_type = ord(descr_type)

    rest = desc[5:]
    try:
        dtype = dtypes[descr_type]
    except KeyError:
        dtype = '{}'.format(descr_type)
    if dtype in text_dtypes:
        return EDIDDescriptor(dtype, _bytes_to_printable(rest))
    else:
        return EDIDDescriptor(dtype, None)


class EDIDSegmenter(object):
    "Expose the sections of an EDID object as properties of this class."
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
        return '{}({!r})'.format(cname, self._edid)
    

class EDIDParser(EDIDSegmenter):
    @property
    def manufacturer_id(self):
        alphabet = ' abcdefghijklmnopqrstuvwxyz'
        mid = super(EDIDParser, self).manufacturer_id
        bits = _bytes_to_bits(mid)
        bits = ''.join(bits)
        bits = bits[1:]         # remove header zero
        letters = [int(''.join(x), 2) for x in _grouper(bits, 5)]
        letters = [alphabet[i] for i in letters]
        return ''.join(letters).upper()

    @property
    def manufacture_year(self):
        year = super(EDIDParser, self).manufacture_year[0]
        return 1990 + year

    @property
    def manufacture_week(self):
        return super(EDIDParser, self).manufacture_week[0]

    @property
    def edid_version(self):
        return super(EDIDParser, self).edid_version[0]

    @property
    def edid_revision(self):
        return super(EDIDParser, self).edid_revision[0]

    @property
    def horizontal_size(self):
        "Horizontal size in cm"
        return super(EDIDParser, self).horizontal_size[0]

    @property
    def vertical_size(self):
        "Vertical size in cm"
        return super(EDIDParser, self).vertical_size[0]

    @property
    def descriptor1(self):
        return parse_descriptor(super(EDIDParser, self).descriptor1)

    @property
    def descriptor2(self):
        return parse_descriptor(super(EDIDParser, self).descriptor2)

    @property
    def descriptor3(self):
        return parse_descriptor(super(EDIDParser, self).descriptor3)

    @property
    def descriptor4(self):
        return parse_descriptor(super(EDIDParser, self).descriptor4)


class BaseMonitor(object):
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

    @property
    def uuid(self):
        try:
            return self._uuid
        except AttributeError:
            pass
        import hashlib
        import uuid
        md5 = hashlib.md5(self.edid).hexdigest()
        self._uuid = uuid.UUID(hex=md5)
        return self._uuid

    def __eq__(self, other):
        if hasattr(other, 'edid'):
            return self.edid == other.edid
        return False
        
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

    @property
    def text(self):
        desc = self._get_descriptors()
        try:
            return '; '.join([x.value for x in desc if x.dtype == 'text'])
        except IndexError:
            return ''

    def as_dict(self):
        import inspect
        fields = []
        for name, obj in inspect.getmembers(self.__class__):
            if (not name.startswith('_')) and inspect.isdatadescriptor(obj):
                fields.append(name)
        d = {}
        for key in fields:
            d[key] = getattr(self, key)
        return d

    def __repr__(self):
        cname = self.__class__.__name__
        return cname + '({})'.format(self._id)

    def __str__(self):
        rstr = repr(self)
        if self.name:
            rstr += '\t->\t{}'.format(self.name)
        return rstr

