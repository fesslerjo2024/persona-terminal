"""Late field, encounter, and fusion registries shared by campaign and combat."""
from . import persona3_autumn
from . import persona3_winter
from . import persona3_autumn_combat
from . import persona3_winter_combat
from . import persona3_autumn_operations
from . import persona3_nyx_combat

FIELD_MODULES=(persona3_autumn,persona3_winter)
TACTICS_MODULES=(persona3_autumn_combat,persona3_winter_combat)
CYCLE_MODULES=(persona3_autumn_operations,persona3_nyx_combat)

def combined(modules,attr):
    return {key:value for module in modules for key,value in getattr(module,attr,{}).items()}

BLOCKS=combined(FIELD_MODULES,'BLOCKS')
NAMES=combined(FIELD_MODULES,'NAMES')
OPENS=combined(FIELD_MODULES,'OPENS')
REPLAY=combined((*FIELD_MODULES,*TACTICS_MODULES),'REPLAY_ENCOUNTERS')
FUSIONS=tuple(row for module in TACTICS_MODULES for row in getattr(module,'FUSIONS',()))
PRICES=combined(TACTICS_MODULES,'SUMMON_PRICE')
PERSONAS=combined(TACTICS_MODULES,'PERSONAS')
# Index by floor; normalize each field module's named passage record.
PASSAGES={number:(key,stages,reward) for module in FIELD_MODULES
          for key,(_,number,stages,reward) in getattr(module,'PASSAGES',{}).items()}


def cycle(battle):
    for module in CYCLE_MODULES:
        result=module.make_cycle(battle)
        if result is not None:return result
    return None
