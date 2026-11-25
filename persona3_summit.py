"""Adamah approach and Makoto's solo passage to Nyx.

The approach compresses 257–258F, before the 259F rematch. The post-Avatar
section follows the solo Nyx Core staging and returning voices, with original
words and explicit turn choices: https://www.youtube.com/watch?v=gdjUjOI8aTE
(17:12, 21:49, 1:33:08–1:34:40).
"""
from dataclasses import dataclass

from persona3_scenic_detail import summit_ascent as ascent_art, summit_seal as seal_art

ADAMAH_PHASE='summit-adamah'
SEAL_PHASE='great-seal'
APPROACH='adamah-approach'
SUMMIT_LEVEL=17
SUMMIT_SUPPLIES={'Medicine':6,'Soul Drop':5,'Revival Bead':3,'Dis-Charm':3}


@dataclass
class Ascent:
    step:int=0
    cache:bool=False

    @property
    def floor(self):
        return (257,258)[self.step]

    def supplies(self):
        pack=dict(SUMMIT_SUPPLIES)
        if self.cache:
            pack['Medicine']+=2
            pack['Soul Drop']+=2
        return pack


@dataclass
class SoloSeal:
    hp:int=100
    beat:int=0
    outcome:str=''

    @property
    def choices(self):
        if self.outcome=='loss':return ('Retry at the threshold',)
        if self.beat==2:return ('Great Seal',)
        return ('Guard', 'Step into the pressure')

    @property
    def copy(self):
        if self.outcome=='loss':
            return 'The Fall swallowed the path. The summit is behind you; retry here.'
        return (
            'You defeated Nyx’s Avatar, not Nyx. Your bonds unlock the Universe, a power that lets Makoto reach Nyx alone. Guard against the first wave.',
            'Your friends’ voices steady you, and the Universe holds. Guard through the second wave to get close enough to stop Nyx.',
            'Your friends’ voices make one last opening. Use the Great Seal to keep Nyx from reaching humanity.',
        )[self.beat]

    def choose(self,index):
        if self.outcome or not 0<=index<len(self.choices):return
        if self.beat==2:
            self.outcome='win'
            return
        # One early step can survive; two careless steps cannot. The bonds
        # sustain Makoto once, but never auto-seal or depend on unlocked links.
        self.hp=max(0,self.hp-((30,36)[self.beat] if index==0 else 63))
        if not self.hp:
            self.outcome='loss'
            return
        if self.beat==0:self.hp=min(100,self.hp+13)
        self.beat+=1

