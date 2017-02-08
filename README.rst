========
Overview
========

A library for reading and parsing Extended Display Identification Data.

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


