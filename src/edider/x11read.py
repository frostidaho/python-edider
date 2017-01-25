#!/usr/bin/env python3
from Xlib import X, display, Xatom
from Xlib.ext import randr

from contextlib import contextmanager

@contextmanager
def get_window(i_screen=0):
    "Create & manage a x-window."
    screen = display.Display().screen(i_screen)
    window = screen.root.create_window(0, 0, 1, 1, 1, screen.root_depth)
    yield window
    window.destroy()

def get_output_id(window):
    "Return the primary output (int) for a given x-window"
    primary_out = randr.get_output_primary(window)
    primary_out = primary_out.output
    return primary_out

def get_output_edid(i_screen=0):
    "Return the raw EDID for a given screen."
    PROPERTY_EDID = display.Display().intern_atom('EDID', only_if_exists=True)
    with get_window(i_screen) as window:
        outp = get_output_id(window)
        # props = randr.list_output_properties(window, outp)
        edid = randr.get_output_property(window, outp, PROPERTY_EDID,
                                         Xatom.INTEGER, 0, 400)
        edid = bytes(edid.value)
    return edid

def get_screen_resolution(i_screen=0):
    scr = display.Display().screen(i_screen)
    return scr.width_in_pixels, scr.height_in_pixels

if __name__ == '__main__':
    for i in range(display.Display().screen_count()):
        edid = get_output_edid(i)
        print('Screen {}'.format(i))
        print(edid)

