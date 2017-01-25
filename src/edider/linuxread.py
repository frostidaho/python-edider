from glob import glob
from os import path
import os
# edid_file = '/sys/devices/pci0000:00/0000:00:02.0/drm/card0/card0-VGA-1/edid'

# edid_files = glob('/sys/class/drm/card*/edid')
# edid_files = glob('/sys/class/drm/card0/*/edid')



def read_bin(file_path):
    # with open(file_path, mode='rb') as f:
    #     lines = f.readlines()
    with open(file_path, mode='rb') as f:
        lines = f.read()
    return lines


def get_connected():
    outputs = glob('/sys/class/drm/card*/status')
    connected = (read_bin(x).decode().strip() for x in outputs)
    for output, status in zip(outputs, connected):
        if status == 'connected':
            yield path.dirname(output)

from edider import Screen
class LinuxScreen(Screen):
    def __init__(self, path):
        self._path = path

    @property
    def edid(self):
        try:
            return self._edid
        except AttributeError:
            self._edid = read_bin(path.join(self._path, 'edid'))
            return self._edid
        

    def _set_resolution(self):
        with open(path.join(self._path, 'modes'), mode='rt') as modes:
            mode = modes.readline()
        x,y = mode.split('x')
        self._width_in_pixels, self._height_in_pixels = x, y

    def __repr__(self):
        cname = self.__class__.__name__
        return cname + '({})'.format(self._path)

    def __str__(self):
        cname = self.__class__.__name__
        return cname + '({})'.format(self._path)




for output in get_connected():
    print('Output: ', output)
    s = LinuxScreen(output)
    print('\tEDID', s.edid)


