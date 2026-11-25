"""Compose chapter modules, keeping unlock order and original trial tables separate."""
from importlib import import_module
from importlib.util import find_spec
from copy import deepcopy
from battle_data import ENEMIES, PERSONAS
from shadow_contract import CAMPAIGN_PERSONAS

START_TEAM = ('Mona','Skull')
START_PERSONAS = ('Arsène','Pixie',"Jack-o'-Lantern")
START_CREDITS = 75
START_SLOTS = 3
START_SQUAD_SLOTS = 2
START_ORACLE = ()
PERSONA_DATA = deepcopy(PERSONAS)
ENEMY_DATA = deepcopy(ENEMIES)
CHAPTERS = ()
FUSIONS = ()

for module in ('early_data','pyramid_data','spaceport_data','casino_data','late_data'):
    if find_spec(module) is None:
        continue  # An unfinished chapter module does not become playable.
    data = import_module(module)
    if hasattr(data, 'CHAPTERS'):
        CHAPTERS += tuple(data.CHAPTERS)
    else:
        info = {'pyramid_data':('pyramid','Futaba’s Pyramid'),
                'spaceport_data':('spaceport','Okumura’s Spaceport')}[module]
        CHAPTERS += (dict(id=info[0],title=info[1],nodes=tuple(data.NODES),
                          brief=info[1],completion='Operation complete.'),)
    PERSONA_DATA.update(getattr(data, 'PERSONA_ADDITIONS', {}))
    ENEMY_DATA.update(getattr(data, 'ENEMY_ADDITIONS', {}))
    FUSIONS += tuple(getattr(data, 'FUSION_ADDITIONS', ()))

PERSONA_DATA.update(CAMPAIGN_PERSONAS)
NODES = tuple(node for chapter in CHAPTERS for node in chapter['nodes'])

# Local progression recipes, not a reproduction of Royal's level/Arcana table.
FUSIONS += tuple(dict(parents=parents,result=result,cost=cost) for parents,result,cost in (
    (('Arsène','Pixie'),'High Pixie',135),
    (('Pixie',"Jack-o'-Lantern"),'Angel',125),
    (('Angel','Silky'),'Jack Frost',200),
    (('Arsène','Silky'),'Makami',230),
    (('Jack Frost','Makami'),'Shiki-Ouji',255),
    (('Makami','Angel'),'Orthrus',260),
    (('Angel','Makami'),'Isis',245),
    (('Isis','Orthrus'),'Thoth',310),
    (('Isis','Thoth'),'Decarabia',360),
) if result in PERSONA_DATA and all(p in PERSONA_DATA for p in parents))
