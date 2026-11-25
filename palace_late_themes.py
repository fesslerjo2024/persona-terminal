"""Read-only route maps for Mementos Depths and the Laboratory."""
from battle_ui import CYAN, DIM, GREEN, RED, WHITE
from reel_palette import IDS

_NAVY = IDS['navy']
_SLATE = IDS['slate']
_TEAL = IDS['teal']
_WINE = IDS['wine']
_ROSE = IDS['rose']

# Each schematic is original Unicode art. It changes when an accessible stop
# becomes selected, but a locked stop cannot preview a later route or room.
_DEPTHS = (
    (
        '╔═╦═══════════╦═╗',
        '║ ║  ╔━━━━━╗  ║ ║',
        '╠═◎━━◎━━━━━◎━━◎═╣',
        '║ ║  ╚╗   ╔╝  ║ ║',
        '║ ╚╗  ╚═╦═╝  ╔╝ ║',
        '║  ╚═◎══◎══◎═╝  ║',
        '║       ║       ║',
        '╚═══════╬═══════╝',
        '        ║        ',
        '        ╵        ',
    ),
    (
        '     ║     ║     ',
        '     ╚═◎═══╝     ',
        '   ┏━━━━┻━━━━┓   ',
        '   ┃ ║ ║ ║ ║ ┃   ',
        ' ╔═╩═╩═╩═╩═╩═╩═╗ ',
        ' ║ ╔════╦════╗ ║ ',
        ' ╚═╣    ║    ╠═╝ ',
        '   ║ ┌──╨──┐ ║   ',
        '   ║ │  │  │ ║   ',
        '   ╨ └──┴──┘ ╨   ',
    ),
    (
        '╔═══════╦═══════╗',
        '║   01  ║  02   ║',
        '║ ║║║║│ ║ │║║║║ ║',
        '╠═══════╬═══════╣',
        '║   03  ║  04   ║',
        '║ ║║║║│ ║ │║║║║ ║',
        '╠═══════╬═══════╣',
        '║   05  ║  06   ║',
        '║ ║║║║│ ║ │║║║║ ║',
        '╚═══════╩═══════╝',
    ),
    (
        ' ╔═════════════╗ ',
        ' ║ ║ ║ ║ ║ ║ ║ ║ ',
        ' ╠═════════════╣ ',
        ' ║ │  │   │  │ ║ ',
        ' ╚═╤══╡   ╞══╤═╝ ',
        '   │  ╵   ╵  │   ',
        '   │   ╷ ╷   │   ',
        '   └───┼─┼───┘   ',
        '       ║ ║       ',
        '       ║ ║       ',
    ),
    (
        '          ╔╗     ',
        '      ╔╗  ║╠═╗   ',
        '      ║╠══╝║▓║   ',
        '   ╔╗ ║║▓╔═╣▓║   ',
        '   ║╠═╝╚═╝ ╚═╝   ',
        '   ║║▓   ╔╗      ',
        ' ╔═╝╚════╝║      ',
        ' ║▓▓    ▒▒║      ',
        ' ╚════════╝      ',
        '        ░        ',
    ),
)

_DEPTH_LAST = 5

_LAB = (
    (
        '┌───────────────┐',
        '│ ╭─╮ ┌─┬─┬─┐   │',
        '│ │+│ ├─┼─┼─┤   │',
        '│ ╰─╯ └─┴─┴─┘   │',
        '├────┬──────────┤',
        '│    │  ╭─────╮ │',
        '│ ○  └──┤ ·ᴗ· │ │',
        '│       ╰─────╯ │',
        '│ ───────────── │',
        '└───────────────┘',
    ),
    (
        '┌───────────────┐',
        '│ ┌───────────┐ │',
        '│ │░░░███░░░░░│ │',
        '│ │███░░░███░░│ │',
        '│ └─────┬─────┘ │',
        '│       │       │',
        '├──┬────┴────┬──┤',
        '│  ╵    │    ╵  │',
        '│       ╵       │',
        '└───────────────┘',
    ),
    (
        '┌───────────────┐',
        '│ ╭┐ ╭┐ ╭┐ ╭┐   │',
        '│ ││ ││ ││ ││   │',
        '│ ╰┘ ╰┘ ╰┘ ╰┘   │',
        '├───────────────┤',
        '│ ◆──────────   │',
        '│ ────██████─   │',
        '│ ───────────   │',
        '│ ─██████████   │',
        '└───────────────┘',
    ),
    (
        '┌───────────────┐',
        '│       ○       │',
        '│      ╱│╲      │',
        '│  ○──●─●─●──○  │',
        '│       │       │',
        '├───────┴───────┤',
        '│   □  □  □     │',
        '│   ■  ■  ■     │',
        '│   □  □  □     │',
        '└───────────────┘',
    ),
    (
        '┌───────────────┐',
        '│        ╱━━━━╮ │',
        '│  ╭━━━━┿━╮   ┃ │',
        '│  ┃   ╱  ┃   ┃ │',
        '│  ┃  ╱   ┃   ╵ │',
        '│  ╰━┿━━━━┿━━╮  │',
        '│   ╱     ┃  ┃  │',
        '│  ╵      ╵  ┃  │',
        '│            ╵  │',
        '└───────────────┘',
    ),
    (
        '┌───────────────┐',
        '│     ╲   ╱     │',
        '│   ╲  ╭─╮  ╱   │',
        '│  ────┤●├────  │',
        '│   ╱  ╰─╯  ╲   │',
        '│     ╱   ╲     │',
        '├───────────────┤',
        '│  ○         ■  │',
        '│  │         │  │',
        '└──╨─────────╨──┘',
    ),
)


def _paint(app, y, x, width, line, color, bold=False, reverse=False):
    if width > 0 and 6 <= y <= app.h - 8 and 0 <= x < app.w - 1:
        app.put(y, x, line[:min(width, app.w - 1 - x)], color, bold, reverse)


def _stage(view):
    """Track the selection without revealing artwork for an inaccessible stop."""
    selected = min(max(0, view.selected), len(view.rows) - 1)
    return max((i for i in range(selected + 1)
                if view.rows[i].status != 'locked'), default=0)


def _geometry(app, rows, depth=False):
    # Keep the largest route label, marker and earned grade entirely readable.
    label = max((len(r.title) for r in rows), default=29) + 10
    # Reserve space for a medal even before one is earned, so the art
    # does not shift sideways on the next visit.
    art_x = max(40, label + (5 if depth else 6))
    if not depth:
        art_x = max(art_x, app.w // 2)
    art = app.w - 3 - art_x
    span = app.h - 15
    step = min(5 if depth else 4, max(1, span // max(1, len(rows) - 1)))
    return art_x, art, step


def _widen(pattern, width):
    """Stretch flat rails and voids, never posts, numbered cells or junctions."""
    original = len(pattern[0])
    if width <= original:
        return pattern
    flat = ' ═━─░▒▓'
    lanes = [i for i in range(1, original - 1)
             if all(row[i] in flat for row in pattern)]
    if not lanes:
        return tuple(row.center(width) for row in pattern)
    rails = [i for i in lanes if any(row[i] != ' ' for row in pattern)] or lanes
    count, remaining = divmod(width - original, len(rails))
    repeats = {col: count + (j < remaining) for j, col in enumerate(rails)}
    return tuple(''.join(c * (1 + repeats.get(i, 0)) for i, c in enumerate(row))
                 for row in pattern)


def _depth_pattern(stage, w, h):
    if stage == _DEPTH_LAST:
        # Draw the broken terminus on the full width; the falling right-hand
        # sequence must keep its diagonal, not move off with repeated cells.
        middle = max(5, (w - 11) // 2)
        further = max(3, w - middle - 9)
        end = middle + further + 7
        return (
            '╔══╦' + '═' * middle + '╦' + '═' * further + '╗',
            '╚══◎' + '━' * middle + '◎' + '━' * further + '╩╲',
            ' ' * end + '╲',
            ' ' * (end + 1) + '·',
        )
    pattern = _widen(_DEPTHS[stage], w)
    if h <= len(pattern):
        return pattern
    # Only vertical portions are repeated. Horizontal paths and cell numbers
    # occur once even with half a screen of extra height.
    stretch = (
        (1, 6, 8),
        (0, 3, 8),
        (2, 5, 8),
        (1, 3, 8),
        (2, 5, 7),
    )[stage]
    count, remainder = divmod(h - len(pattern), len(stretch))
    lines = []
    for i, row in enumerate(pattern):
        lines.append(row)
        if i in stretch:
            vertical = ''.join(c if c in '║┃│╎┆┋▓▒░' else
                               '║' if c in '╔╗╚╝╬╦╠╣╩' else ' '
                               for c in row)
            lines.extend([vertical] * (count + (stretch.index(i) < remainder)))
    return lines


def _depth_art(app, x, width, stage):
    height = app.h - 14
    pattern = _depth_pattern(stage, width, height)
    base = _SLATE if stage >= 2 else _TEAL
    accent = RED if stage >= 3 else _WINE if stage == 2 else _TEAL
    for j, line in enumerate(pattern):
        is_rail = any(c in line for c in '◎╬╩0123456')
        _paint(app, 6 + j, x, width, line, accent if is_rail else base, is_rail)


def _lab_art(app, x, width, stage):
    pattern = _widen(_LAB[stage], min(width, 31))
    start = x + (width - len(pattern[0])) // 2
    top = 6 + max(0, (app.h - 13 - len(pattern)) // 2)
    for i, line in enumerate(pattern):
        # A white luminous instrument face gives way to darker evidence
        # rather than changing the underlying wording or choices.
        light = stage < 2 or i < 5
        color = WHITE if light else _ROSE if stage >= 3 else CYAN
        _paint(app, top + i, start, width, line, color, light, light)


def _label(row, index):
    mark = {'locked': '▣', 'clear': '✓', 'open': '◆'}[row.status]
    point = '▶' if row.selected else ' '
    suffix = f' [{row.medal}]' if row.medal else ''
    return f'{point}{index + 1:02} {mark} {row.title}{suffix}'


def _depth_rows(app, view, width, step, stage):
    accent = RED if stage == _DEPTH_LAST else _WINE if stage >= 2 else _TEAL
    for i, row in enumerate(view.rows):
        color = (DIM if row.status == 'locked' else accent if row.selected else
                 GREEN if row.status == 'clear' else WHITE)
        last = i == len(view.rows) - 1
        pos = 6 + i * step
        rail = '║' if i <= stage else '╎'
        station = ' ' if last and stage == i else '╵' if last else '◎' if i <= stage else '○'
        _paint(app, pos, 3, 1, station, accent if i <= stage else DIM, row.selected)
        _paint(app, pos, 4, width - 1, _label(row, i), color, row.selected, row.selected)
        if not last:
            for gap in range(1, step):
                _paint(app, pos + gap, 3, 1, rail, accent if i < stage else DIM)


def _lab_cards(app, view, width, step, stage):
    for i, row in enumerate(view.rows):
        pos = 6 + i * step
        locked = row.status == 'locked'
        # Keep gated cards unaltered. Looking at an inaccessible operation
        # cannot expose evidence or change a past card's appearance.
        compromised = stage >= 2 and i <= stage and not locked
        severity = min(stage - 1, 4) if compromised else 0
        frame = _ROSE if severity >= 3 else _TEAL if compromised else _NAVY
        color = DIM if locked else WHITE if row.selected else GREEN if row.status == 'clear' and not compromised else WHITE
        label = _label(row, i)
        card = label.ljust(width - 2)
        edge = '╎' if locked else '╱' if severity >= 3 else '┤' if compromised else '│'
        other = '╎' if locked else '╲' if severity >= 3 else '┐' if compromised else '│'
        _paint(app, pos, 3, 1, edge, frame, row.selected)
        _paint(app, pos, 4, width - 2, card, color, row.selected, row.selected or not locked and not compromised)
        _paint(app, pos, 3 + width - 1, 1, other, frame, row.selected)
        if step > 1:
            seam = '┄' if locked else '╌' if compromised else '─'
            length = width - 2
            if severity >= 2:
                first, end = length // 5 + (i * 2) % (length // 3), length * 4 // 5
                seam = seam * first + '▒' * (severity + 1) + seam * (end - first - severity - 1) + ' ' * (length - end)
            else:
                seam *= length
            _paint(app, pos + 1, 4, length, seam, frame)


def draw_depths(app, view):
    if not view.rows:
        return
    stage = min(_stage(view), _DEPTH_LAST)
    x, width, step = _geometry(app, view.rows, True)
    _depth_rows(app, view, x - 4, step, stage)
    _depth_art(app, x, width, stage)


def draw_laboratory(app, view):
    if not view.rows:
        return
    stage = min(_stage(view), len(_LAB) - 1)
    x, width, step = _geometry(app, view.rows)
    _lab_cards(app, view, x - 4, step, stage)
    _lab_art(app, x, width, stage)


THEMES = {'depths': draw_depths, 'laboratory': draw_laboratory}
