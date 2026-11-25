"""Additional scene pigments. Keep IDs 1–6 stable for campaign menus."""
import curses as C

PIGMENTS = {
    'rose':   (212, C.COLOR_MAGENTA),
    'amber':  (215, C.COLOR_YELLOW),
    'violet': (141, C.COLOR_MAGENTA),
    'teal':   (44, C.COLOR_CYAN),
    'navy':   (68, C.COLOR_BLUE),
    'forest': (70, C.COLOR_GREEN),
    'ochre':  (172, C.COLOR_YELLOW),
    'wine':   (132, C.COLOR_MAGENTA),
    'slate':  (103, C.COLOR_BLUE),
}
IDS = {name:i for i,name in enumerate(PIGMENTS,7)}


def install(background):
    for name,(xterm,classic) in PIGMENTS.items():
        C.init_pair(IDS[name],xterm if C.COLORS>=256 else classic,background)
