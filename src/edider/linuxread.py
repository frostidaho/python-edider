from glob import glob
from os import path

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

from edider.parser import BaseScreen
class LinuxScreen(BaseScreen):
    def __init__(self, path):
        self._id = path
        self._path = path

    @property
    def edid(self):
        try:
            return self._edid
        except AttributeError:
            self._edid = read_bin(path.join(self._path, 'edid'))
            return self._edid
        
    def _get_resolution(self):
        with open(path.join(self._path, 'modes'), mode='rt') as modes:
            mode = modes.readline()
        x,y = mode.strip().split('x')
        self._width_in_pixels, self._height_in_pixels = int(x), int(y)

    @property
    def output_name(self):
        try:
            return self._output_name
        except AttributeError:
            name = path.basename(self._path)
            self._output_name = name.split('-', maxsplit=1)[-1]
            return self._output_name



if __name__ == '__main__':
    for output in get_connected():
        print('Output: ', output)
        s = LinuxScreen(output)
        print('\tEDID', s.edid)
