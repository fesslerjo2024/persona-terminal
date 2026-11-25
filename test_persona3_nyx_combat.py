"""Combat-level tests for the playable finale (no saves, apps or GUI)."""
import unittest

from persona3_combat import P3Battle, SKILLS, THEURGIES, LEAD_ID
from persona3_nyx_combat import AVATAR, FORMS, JIN, TAKAYA


ROSTERS=((LEAD_ID,'Yukari','Junpei','Akihiko'),(LEAD_ID,'Ken','Mitsuru','Koromaru'))
STOCK={p:() for p in ("Jack O'Lantern",'Jack Frost','Orpheus','Apsaras',
                       'Seiryu','Kikuri-Hime','Pale Rider','Suzaku','Raphael','Ose')}
SUPPLIES={'Medicine':5,'Soul Drop':2,'Revival Bead':1,'Dis-Charm':2}


def _choice(b):
    """Plan through regular public actions; affinities are a known-playthrough strategy."""
    actor=b.actor
    foe=next((u for u in b.enemies if u.alive),b.enemies[0])
    living=[u for u in b.allies if u.alive]
    lead=b.allies[0]
    wounded=min(living,key=lambda u:u.hp/u.max_hp)
    if b.charge.get('Fuuka')==100 and wounded.hp*2<wounded.max_hp:
        return 'oracle',None,None
    shield='NEXT' in b.threat
    if any(k in b.threat for k in ('GRENADE /','BUFUDYNE /')) and f'{actor.label}:' in b.threat:
        shield=True
    pool=[(95 if shield else 0,('guard',None,None))]
    masks=(tuple(b.stock) if not b.persona_used else (b.persona,)) if actor.name==LEAD_ID else (None,)

    def add(score,action,target=None,persona=None):
        targets=b._targets(action)
        if (target in targets or target is None and not targets) and not b._block(action,target,persona=persona):
            pool.append((score,(action,target,persona)))

    def attack_power(p,elem):
        return p*(.52 if foe.affinity.get(elem)=='resist' else 1)

    def works(elem):
        return foe.affinity.get(elem) not in ('null','drain','repel')

    for persona in masks:
        for n in b.stock[persona] if persona else actor.skills:
            kind,elem,power,sp,mode,hp=SKILLS[n]
            action='skill:'+n
            if kind=='heal':
                top=lead if lead.hp<lead.max_hp*.40 else wounded
                ratio=wounded.hp/wounded.max_hp
                amount=sum(min(u.max_hp-u.hp,power) for u in living)*.73 if mode=='team' else min(top.max_hp-top.hp,power)
                score=amount*(1.15-ratio if ratio<.62 else .20)-sp*.3
                if shield and top.hp<top.max_hp*.42:score+=55
                add(score,action,None if mode=='team' else top,persona)
            elif kind=='buff' and elem=='attack' and mode=='team' and any(u.attack<1 for u in living):
                add(57,action,None,persona)
            elif kind=='debuff' and not shield and foe.hp>135:
                if elem=='defense' and foe.defense>=0 and foe.hp>=foe.max_hp*.45:
                    add(51,action,foe,persona)
                if elem=='attack' and foe.attack>=0 and wounded.hp<wounded.max_hp*.59:
                    add(48,action,foe,persona)
            elif kind=='hit' and not shield and works(elem):
                score=attack_power(power,elem)-sp*.42-hp*.7
                add(score+(22 if foe.hp<=score else 0),action,foe if mode=='one' else None,persona)
    if not shield and works(actor.element):
        score=attack_power(actor.power,actor.element)+2
        add(score+(22 if foe.hp<=score else 0),'attack',foe)
    for id in b._theurgy_ids():
        if b._theurgy_block(id):continue
        _,kind,_,power,mode,_=THEURGIES[id]
        if kind=='damage' and not shield and (foe.hp>power/2 or not works(actor.element)):
            pool.append((min(108,power),('theurgy:'+id,foe if mode=='single' else None,None)))
        if kind=='heal' and wounded.hp/wounded.max_hp<.61:
            pool.append((109,('theurgy:'+id,None,None)))
    if wounded.hp<wounded.max_hp*.68:
        add(min(wounded.max_hp-wounded.hp,50)*1.12+
            (57 if wounded.hp<wounded.max_hp*.29 and shield else 0),'item:Medicine',wounded)
    for u in b.allies:
        if not u.alive:add(70,'item:Revival Bead',u)
    if actor.sp<8:add(41 if shield else 25,'item:Soul Drop',actor)
    return max(pool,key=lambda pair:pair[0])[1]


class NyxCombatTests(unittest.TestCase):
    def test_complete_summit_with_two_different_squads_and_carry(self):
        for party,seed in zip(ROSTERS,(13,41)):
            with self.subTest(party=party):
                previous=None
                for id in (JIN,TAKAYA,AVATAR):
                    b=P3Battle(id,level=17,persona='Suzaku',stock=STOCK,fuuka=True,theurgy=True,
                               party=party,seed=seed,low_motion=True,
                               resources=previous.resources if previous else None,
                               inventory=previous.inventory if previous else SUPPLIES)
                    if previous:
                        self.assertEqual(b.resources,previous.resources)
                        self.assertEqual(b.inventory,previous.inventory)
                    if id==TAKAYA:self.assertNotIn('Jin',b.threat)
                    phases=[]
                    seen=set()
                    for _ in range(180):
                        if b.outcome:break
                        seen.add(b.threat)
                        if id==AVATAR:
                            form=b.late_cycle.form.name
                            if not phases or phases[-1]!=form:
                                phases.append(form)
                        action,t,p=_choice(b)
                        self.assertIsNone(b.act(action,t,persona=p),(action,b.actor.label,b.threat))
                    self.assertEqual(b.outcome,'win',(id,b.log))
                    if id==AVATAR:
                        self.assertEqual(phases,[f.name for f in FORMS])
                        self.assertTrue(any('APOCALYPSE NEXT' in t for t in seen),seen)
                        self.assertTrue(any('NIGHT QUEEN NEXT' in t for t in seen),seen)
                        self.assertTrue(any('The Avatar falls' in line for line in b.log))
                        self.assertFalse(b.targetable_enemies)
                        self.assertFalse(any('Great Seal' in line for line in b.log))
                    previous=b

    def test_arcana_shift_invalidates_previous_intel(self):
        b=P3Battle(AVATAR,level=17,theurgy=True,stock=STOCK,seed=0,low_motion=True)
        foe=b.enemies[0]
        self.assertTrue(b.act('great-seal'))
        self.assertIsNone(b.act('attack',foe))
        self.assertIn('Slash',b.seen[foe.name])
        while b.late_cycle.form.name=='Fool':
            self.assertIsNone(b.act('guard'))
        self.assertEqual(foe.affinity,{'Fire':'null'})
        self.assertNotIn(foe.name,b.seen)
        self.assertFalse(foe.down)
        self.assertFalse(b.all_out)

    def test_defeating_death_ends_combat_without_starting_a_second_battle(self):
        b=P3Battle(AVATAR,level=13,seed=2)
        cycle=b.late_cycle
        cycle._shift(b,len(FORMS)-1)
        cycle.boss.hp=0
        self.assertTrue(b._ended())
        self.assertEqual(b.outcome,'win')
        self.assertEqual(cycle.boss.name,'Nyx Avatar')
        self.assertEqual(cycle.boss.hp,0)
