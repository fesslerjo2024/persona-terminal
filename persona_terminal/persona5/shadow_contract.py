"""Optional one-time Hold Up recruitment; no save fields or RNG of its own."""
from collections.abc import Mapping
from dataclasses import dataclass


# Species that exist as regular enemies, adapted as small, balanced masks
# for the optional system. Other campaign masks remain owned by campaign data.
CAMPAIGN_PERSONAS = {
    'Eligor': {
        'skills': ['Agi', 'Cleave', 'Tarukaja'],
        'affinity': {'Electric':'weak', 'Fire':'resist', 'Curse':'resist'},
        'role': 'Fire • physical • attack up',
    },
    'Koppa Tengu': {
        'skills': ['Garu', 'Sukukaja', 'Sukunda'],
        'affinity': {'Ice':'weak', 'Wind':'resist'},
        'role': 'Wind • agility effects',
    },
    'Fuu-Ki': {
        'skills': ['Garula', 'Magarula', 'Sukunda'],
        'affinity': {'Electric':'weak', 'Wind':'resist'},
        'role': 'Wind • agility debuff',
    },
}


@dataclass(frozen=True)
class Offer:
    node: str
    shadow: str
    persona: str


# An allow-list of ordinary encounters excludes palace bosses, staged
# reinforcements and interludes even if a later data edit reuses a species.
_NORMAL_OPERATIONS = {
    'east-gallery': {'Eligor': 'Eligor'},
    'treasure-route': {'Eligor': 'Eligor'},
    'museum-entry': {'Koppa Tengu': 'Koppa Tengu'},
    'museum-security': {'Koppa Tengu': 'Koppa Tengu'},
    'museum-gallery': {'Koppa Tengu': 'Koppa Tengu'},
    'museum-vault': {'Koppa Tengu': 'Koppa Tengu'},
    'bank-service': {'Fuu-Ki': 'Fuu-Ki'},
    'bank-security': {'Fuu-Ki': 'Fuu-Ki'},
    'bank-heist': {'Fuu-Ki': 'Fuu-Ki'},
    'pyramid-light': {'Pyramid Isis': 'Isis'},
}


def _reward_personas(reward):
    value=reward.get('personas') or reward.get('persona') or ()
    if isinstance(value,str):
        return {value: ()}
    return dict(value) if isinstance(value,Mapping) else dict.fromkeys(value, ())


def offers(node, registered):
    """Eligible species by exact source identity; never infer from UI names."""
    masks=_NORMAL_OPERATIONS.get(node['id'], {})
    if not masks:
        return {}
    guaranteed=set(_reward_personas(node.get('rewards',node.get('reward',{})) or {}))
    species={name for wave in node.get('waves',()) for name in wave}
    return {shadow:Offer(node['id'],shadow,name) for shadow,name in masks.items()
            if shadow in species and name not in registered and name not in guaranteed}


def merge_reward(node, registered, reward, result):
    """Validate the earned offer again at the atomic first-clear transaction."""
    if not isinstance(result,Offer) or offers(node,registered).get(result.shadow)!=result:
        raise ValueError('That Shadow Contract is not available for this operation.')
    result_masks=_reward_personas(reward)
    result_masks[result.persona]=()
    return {**reward,'personas':result_masks}


def _targets(b):
    allowed=b.config.get('contract_offers')
    if not b.story or b.contract is not None or not allowed or not b.hold_up:
        return {}
    visible=b.visible_enemies
    # _spawn instantiates this exact ordered list; the printed A/B duplicate
    # suffix is deliberately not parsed, and hidden foes cannot be picked.
    return {target:allowed[species] for target,species in zip(b.enemies,b.waves[b.wave-1])
            if species in allowed and target in visible and target.alive
            and target.down and not target.no_knockdown}


def targets(b):
    return list(_targets(b))


def actions(b):
    candidates=_targets(b)
    if not candidates:
        return []
    masks=', '.join(dict.fromkeys(offer.persona for offer in candidates.values()))
    return [('contract','Shadow Contract',f'{masks}: register on victory. Ends Hold Up.')]


def accept(b,target):
    """Trade the current Hold Up for one withdrawal and a pending Persona."""
    offer=_targets(b).get(target)
    if offer is None:
        return 'No Shadow Contract for that target.'
    b.contract=offer
    b._say(f'{target.name} withdraws. Register {offer.persona} on victory.')
    # Engine presence is HP-based. No damage/KO animation: the Shadow left.
    target.hp=0
    target.down=False
    target.status=''
    b.one_more=False
    b.chain=0
    b.passed.clear()
    if not b._state() or b.phase=='turn':
        b._advance()
    return None
