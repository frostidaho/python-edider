from edider.x11read import *


with get_window(0) as win:
    x = randr.get_screen_resources(win)
    outs = x.outputs
    outs2 = []
    for out in outs:
        outs2.append(randr.get_output_info(win, out, 0))
        print(outs2[-1])
    
# win = get_window(0)
# win = win.__enter__()
