"""Turn an isolated story/sandbox loadout into a battle without mutating it."""
from battle_engine import Battle
from battle_data import SKILLS
from cutins import ACTIVE_ORACLE_FEATURES
import campaign_data as config
from shadow_contract import offers


def stage_party(campaign,node):
    """Return the actual deployed allies, shared by the briefing and combat."""
    if node.get('party_size')==1:
        return {}
    team = {name: spec for name,spec in campaign.party_loadout().items()
            if name not in node.get('forbidden_team', ())}
    for name,spec in team.items():
        spec.update(node.get('team_overrides', {}).get(name, {}))
    return team


def solo_readiness(campaign,node):
    """Only report an actionable concern, based on Joker's equipped masks."""
    if node.get('party_size')!=1 or not node.get('solo_threats'):
        return ''
    masks=campaign.persona_loadout()
    lead=next(iter(masks.values()))
    threats=node['solo_threats']
    danger=next((e for e in threats if lead['affinity'].get(e)=='weak'),None)
    if danger and any(spec['affinity'].get(danger)!='weak' for spec in masks.values()):
        return f'Your lead mask is weak to {danger}. Start on a safer mask.'
    if danger:
        return f'Every equipped mask is weak to {danger}. Equip another.'
    heal=any(SKILLS[s]['kind']=='heal' and SKILLS[s]['power']>=60
             for spec in masks.values() for s in spec['skills'])
    if not heal:
        return 'No strong heal equipped. Bring a mask with Diarama or better.'
    return ''


def build_stage(campaign, node_id, seed=None):
    if campaign.status != 'ready' or not campaign.can_play(node_id):
        raise ValueError('Clear the previous operation before deploying.')
    node = campaign.get_node(node_id)
    data = campaign.data
    team = stage_party(campaign,node)
    masks = campaign.persona_loadout()
    nav = node.get('navigator', 'Oracle' if set(data.get('oracle', ())) and
                   node_id.startswith(('space', 'casino', 'cruiser', 'depth', 'lab')) else 'Mona')
    allowed = ACTIVE_ORACLE_FEATURES.intersection(
        node.get('oracle_features_available', ACTIVE_ORACLE_FEATURES if nav == 'Oracle' else ()))
    growth = {k:data.get(k,0) for k in ('joker_hp','joker_sp')}
    if getattr(campaign,'path',None) is None:
        for earlier in config.NODES:
            if earlier['id']==node_id:break
            for k in growth:growth[k]+=earlier.get('reward',{}).get(k,0)
    if node.get('party_size')==1:
        growth['joker_hp']+=32;growth['joker_sp']+=12
    contracts = (offers(node,data['personas']) if getattr(campaign,'path',None) is not None
                 and node_id not in data['cleared'] else {})
    b = Battle(tuple(team), node['title'], seed=seed,
               encounter_config={**node, 'party_size':len(team)+1,'navigator':nav,
                                 'oracle_features': allowed.intersection(data.get('oracle',())),
                                 'available_thieves':('Joker',*data.get('teammates',())),
                                 'contract_offers':contracts},
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
