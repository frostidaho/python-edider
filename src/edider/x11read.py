#!/usr/bin/env python3
from Xlib import X, display, Xatom
from Xlib.ext import randr
from edider.parser import BaseScreen
from contextlib import contextmanager
from collections import namedtuple

OutputInfo = namedtuple('OutputInfo', ('edid', 'name', 'props'))

@contextmanager
def get_window(i_screen=0):
    "Create & manage a x-window."
    screen = display.Display().screen(i_screen)
    window = screen.root.create_window(0, 0, 1, 1, 1, screen.root_depth)
    yield window
    window.destroy()

def get_connected_outputs(i_screen=0):
    "Yield the X11-index for each connected monitor"
    with get_window(i_screen) as window:
        res = randr.get_screen_resources(window)
        outputs = res.outputs
        for output in outputs:
            info = randr.get_output_info(window, output, 0)
            if info.connection == 0:
                yield output

CRTCInfo = namedtuple('CRTCInfo', ('idx', 'info'))
def crtc_info(*crtc_idx):
    with get_window() as win:
        for idx in crtc_idx:
            info = randr.get_crtc_info(win, idx, 0)._data
            yield CRTCInfo(idx, info)

class X11Output:
    def __init__(self, idx):
        self.idx = idx

    @property
    def edid(self):
        try:
            return self._edid
        except AttributeError:
            pass
        PROPERTY_EDID = display.Display().intern_atom('EDID', only_if_exists=True)
        with get_window() as win:
            edid = randr.get_output_property(
                win,
                self.idx,
                PROPERTY_EDID,
                Xatom.INTEGER,
                0,
                400,
            )
            edid = bytes(edid.value)
            self._edid = edid
        return self._edid

    @property
    def info(self):
        try:
            return self._info
        except AttributeError:
            pass
        with get_window() as win:
            self._info = randr.get_output_info(win, self.idx, 0)._data
        return self._info

    @property
    def name(self):
        return self.info['name']

    @property
    def crtc(self):
        return next(crtc_info(self.info['crtc']))

    @property
    def crtcs(self):
        return list(crtc_info(*self.info['crtcs']))

    def _get_modes(self):
        with get_window() as win:
            res = randr.get_screen_resources(win)
            modes = res._data['modes']
            modes = [x._data for x in modes]
            return modes

    @property
    def modes(self):
        return self._get_modes()

    @property
    def mode(self):
        modes = self._get_modes()
        mode_id = self.crtc.info['mode']
        modes = [x for x in modes if x['id'] == mode_id]
        return modes[0]

# def get_output_info(*output_ids, i_screen=0):
#     "Return the raw EDID for a given screen."
#     PROPERTY_EDID = display.Display().intern_atom('EDID', only_if_exists=True)
#     with get_window(i_screen) as window:
#         for outp in output_ids:
#             # props = randr.list_output_properties(window, outp)
#             props = randr.get_output_info(window, outp, 0)
#             edid = randr.get_output_property(window, outp, PROPERTY_EDID,
#                                              Xatom.INTEGER, 0, 400)
#             edid = bytes(edid.value)
#             yield OutputInfo(
#                 edid=edid,
#                 props=props,
#                 name=props.name,
#             )
#             # yield edid, props

# def get_screen_resolution(i_screen=0):
#     scr = display.Display().screen(i_screen)
#     return scr.width_in_pixels, scr.height_in_pixels

# class X11Screen(BaseScreen):
#     def __init__(self, index=0):
#         """Index is the X11 index of the screen"""
#         self._id = index

#     @property
#     def edid(self):
#         try:
#             return self._edid
#         except AttributeError:
#             self._edid = get_output_edid(self._id)
#             return self._edid
        
#     # def _get_resolution(self):
#     #     x,y = get_screen_resolution(self._id)
#     #     self._width_in_pixels, self._height_in_pixels = int(x), int(y)


if __name__ == '__main__':
    xos = [X11Output(x) for x in get_connected_outputs()]
    xo = xos[0]
    xo1 = xos[1]

    # win = get_window()
    # win = win.__enter__()

