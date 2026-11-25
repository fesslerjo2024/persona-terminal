"""Reproduce the keyboard and rules regressions from the first Royal run."""
import curses as C
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from persona_terminal.persona5.battle_engine import Battle, SKILLS
from persona_terminal.persona5.battle_ui import ESC
from persona_terminal.persona5.campaign_combat import build_stage
from persona_terminal.persona5.campaign_state import Campaign, TestingCampaign
from .test_battle_audit import Surface, advance_linear_story


class CombatPlaytest(TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.store=Campaign(Path(tmp.name)/'disposable.json')
        self.store.new_game()

    def scene(self,w,h):
        app=Surface(self.store,w,h)
        app.key('1');app.key('1');app.key('\n')
        advance_linear_story(app)
        self.assertEqual(app.page,'battle')
        return app,app._b_battle

    def test_depleted_item_number_remains_bound_and_cannot_act(self):
        before=self.store.path.read_bytes()
        for w,h in ((65,25),(100,35)):
            app,b=self.scene(w,h)
            # Repeat the real sequence from the playtest: Snuff Soul is key 5.
            # Start with depleted SP so the first use has a legitimate target.
            joker=b.allies[0];joker.sp=0
            app.key('5');app.key('5');app.key('1')
            self.assertEqual(b.items['Snuff Soul'],0)
            self.assertEqual(b.items['Hiranya'],2)
            app.key('5');app.key('5')
            self.assertIn('No Snuff Soul left in the bag.',app.capture(app.battle_page))
            self.assertIn('5 Snuff Soul ×0',app.capture(app.battle_page))
            actor=b.actor
            before_retry=dict(b.items)
            app.key('\n')
            self.assertIs(b.actor,actor)
            self.assertEqual(b.items,before_retry)
            self.assertEqual(b.actions('items')[5][0],'item:Hiranya')
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_pending_mask_and_defense_stay_visible_in_target_picker(self):
        for w,h in ((65,25),(100,35)):
            app,b=self.scene(w,h)
            self.assertEqual(b.actor.name,'Joker')
            app.key('1');app.key(C.KEY_RIGHT);app.key('1')
            self.assertEqual(app._b_screen,'targets')
            panel=app.capture(app.battle_page)
            self.assertIn('Pixie / PREVIEW',panel)
            self.assertIn('GuW IcW ElR',panel)
            self.assertIn('Zio → TARGET',panel)
            self.assertEqual(b.persona,'Arsène')
            app.key(ESC);app.key(ESC)
            self.assertNotIn('Pixie / PREVIEW',app.capture(app.battle_page))
            self.assertEqual(b.persona,'Arsène')

    def test_one_more_reports_actual_weakness_chain_and_prior_defense(self):
        b=Battle((),'Fixture',seed=1,shuffle_turns=False,
                 encounter_config={'party_size':1,'waves':[['Silky']]},
                 joker_stats={'hp':170})
        app,_=self.scene(65,25)
        app._b_battle=b;app._b_personas=b.personas
        b.allies[0].buffs['defense']=(-1,3)
        self.assertFalse(b.defeat_diagnosis())
        before=self.store.path.read_bytes()
        app.key('2');app.key('1')
        self.assertEqual(b.phase,'loss')
        self.assertEqual(b.defeat_diagnosis(),(
            'Silky hit Joker’s Ice weakness: 94, then 94 (One More).',
            'Joker’s defense was already lowered.',
        ))
        self.assertTrue(any('Silky gets One More!' in line for line in b.log))
        with patch('persona_terminal.persona5.campaign.time.monotonic',return_value=app.finished+2):
            panel=app.capture(app.draw_combat)
        self.assertEqual(app.page,'result')
        self.assertIn('Silky hit Joker’s Ice weakness: 94, then 94 (One More).',panel)
        self.assertIn('Joker’s defense was already lowered.',panel)
        self.assertIn('A ADJUST LEAD',panel)
        app.key('a')
        self.assertEqual(app.page,'adjust-lead')
        app.key(ESC)
        self.assertEqual(app.page,'result')
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_bonus_forecast_differentiates_scheduled_turn(self):
        app,b=self.scene(65,25)
        # Put a verified same-slot Baton recipient into a deterministic order.
        joker,mona=b.allies[:2]
        b.cursor=0;b.order=[joker,mona,*b.enemies];b.next_order=b.order[:]
        b.actor=joker;b.one_more=True
        self.assertIsNone(b.act('pass:Mona'))
        self.assertIn('NOW Mona +1   NEXT REGULAR Mona',app.capture(app.battle_page))
        b.act('guard')
        self.assertIs(b.actor,mona)
        self.assertNotIn('NEXT REGULAR',app.capture(app.battle_page))

    def test_stale_intel_does_not_leak_replacement_or_hide_tell(self):
        for w,h in ((65,25),(100,35)):
            app,b=self.scene(w,h)
            foe=b.enemies[0]
            b.seen[foe.name]={'Fire':'weak'}
            b.invalidate_readings(foe)
            self.assertIn('READINGS CHANGED',app.capture(app.battle_page))
            self.assertFalse(b.seen.get(foe.name))
            b._strike(b.actor,foe,dict(SKILLS['Eiha'],accuracy=150))
            self.assertNotIn('READINGS CHANGED',app.capture(app.battle_page))
            self.assertIn('Curse',b.seen[foe.name])

    def test_wakaba_rejects_melee_before_spending_turn_or_hp(self):
        b=build_stage(TestingCampaign(),'pyramid-boss',seed=0)
        actor=b.actor;boss=b.enemies[0]
        self.assertEqual(actor.name,'Skull')
        self.assertIn('Magic or Gun. Melee won’t reach.',b.story_intent)
        before=(b.actor,b.cursor,actor.hp,actor.sp,actor.ammo,boss.hp,b.log[:])
        for aid in ('attack','skill:Tempest Slash'):
            self.assertIn('airborne',b.action_block(aid,pick_target=True))
            self.assertIn('airborne',b.act(aid,boss))
            self.assertEqual((b.actor,b.cursor,actor.hp,actor.sp,actor.ammo,boss.hp,b.log),before)
        self.assertIsNone(b.action_block('gun',boss))
        self.assertIsNone(b.action_block('skill:Zionga',boss))
        # Reach the real Ballista through turns, never splicing in a gate.
        for _ in range(14):
            if b.actions('story-special'):break
            self.assertIsNone(b.act('guard'))
        self.assertEqual(b.actions('story-special')[0][1],'Fire Ballista')
        self.assertIsNone(b.act('story-special'))
        self.assertGreater(b._boss_state.get('grounded',0),0)
        self.assertIsNone(b.action_block('attack',boss))
        for _ in range(4):
            if b.actor.name=='Skull':break
            self.assertIsNone(b.act('guard'))
        self.assertEqual(b.actor.name,'Skull')
        self.assertIsNone(b.action_block('skill:Tempest Slash',boss))

    def test_item_description_and_positive_heal_deltas(self):
        b=Battle(('Mona','Skull','Panther'),'Castle Downfall',seed=4,shuffle_turns=False)
        self.assertTrue(b.actions('items')[0][2].startswith('Uses 1 item'))
        joker,mona,skull,panther=b.allies
        joker.hp-=12;skull.hp-=19
        old_sp=mona.sp
        b.actor=mona
        self.assertIsNone(b.act('skill:Mediarama'))
        self.assertEqual(mona.sp,old_sp-12)
        take_heal=[line for line in b.log if 'recover' in line]
        self.assertEqual(take_heal,['HP recovered: Joker +12, Skull +19.'])
        self.assertFalse(any('recovers 0' in line for line in b.log))
