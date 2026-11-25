"""Turn an isolated story/sandbox loadout into a battle without mutating it."""
from battle_engine import Battle
from battle_data import SKILLS
import campaign_data as config


DEFENSE_ELEMENTS = ('Fire','Ice','Electric','Wind','Psy','Nuclear','Bless','Curse')
SUPPORT_KINDS = ('heal','revive','cure','buff','debuff','dekaja','dekunda')


def equipped_kits(campaign,node):
    team = {name: spec for name,spec in campaign.party_loadout().items()
            if name not in node.get('forbidden_team', ())}
    for name,spec in team.items():
        spec.update(node.get('team_overrides', {}).get(name, {}))
    if node.get('party_size')==1:team={}
    masks = campaign.persona_loadout()
    return team,masks


def readiness(campaign,node):
    """Summarize the deployed party, not enemy or hidden affinity data."""
    team,masks=equipped_kits(campaign,node)
    entries={'Joker': [move for mask in masks.values() for move in mask['skills']]}
    entries.update({name: kit['skills'] for name,kit in team.items()})
    rows={}
    for name, moves in entries.items():
        markers={SKILLS[m]['element'] for m in moves if m in SKILLS and SKILLS[m]['kind']=='damage'}
        support={SKILLS[m]['kind'] for m in moves if m in SKILLS}
        rows[name]=(tuple(e for e in DEFENSE_ELEMENTS if e in markers),
                    tuple(k for k in SUPPORT_KINDS if k in support))
    return rows


def build_stage(campaign, node_id, seed=None):
    if campaign.status != 'ready' or not campaign.can_play(node_id):
        raise ValueError('Clear the previous operation before deploying.')
    node = campaign.get_node(node_id)
    data = campaign.data
    team,masks=equipped_kits(campaign,node)
    nav = node.get('navigator', 'Oracle' if set(data.get('oracle', ())) and
                   node_id.startswith(('space', 'casino', 'cruiser', 'depth', 'lab')) else 'Mona')
    allowed = set(node.get('oracle_features_available', ('support', 'guard', 'ufo') if nav == 'Oracle' else ()))
    growth = {k:data.get(k,0) for k in ('joker_hp','joker_sp')}
    if getattr(campaign,'path',None) is None:
        for earlier in config.NODES:
            if earlier['id']==node_id:break
            for k in growth:growth[k]+=earlier.get('reward',{}).get(k,0)
    if node.get('party_size')==1:
        growth['joker_hp']+=32;growth['joker_sp']+=12
    b = Battle(tuple(team), node['title'], seed=seed,
               encounter_config={**node, 'party_size':len(team)+1,'navigator':nav,
                                 'oracle_features': allowed.intersection(data.get('oracle',())),
                                 'available_thieves':('Joker',*data.get('teammates',()))},
               team_data=team, persona_pool=masks, enemy_data=config.ENEMY_DATA,
               joker_stats={'hp':180+growth['joker_hp'],'sp':55+growth['joker_sp']})
    b.items.update(node.get('items', {}))
    if node.get('party_size')==1:
        b.items['Medicine']+=2
        b.items['Snuff Soul']+=1
    return b


def stage_grade(b):
    if b.phase != 'win':
        raise ValueError('A battle must be won to earn a medal.')
    standing = [u for u in b.allies if u.alive and not u.down]
    return 'S' if len(standing)==len(b.allies) and all(2*u.hp>=u.max_hp for u in standing) else 'A' if len(standing)*4>=len(b.allies)*3 else 'B'
