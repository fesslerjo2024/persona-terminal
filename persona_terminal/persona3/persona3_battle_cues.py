"""Brief, scene-local battle readouts; the battle log remains the history."""
from dataclasses import dataclass

HOLD_SECONDS = .60
BADGES = {'WEAK': 'W', 'RESIST': 'R', 'DOWN': '↓', 'CRIT': '!', 'GUARD': 'G',
          'REPEL': 'P', 'DRAIN': 'D', 'NULL': 'N'}


@dataclass(frozen=True)
class BattleCue:
    delta: int
    tags: tuple = ()

    def combine(self, delta, tags):
        return BattleCue(self.delta + delta, tuple(dict.fromkeys((*self.tags, *tags))))

    def labels(self, resource):
        amount = f'{"−" if self.delta < 0 else "+"}{abs(self.delta)}' if self.delta else ''
        full = ' · '.join(filter(None, (f'{amount} {resource}' if amount else '', *self.tags)))
        short = ' '.join(filter(None, (amount, *self.tags)))
        compact = ' '.join(filter(None, (amount, ''.join(BADGES.get(t, t) for t in self.tags))))
        return tuple(dict.fromkeys((full, short, compact, amount or compact)))


class BattleCues:
    def __init__(self):
        self.effects = {}
        self.expires = 0.

    def publish(self, effects, now):
        self.effects = dict(effects)
        self.expires = now + HOLD_SECONDS

    def get(self, key, now):
        return self.effects.get(key) if now < self.expires else None
