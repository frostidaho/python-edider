#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from edider import get_monitors


def print_attr(monitor, attr_name):
    print('\t', attr_name, '\t-> ', getattr(monitor, attr_name))

def print_monitor(m):
    print('\n', 60*'-', sep='')
    print(m)
    print_attr(m, 'geometry')
    print_attr(m, 'status')
    print_attr(m, 'is_primary')
    print_attr(m, 'manufacture_year')
    print_attr(m, 'manufacturer_id')
    print_attr(m, 'name')
    print_attr(m, 'text')
    print_attr(m, 'serial_no')
    print_attr(m, 'output_name')
    print_attr(m, 'width_in_cm')
    print_attr(m, 'height_in_cm')
    print(60*'-')


if __name__ == '__main__':
    monitors = get_monitors()
    for mon in monitors:
        print_monitor(mon)
