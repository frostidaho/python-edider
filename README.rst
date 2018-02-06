========
Overview
========

A library for reading and parsing Extended Display Identification Data (EDID).
It supports python-3.x and python-2.7.

* Free software: BSD license

Example
=======
.. code:: python

    from edider import get_monitors
    
    for monitor in get_monitors():
        print(monitor)
        print(list(monitor.as_dict().keys()))

Installation
============

::

    git clone https://github.com/frostidaho/python-edider.git
    pip install --user ./python-edider


