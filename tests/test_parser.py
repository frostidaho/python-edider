# -*- coding: utf-8 -*-
import os
import unittest
from edider.parser import (EDIDSegmenter, EDIDParser)
from builtins import bytes
try:
    testdir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    testdir = os.getcwd()

def get_example_edid(name):
    path = os.path.join(testdir, 'data', name)
    with open(path, mode='rb') as edid_bin:
        return bytes(edid_bin.read())

class TestSegmenter(unittest.TestCase):
    def test_header(self):
        eds = EDIDSegmenter(get_example_edid('edid2.bin'))
        FIXED_HEADER = b'\x00\xff\xff\xff\xff\xff\xff\x00'
        self.assertEqual(eds.fixed_header, FIXED_HEADER)

    def test_version(self):
        eds = EDIDSegmenter(get_example_edid('edid2.bin'))
        self.assertEqual(eds.edid_version[0], 1)
        self.assertEqual(eds.edid_revision[0], 3)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.edp = EDIDParser(get_example_edid('edid2.bin'))

    def test_mfg_id(self):
        self.assertEqual(self.edp.manufacturer_id, 'TSB')

    def test_mfg_year(self):
        self.assertEqual(self.edp.manufacture_year, 2009)

    def test_mfg_week(self):
        self.assertEqual(self.edp.manufacture_week, 255)

    def test_horizontal_size(self):
        # in cm
        self.assertEqual(self.edp.horizontal_size, 89)

    def test_vertical_size(self):
        # in cm
        self.assertEqual(self.edp.vertical_size, 50)

    def test_version(self):
        self.assertEqual(self.edp.edid_version, 1)
        self.assertEqual(self.edp.edid_revision, 3)

    def test_descriptor_name(self):
        d3 = self.edp.descriptor3
        self.assertEqual(d3.dtype, 'name')
        self.assertEqual(d3.value, 'TOSHIBA-TV')

# edp = EDIDParser(get_example_edid('edid2.bin'))
# eds = EDIDSegmenter(get_example_edid('edid2.bin'))

