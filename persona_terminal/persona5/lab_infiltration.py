"""Three temporary, independently playable Laboratory rooms."""
from dataclasses import dataclass

from .battle_ui import CYAN, DIM, GOLD, GREEN, RED, WHITE, ENTER, ESC
from . import persona5_story_art as art

_ARCHIVE = (
    ('Open the pilot transcript',
     'A patient remembers a friend’s hand on her shoulder. She can no longer remember why she was crying, or why she had asked the friend to stay. The interview is stamped “SUCCESS”.'),
    ('Open the consent form',
     'The field for the patient’s signature has been left blank. Under it, a later stamp reads “AUTHORIZATION NOT REQUIRED”.'),
)
_CONSULTATION = (
    'Remove the memory of the recital.',
    'Let her decide how to live with it.',
)
_ENTRY = {
    'archive': 'SEARCH ARCHIVE',
    'consult': 'ENTER CONSULTATION',
    'bridge': 'CHECK THE BRIDGE',
}


def entry_label(room):
    return _ENTRY[room]


@dataclass
class LabInfiltration:
    node_id: str
    room: str
    pick: int = 0
    record: int | None = None
    approved: bool | None = None
    blue: bool = False
    warning: str = ''

    def key(self, app, key):
        if key == ESC:
            if self.room == 'archive' and self.record is not None:
                self.record = None
            else:
                return 'back'
            return None
        if (self.room == 'archive' and self.record is not None
                or self.room == 'consult' and self.approved is not None):
            return 'deploy' if key in ENTER else None
        self.pick = app.nav(key, self.pick, 2)
        choice = app.commit(key, self.pick, 2)
        if choice is None:
            return None
        self.pick = choice
        if self.room == 'archive':
            self.record = choice
        elif self.room == 'consult':
            self.approved = choice == 0
        elif choice == 0:
            self.blue = not self.blue
            self.warning = ''
        elif self.blue:
            return 'deploy'
        else:
            self.warning = 'The red span ends at a closed ward. Stay on this side.'
        return None

    def prepare(self, battle):
        if self.room == 'consult':
            if self.approved:
                for thief in battle.allies:
                    thief.buffs['defense'] = (1, 1)
                # The initiative is already sitting on its first action; count
                # it as that actor's covered turn, just like later slots.
                battle._slot_effects['defense'] = battle.actor.buffs['defense']
                battle._say('Consultation cover: the crew begins with defense up for one turn.')
            else:
                battle._say('The crew enters through the maintenance hatch, without cover.')
        elif self.room == 'bridge':
            battle._say('The blue bridge carries the crew to the Eden patrol.')
        else:
            battle._say('Oracle opens the archive door. The research wing patrol is ahead.')

    def draw(self, app):
        if self.room == 'archive':
            self._draw_archive(app)
        elif self.room == 'consult':
            self._draw_consult(app)
        else:
            self._draw_bridge(app)

    def _draw_archive(self, app):
        if self.record is None:
            app.panel('LABORATORY / ARCHIVE', 'PATIENT RECORDS', '↑↓ PICK  ↵ OPEN  ESC BACK')
            app.lines(7, 3, 'Two pages sit open behind the glass. Oracle can read either while she releases the lock.',
                      limit=2, color=DIM)
            app._b_list([(name, '', True) for name, _ in _ARCHIVE],
                        11, 3, app.w-6, 2, self.pick)
            return
        name, note = _ARCHIVE[self.record]
        app.panel('LABORATORY / ARCHIVE', name.removeprefix('Open the ').upper(),
                  '↵ THROUGH THE ARCHIVE  ESC OTHER RECORD')
        app.lines(8, 3, note, limit=5, color=WHITE)
        app.lines(15, 3, 'The security latch clicks. Footsteps pass the far door.', limit=2, color=DIM)

    def _draw_consult(self, app):
        if self.approved is None:
            app.panel('LABORATORY / CONSULTATION', 'RECOMMEND A TREATMENT',
                      '↑↓ ANSWER  ↵ SUBMIT  ESC BACK')
            app.lines(7, 3, 'A pianist hurt her hand at a recital. Remembering the song hurts, but she still wants to play it. What do you recommend?',
                      limit=4, color=WHITE)
            app._b_list([(answer, '', True) for answer in _CONSULTATION], 13, 3, app.w-6, 2, self.pick)
            return
        approved = self.approved
        app.panel('LABORATORY / CONSULTATION', 'TREATMENT ACCEPTED' if approved else 'TREATMENT REJECTED',
                  ('↵ MAIN PASSAGE' if approved else '↵ MAINTENANCE HATCH')+'  ESC BACK')
        answer = ('Distress removed. Please proceed through the protected passage.'
                  if approved else 'Distress may persist. Access through the main passage is denied.')
        app.lines(8, 3, answer, limit=2, color=GREEN if approved else RED)
        route = ('Oracle: The passage’s barrier can cover us for one turn.'
                 if approved else 'Oracle: There’s a maintenance hatch. Same destination, no cover.')
        app.lines(13, 3, route, limit=3, color=WHITE)

    def _draw_bridge(self, app):
        app.panel('LABORATORY / TWILIGHT CORRIDOR', 'BRIDGE SWITCH',
                  '↑↓ PICK  ↵ ACT  ESC BACK')
        art.draw(app,art.lab_bridge,15,6,app.w-29,4,blue=self.blue)
        app.put(8,3,'CLOSED WARD',DIM if self.blue else RED,True)
        app.put(8,app.w-9,'EDEN',CYAN if self.blue else DIM,True)
        app.mid(10,'ENTRY',WHITE,True)
        state = 'Blue span leads to Eden.' if self.blue else 'Red span leads to the closed ward.'
        app.lines(11, 3, state, limit=2, color=WHITE)
        options = (('Throw the color switch', '', True), ('Cross the bridge', '', True))
        app._b_list(options, 14, 3, app.w-6, 2, self.pick)
        if self.warning:
            app.lines(18, 3, self.warning, limit=2, color=GOLD)
