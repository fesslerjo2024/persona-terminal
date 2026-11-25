"""Isolated save data for the reconstructed Phantom campaign.

Reading a Campaign never initializes or migrates a file. Only explicit state
actions commit, and each action commits all changes or none. A TestingCampaign
shares the same loadout API but has no path and no filesystem operations.
"""
from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
from collections.abc import Mapping
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import campaign_data as assets
from battle_data import SKILLS, TEAM

try:
    import fcntl
except ImportError:  # Unix is preferred; file-change checks still run elsewhere.
    fcntl = None

BASE = Path(__file__).resolve().parent
DEFAULT_SAVE = BASE / 'weekend-campaign-save.json'
VERSION = 1
MAX_SAVE_BYTES = 2 * 1024 * 1024
MAX_SQUAD = 3
START_SLOTS = 3
MAX_SLOTS = 12
MAX_PERSONA_SKILLS = 8
MEDALS = {'B': 1, 'A': 2, 'S': 3}


class CampaignError(ValueError):
    """A blocked or uncommitted campaign action."""
NODES = assets.NODES
PERSONA_DATA = assets.PERSONA_DATA
ENEMY_DATA = assets.ENEMY_DATA

def _ordered_nodes():
    if isinstance(NODES, Mapping):
        return dict(NODES)
    return {node['id']: node for node in NODES}

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)

def _unique(items):
    return list(dict.fromkeys(items))

def _int(value, minimum=0, maximum=None):
    return (type(value) is int and value >= minimum and
            (maximum is None or value <= maximum))

def _start_team():
    return _unique(n for n in _as_list(assets.START_TEAM) if n != 'Joker')

def _start_personas():
    p = assets.START_PERSONAS
    if isinstance(p, Mapping):
        return {n: _unique(_as_list(skills)) if not isinstance(skills, Mapping) else [] for n, skills in p.items()}
    return {n: [] for n in _as_list(p)}

def _new_data():
    teammates = _start_team()
    personas = _start_personas()
    slots = getattr(assets, 'START_SLOTS', START_SLOTS)
    squad_slots = getattr(assets, 'START_SQUAD_SLOTS', 2)
    loadout = list(personas)[:slots]
    return {
        'version': VERSION, 'cleared': {},
        'credits': getattr(assets, 'START_CREDITS', 0),
        'teammates': teammates, 'squad': teammates[:squad_slots],
        'personas': personas, 'loadout': loadout,
        'primary': loadout[0] if loadout else None,
        'slots': slots, 'squad_slots': squad_slots,
        'joker_hp': 0, 'joker_sp': 0, 'stats': {},
        'oracle': _unique(_as_list(getattr(assets, 'START_ORACLE', ()))),
        'team_skills': {}, 'skill_cards': {},
    }

def _decode(raw, *, testing=False):
    if len(raw) > MAX_SAVE_BYTES:
        raise ValueError('Save too large.')
    def pairs(items):
        out = dict(items)
        if len(out) != len(items):
            raise ValueError('Duplicate JSON keys.')
        return out
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite number.')))
    if not isinstance(value, dict) or type(value.get('version')) is not int or value['version'] != VERSION:
        raise ValueError('Unrecognized campaign save format.')
    if not isinstance(value.get('cleared'), dict):
        raise ValueError('Invalid cleared chapter list.')
    cleared = value['cleared']; order = list(_ordered_nodes())
    if any(k not in order or not isinstance(v, str) or v not in MEDALS for k, v in cleared.items()):
        raise ValueError('Unrecognized cleared chapter.')
    if not testing and set(cleared) != set(order[:len(cleared)]):
        raise ValueError('Campaign advances in chapter order.')
    if not _int(value.get('credits')):
        raise ValueError('Invalid credit balance.')
    for field in ('joker_hp', 'joker_sp'):
        if not _int(value.get(field)):
            raise ValueError('Invalid ' + field + ' data.')
    stats = value.get('stats')
    if not isinstance(stats, dict) or not all(_int(v) for v in stats.values()):
        raise ValueError('Invalid stat data.')
    if not _valid_names(value.get('oracle'), {'support','guard','ufo'}):
        raise ValueError('Invalid Oracle support configuration.')
    if not _int(value.get('slots'), 1, MAX_SLOTS) or not _int(value.get('squad_slots'), 1, MAX_SQUAD):
        raise ValueError('Invalid loadout capacity.')
    roster = value.get('teammates'); squad = value.get('squad')
    if not _valid_names(roster, set(TEAM)-{'Joker'}):
        raise ValueError('Invalid teammate roster.')
    if not _valid_names(squad, set(roster)) or len(squad) > value['squad_slots']:
        raise ValueError('Invalid active squad.')
    upgrades = value.get('team_skills')
    if not isinstance(upgrades, dict) or any(n not in roster or not _valid_names(v, SKILLS) for n, v in upgrades.items()):
        raise ValueError('Invalid teammate skills.')
    cards = value.get('skill_cards')
    if not isinstance(cards, dict) or any(n not in SKILLS or not _int(v, 1) for n, v in cards.items()):
        raise ValueError('Invalid skill card stock.')
    personas = value.get('personas'); loadout = value.get('loadout')
    if not isinstance(personas, dict) or not personas:
        raise ValueError('Missing Persona collection.')
    for name, skills in personas.items():
        if name not in PERSONA_DATA or not _valid_names(skills, SKILLS):
            raise ValueError('Invalid Persona collection entry.')
    if not _valid_names(loadout, set(personas)) or not 1 <= len(loadout) <= value['slots']:
        raise ValueError('Invalid Persona loadout.')
    if value.get('primary') not in loadout:
        raise ValueError('The primary Persona must be carried.')
    return value

def _valid_names(items, pool):
    return (isinstance(items, list) and all(isinstance(n, str) and n in pool for n in items)
            and len(set(items)) == len(items))

def _serialize(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')

def _read(path):
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
                     | getattr(os, 'O_NONBLOCK', 0))
    except FileNotFoundError:
        return None
    with os.fdopen(fd, 'rb') as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise OSError('Campaign path is not a regular file.')
        return f.read(MAX_SAVE_BYTES + 1)

def _sync_dir(path):
    if os.name != 'posix':
        return
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        os.fsync(fd)
    except OSError:
        # The atomic rename has succeeded. Some filesystems cannot fsync
        # directories, and a sync fault shouldn't imply that it did not commit.
        pass
    finally:
        if fd is not None:
            os.close(fd)

@contextmanager
def _save_lock(path):
    fd = None
    if fcntl is not None:
        fd = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        if fd is not None:
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        if fd is not None:
            os.close(fd)

def _write(path, raw, *, exclusive=False):
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', suffix='.tmp', dir=path.parent)
    try:
        f = os.fdopen(fd, 'wb')
        with f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        if exclusive:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
        _sync_dir(path.parent)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass

def _reward_mapping(node):
    return node.get('rewards', node.get('reward', {})) or {}

def _apply_rewards(data, rewards):
    if not isinstance(rewards, Mapping):
        raise ValueError('Node rewards must be a mapping.')
    gained = {}
    credits = rewards.get('credits', 0)
    if not _int(credits):
        raise ValueError('Reward credits must be a non-negative number.')
    if credits:
        data['credits'] += credits
        gained['credits'] = credits
    full_squad = len(data['squad']) == data['squad_slots']
    _update_capacity(data, rewards, gained)
    for teammate in _as_list(rewards.get('teammates', rewards.get('roster', rewards.get('team')))):
        if teammate not in TEAM or teammate == 'Joker':
            raise ValueError('Unknown teammate reward: ' + str(teammate))
        if teammate not in data['teammates']:
            data['teammates'].append(teammate)
            if len(data['squad']) < data['squad_slots']:
                data['squad'].append(teammate)
            gained.setdefault('teammates', []).append(teammate)
    if full_squad and 'squad_slots' in gained:
        standby = [n for n in data['teammates'] if n not in data['squad']]
        data['squad'].extend(standby[:data['squad_slots']-len(data['squad'])])
    for field in ('joker_hp', 'joker_sp'):
        increment = rewards.get(field, 0)
        if not _int(increment):
            raise ValueError('Invalid ' + field + ' reward.')
        if increment:
            data[field] += increment
            gained[field] = increment
    for feature in _as_list(rewards.get('oracle')):
        if feature not in {'support','guard','ufo'}:
            raise ValueError('Invalid Oracle reward.')
        if feature not in data['oracle']:
            data['oracle'].append(feature)
            gained.setdefault('oracle', []).append(feature)
    team_skills = rewards.get('team_skills') or {}
    if not isinstance(team_skills, Mapping):
        raise ValueError('Teammate skill rewards need a mapping.')
    for name, bonuses in team_skills.items():
        if name not in data['teammates']:
            raise ValueError('Unknown teammate: ' + str(name))
        moves = data['team_skills'].setdefault(name, [])
        for skill in _as_list(bonuses):
            if skill not in SKILLS:
                raise ValueError('Unknown teammate skill: ' + str(skill))
            if skill not in moves and skill not in TEAM[name]['skills']:
                moves.append(skill)
                gained.setdefault('team_skills', {}).setdefault(name, []).append(skill)
    cards = rewards.get('skill_cards') or []
    if isinstance(cards, Mapping):
        stock = cards.items()
    else:
        stock = ((skill, 1) for skill in _as_list(cards))
    for skill, count in stock:
        if skill not in SKILLS or not _int(count, 1):
            raise ValueError('Invalid skill card reward: ' + str(skill))
        data['skill_cards'][skill] = data['skill_cards'].get(skill, 0) + count
        gained.setdefault('skill_cards', []).extend([skill]*count)
    personas = rewards.get('personas') or rewards.get('persona') or []
    personas = personas if isinstance(personas, Mapping) else dict.fromkeys(_as_list(personas), ())
    additions = dict(personas)
    skills = rewards.get('skills') or {}
    if not isinstance(skills, Mapping):
        raise ValueError('Skill rewards need a Persona-to-skills mapping.')
    for name, bonus in skills.items():
        additions[name] = _as_list(additions.get(name)) + _as_list(bonus)
    for name, bonus in additions.items():
        if name not in PERSONA_DATA:
            raise ValueError('Unknown Persona reward: ' + str(name))
        if name not in data['personas']:
            gained.setdefault('personas', []).append(name)
            data['personas'][name] = []
        for skill in _as_list(bonus):
            if skill not in SKILLS:
                raise ValueError('Unknown skill reward: ' + str(skill))
            if skill not in data['personas'][name]:
                data['personas'][name].append(skill)
                gained.setdefault('skills', {}).setdefault(name, []).append(skill)
    stat_bonus = rewards.get('stats') or {}
    if not isinstance(stat_bonus, Mapping):
        raise ValueError('Invalid stat rewards.')
    for key, n in stat_bonus.items():
        if not _int(n):
            raise ValueError('Invalid stat reward.')
        data['stats'][key] = data['stats'].get(key, 0) + n
    if stat_bonus:
        gained['stats'] = dict(stat_bonus)
    return gained

def _update_capacity(data, rewards, gained):
    for field, maximum in (('slots', MAX_SLOTS), ('squad_slots', MAX_SQUAD)):
        old = data[field]
        target = rewards.get(field)
        add = rewards.get(field + '_add', 0)
        if not _int(add):
            raise ValueError('Invalid capacity increase.')
        if target is not None:
            if not _int(target, 1):
                raise ValueError('Invalid loadout capacity.')
            if target == 1:
                add += 1  # Current story modules use +1; legacy nodes give totals.
                target = old
            elif field == 'squad_slots':
                target -= 1  # Older rewards give total battle size, including Joker.
        data[field] = min(maximum, max(old, target if target is not None else old) + add)
        if data[field] > old:
            gained[field] = data[field] - old

class Campaign:
    def __init__(self, path=DEFAULT_SAVE):
        self.path = Path(path).absolute() if path is not None else DEFAULT_SAVE
        self.last_error = ''
        self.last_backup = None
        self.status = 'missing'
        self._raw = None
        self._data = _new_data()
        self.reload()

    @property
    def data(self):
        value = copy.deepcopy(self._data)
        value['roster'] = list(value['teammates'])
        return value

    def reload(self):
        self.last_error = ''
        self._data = _new_data()
        self._raw = None
        try:
            self._raw = _read(self.path)
            if self._raw is None:
                self.status = 'missing'
            else:
                self._data = _decode(self._raw)
                self.status = 'ready'
        except (OSError, ValueError, RecursionError, TypeError, KeyError, OverflowError) as exc:
            self.status = 'corrupt'
            self.last_error = 'Campaign save could not be loaded: ' + str(exc)
        return self.status

    def _fail(self, message):
        self.last_error = message
        raise CampaignError(message)

    def new_game(self):
        """Explicitly start over; save an exact sibling backup if one exists."""
        self.last_backup = None
        self._commit(_new_data(), reset=True)
        return self.last_backup

    def _commit(self, value, *, reset=False):
        if not reset and self.status != 'ready':
            return self._fail('Start or load a valid campaign first.')
        self.last_error = ''
        value.pop('roster', None)
        try:
            next_bytes = _serialize(value)
            _decode(next_bytes)
            with _save_lock(self.path):
                current = _read(self.path)
                if current is not None and len(current) > MAX_SAVE_BYTES:
                    return self._fail('Save is too large to replace safely.')
                if current != self._raw:
                    return self._fail('Save changed on disk. Reload before trying again.')
                if reset and current is not None:
                    backup = self.path.with_name(self.path.name + '.' + uuid4().hex + '.backup')
                    _write(backup, current, exclusive=True)
                    self.last_backup = backup
                _write(self.path, next_bytes, exclusive=current is None)
        except CampaignError:
            raise
        except (OSError, ValueError, TypeError, OverflowError) as exc:
            return self._fail('Campaign progress was not saved: ' + str(exc))
        self._data = value
        self._raw = next_bytes
        self.status = 'ready'
        return True

    def get_node(self, node_id):
        node = _ordered_nodes().get(node_id)
        return copy.deepcopy(node) if node is not None else None

    @property
    def next_node(self):
        return next((k for k in _ordered_nodes() if k not in self._data['cleared']), None)

    def can_play(self, node_id):
        return (self.status == 'ready' and node_id in _ordered_nodes()
                and (node_id == self.next_node or node_id in self._data['cleared']))

    def clear(self, node_id, grade=None):
        grade = 'B' if grade is None else grade
        if not isinstance(grade, str) or grade not in MEDALS:
            return self._fail('Invalid combat medal.')
        if not self.can_play(node_id):
            return self._fail('That operation is locked.')
        current = self._data['cleared'].get(node_id)
        value = self.data
        if current:
            if MEDALS[grade] > MEDALS[current]:
                value['cleared'][node_id] = grade
                self._commit(value)
            return {}
        try:
            rewards = _apply_rewards(value, _reward_mapping(self.get_node(node_id)))
        except (ValueError, TypeError) as exc:
            return self._fail(str(exc))
        value['cleared'][node_id] = grade
        self._commit(value)
        return rewards

    def equip_squad(self, names):
        if isinstance(names, str):
            return self._fail('Choose a list of teammates.')
        try:
            names = list(names)
        except TypeError:
            return self._fail('Choose a list of teammates.')
        if not all(isinstance(n, str) for n in names) or names.count('Joker') > 1:
            return self._fail('Choose distinct teammates.')
        names = [n for n in names if n != 'Joker']
        if not _valid_names(names, set(self._data['teammates'])) or len(names) > self._data['squad_slots']:
            return self._fail(f"Choose up to {self._data['squad_slots']} distinct recruited teammates.")
        value = self.data
        value['squad'] = names
        return self._commit(value)

    def equip_personas(self, names, primary=None):
        if isinstance(names, str):
            return self._fail('Choose a list of Personas.')
        try:
            names = list(names)
        except TypeError:
            return self._fail('Choose a list of Personas.')
        if not _valid_names(names, self._data['personas']) or not 1 <= len(names) <= self._data['slots']:
            return self._fail(f"Choose 1–{self._data['slots']} distinct owned Personas.")
        if primary is None:
            primary = self._data['primary'] if self._data['primary'] in names else names[0]
        if primary not in names:
            return self._fail('The primary Persona must be in the loadout.')
        value = self.data
        value['loadout'], value['primary'] = names, primary
        return self._commit(value)

    def party_loadout(self):
        """Ordered battle specs for teammates only; Joker is provided separately."""
        team = {}
        for name in self._data['squad']:
            spec = copy.deepcopy(TEAM[name])
            spec['skills'] = _unique(list(spec['skills']) + self._data['team_skills'].get(name, []))
            team[name] = spec
        return team

    def persona_spec(self, name):
        if name not in PERSONA_DATA:
            return self._fail('Unknown Persona: ' + str(name))
        spec = copy.deepcopy(PERSONA_DATA[name])
        spec['skills'] = _unique(list(spec['skills']) + self._data['personas'].get(name, []))
        return spec

    def persona_loadout(self):
        primary = self._data['primary']
        names = ([primary] if primary else []) + [p for p in self._data['loadout'] if p != primary]
        return {name: self.persona_spec(name) for name in names}

    def fusion_options(self, name):
        recipe = next((r for r in getattr(assets, 'FUSIONS', ()) if r.get('result') == name), None)
        if recipe is None or name not in PERSONA_DATA:
            return self._fail('No known fusion for ' + str(name) + '.')
        parents = tuple(recipe['parents'])
        owned = self._data['personas']
        missing = [donor for donor in parents if donor not in owned]
        cost = recipe['cost']
        if not _int(cost):
            return self._fail('Fusion has invalid credit cost.')
        donors = {}
        base_skills = set(PERSONA_DATA[name]['skills'])
        for donor in parents:
            if donor in owned:
                donors[donor] = [skill for skill in self.persona_spec(donor)['skills']
                                 if skill not in base_skills
                                 and not SKILLS[skill].get('enemy_only', False)]
        reason = ('Already registered.' if name in owned else
                  'Missing parents: ' + ', '.join(missing) if missing else
                  'Insufficient credits.' if self._data['credits'] < cost else '')
        return {'recipe': copy.deepcopy(recipe), 'donors': donors, 'reason': reason,
                'available': not reason}

    def fuse(self, name, skill=None, donor=None):
        options = self.fusion_options(name)
        if not options['available']:
            return self._fail(options['reason'])
        if skill is not None and skill not in options['donors'].get(donor, ()):
            return self._fail('The selected parent cannot pass down that skill.')
        if skill is None and donor is not None:
            return self._fail('Choose a skill to inherit from that parent.')
        if skill is not None and len(self.persona_spec(name)['skills']) >= MAX_PERSONA_SKILLS:
            return self._fail('This Persona has no room for a bonus skill.')
        value = self.data
        value['credits'] -= options['recipe']['cost']
        value['personas'][name] = [skill] if skill else []
        self._commit(value)
        return name

    def apply_skill_card(self, name, skill):
        if name not in self._data['personas']:
            return self._fail('Register that Persona before teaching it a skill.')
        if self._data['skill_cards'].get(skill, 0) < 1:
            return self._fail('No copy of that Skill Card is available.')
        skills = self.persona_spec(name)['skills']
        if skill in skills:
            return self._fail('This Persona already knows that skill.')
        if len(skills) >= MAX_PERSONA_SKILLS:
            return self._fail('This Persona has no room for a bonus skill.')
        value = self.data
        value['personas'][name].append(skill)
        value['skill_cards'][skill] -= 1
        if not value['skill_cards'][skill]:
            del value['skill_cards'][skill]
        self._commit(value)
        return skill

class TestingCampaign(Campaign):
    """Fully unlocked test-only state; no reads from or writes to any save."""
    __test__ = False

    def __init__(self):
        self.path = None
        self.status = 'ready'
        self.last_error = ''
        self.last_backup = None
        self._raw = None
        self.new_game()

    def reload(self):
        return self.status

    def new_game(self):
        data = _new_data()
        data['teammates'] = [n for n in TEAM if n != 'Joker']
        data['personas'] = {n: [] for n in PERSONA_DATA}
        data['slots'] = min(MAX_SLOTS, len(PERSONA_DATA))
        data['squad_slots'] = MAX_SQUAD
        data['credits'] = 9999
        data['oracle'] = ['support','guard','ufo']
        data['skill_cards'] = {k: 5 for node in _ordered_nodes().values()
                               for k in _as_list(_reward_mapping(node).get('skill_cards'))}
        self._commit(data, reset=True)
        return None

    def can_play(self, node_id):
        return node_id in _ordered_nodes()

    def clear(self, node_id, grade=None):
        if not self.can_play(node_id):
            return self._fail('Unknown practice operation.')
        return {}  # Tests never record medals or story rewards.

    def _commit(self, value, *, reset=False):
        try:
            value.pop('roster', None)
            _decode(_serialize(value), testing=True)
        except (ValueError, TypeError, OverflowError) as exc:
            return self._fail(str(exc))
        self._data = value
        self.last_error = ''
        self.status = 'ready'
        return True
