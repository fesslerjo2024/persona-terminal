"""Scene state, clue continuity, compact rendering, and campaign keyboard wiring."""
from pathlib import Path
from tempfile import TemporaryDirectory
import curses as C
import cinema
import unittest
from unittest.mock import patch

from battle_ui import ESC
from campaign_data import CHAPTERS, NODES
from campaign_state import Campaign
from campaign_story import (CASINO_SIGNAL, PYRAMID_FRAGMENTS, PYRAMID_MOTIF,
                            RECRUIT_HANDOFFS, SCENES, StoryScene, story_offer)
from satanael_scene import TITLE as SATANAEL_CUT
from test_palace_menu import RecordedSurface
from weekend_bosses import on_round


class CampaignStoryTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / 'campaign.json'

    def fixture(self, operation):
        save = Campaign(self.path)
        save.new_game()
        for node in NODES:
            if node['id'] == operation:
                break
            save.clear(node['id'], 'S')
        app = RecordedSurface(save)
        app.key('1')
        app.ch, number = next(
            (i, j+1) for i, chapter in enumerate(CHAPTERS)
            for j, node in enumerate(chapter['nodes']) if node['id'] == operation
        )
        app.key(str(number))
        self.assertEqual(app.page, 'brief')
        return app

    def test_cold_open_and_casino_phone_handoff_are_keyboard_scenes(self):
        app = RecordedSurface(Campaign(self.path))
        app.key('2')
        self.assertEqual(app.story_scene.scene_id, 'casino-cold-open')
        self.assertIn(CASINO_SIGNAL, app.story_scene.scene.beats['start'].body)
        app.key('1')
        self.assertEqual(app.story_scene.beat, 'balcony')
        for beat in ('arrest', 'interrogation'):
            app.key('\n')
            self.assertEqual(app.story_scene.beat, beat)
        app.key('\n')
        self.assertEqual(app.page, 'prologue')
        result = self.fixture('casino-heist')
        result.key('\n')
        self.assertEqual(result.story_scene.scene_id, 'casino-phone-setup')
        self.finish_linear_scene(result)
        result._b_battle.phase = 'win'
        result.record()
        result.page = 'result'
        result.key('\n')
        self.assertEqual(result.story_scene.scene_id, 'casino-payoff')
        self.assertIn(CASINO_SIGNAL, result.story_scene.scene.beats['start'].body)
        for k in ('1', '\n', '\n'):
            result.key(k)
        self.assertEqual(result.story_scene.beat, 'table')
        result.key('\n')
        self.assertEqual(result.story_scene.beat, 'change')
        result.key('\n')
        result.key('\n')
        self.assertEqual(result.page, 'result')
        self.assertIsNone(result.after_scene())
        self.assertTrue(Campaign(self.path).can_play('cruiser-guests'))

    def test_opener_primary_action_and_april_handoff_are_visibly_selectable(self):
        app = RecordedSurface(Campaign(self.path))
        app.w, app.h = 65, 25
        app.key('2')
        app.story_scene.draw(app)
        joined = ' '.join(t.strip() for _, _, t, *_ in app.calls)
        for phrase in ('NOVEMBER / CASINO', 'You’re Joker', 'just pulled off a heist',
                       'Take the service stairs', 'ENTER SELECT'):
            self.assertIn(phrase, joined)
        self.assertIn('Take the service stairs', next(t for _, _, t, _, bold, reverse
                                                     in app.calls if bold and reverse))
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'balcony')
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'arrest')
        app.reset()
        app.story_scene.draw(app)
        self.assertIn('cuff you', ' '.join(t.strip() for _, _, t, *_ in app.calls))
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'interrogation')
        app.reset()
        app.story_scene.draw(app)
        text = ' '.join(t.strip() for _, _, t, *_ in app.calls)
        self.assertIn('Prosecutor Sae Niijima', text)
        self.assertIn('start in April', text)
        self.assertTrue(any('TELL SAE HOW IT STARTED' in t and reverse for _, _, t, _, _, reverse in app.calls))
        app.key('\n')
        self.assertEqual(app.page, 'prologue')
        app.reset()
        app.story_panel()
        self.assertTrue(any('APRIL / SHUJIN' in t for _, _, t, *_ in app.calls))

    def test_opener_accepts_only_left_clicks_inside_the_button(self):
        app = RecordedSurface(Campaign(self.path))
        app.key('2')
        scene = app.story_scene
        y, x, label, _ = scene.primary_button()
        for point in ((0, x, y-1, 0, C.BUTTON1_CLICKED),
                      (0, x+len(label), y, 0, C.BUTTON1_CLICKED),
                      (0, x+2, y, 0, C.BUTTON3_CLICKED)):
            with patch('campaign_story.C.getmouse', return_value=point):
                app.key(C.KEY_MOUSE)
            self.assertEqual(scene.beat, 'start')
        with patch('campaign_story.C.getmouse', return_value=(0, x+2, y, 0, C.BUTTON1_CLICKED)):
            app.key(C.KEY_MOUSE)
            self.assertEqual(scene.beat, 'balcony')
            for beat in ('arrest', 'interrogation'):
                app.key(C.KEY_MOUSE)
                self.assertEqual(scene.beat, beat)
            app.key(C.KEY_MOUSE)
        self.assertEqual(app.page, 'prologue')

    def test_continue_restores_casino_april_and_the_escape_without_a_reward(self):
        def reopen():
            app = RecordedSurface(Campaign(self.path))
            self.assertTrue(app.key('1'))
            return app

        app = RecordedSurface(Campaign(self.path))
        app.key('2')
        app.key('\n')
        self.assertEqual(Campaign(self.path).data['story_opening'], 'casino:balcony')
        app.key(ESC)
        self.assertEqual(app.page, 'title')
        app = reopen()
        self.assertEqual(app.story_scene.beat, 'balcony')
        for _ in range(3):
            app.key('\n')
        self.assertEqual(app.page, 'prologue')
        app = reopen()
        self.assertEqual(app.page, 'prologue')
        before = Campaign(self.path).data
        app.key('\n')
        self.assertEqual((app.page, app.story_scene.scene_id), ('story-scene', 'castle-return'))
        app.key('\n')
        self.assertEqual(app.page, 'escape-fight')
        app = reopen()
        self.assertEqual(app.page, 'escape-fight')
        self.assertIs(app.escape_fight.battle.actor, app.escape_fight.battle.allies[0])
        for _ in range(4):
            if app.escape_fight.battle.phase == 'win':break
            app.key('1')
        self.assertEqual(app.escape_fight.battle.phase, 'win')
        app = reopen()
        self.assertEqual((app.page, app.story_scene.beat), ('story-scene', 'return'))
        self.finish_linear_scene(app)
        self.assertEqual(app.page, 'map')
        self.assertNotIn('story_opening', Campaign(self.path).data)
        before.pop('story_opening')
        self.assertEqual(Campaign(self.path).data, before)
        self.assertEqual(reopen().page, 'map')
        self.assertIsNone(story_offer('castle-gate', 'before'))
        app.key('h')
        self.assertEqual(app.page,'drill')

    def test_legacy_april_checkpoint_opens_the_condensed_scene(self):
        store=Campaign(self.path)
        store.new_game(opening=True)
        store.checkpoint_opening('april:2')
        app=RecordedSurface(Campaign(self.path))
        app.key('1')
        self.assertEqual(app.page,'prologue')
        app.key('\n')
        self.assertEqual(app.story_scene.scene_id,'castle-return')

    def test_the_press_is_an_actionable_gate_before_the_factory_battle(self):
        app=self.fixture('spaceport-factory')
        original=self.path.read_bytes()
        app.brief()
        self.assertTrue(any('ENTER CONSOLE' in t for _,_,t,*_ in app.calls))
        app.key('\n')
        self.assertEqual(app.page,'spaceport-press')
        app.key('1');app.key('\n')
        self.assertEqual(app.page,'spaceport-press')
        app.key(ESC)
        self.assertEqual(app.page,'brief')
        app.key('\n');app.key('2')
        self.assertEqual(app.page,'spaceport-press')
        app.key('\n')
        self.assertEqual(app.page,'battle')
        self.assertEqual(app._b_battle.config['id'],'spaceport-factory')
        self.assertEqual(original,self.path.read_bytes())

    def test_essential_debrief_cannot_be_lost_by_leaving_or_relaunching(self):
        app = self.fixture('castle-gate')
        app.deploy()
        if app.page == 'story-scene':
            self.finish_linear_scene(app)
        self.assertEqual(app.page, 'battle')
        app._b_battle.phase = 'win'
        app.record()
        app.page = 'result'
        self.assertEqual(Campaign(self.path).data['pending_story_after'], 'castle-gate')
        app.key('r')
        self.assertEqual(app.page, 'result')
        app.key(ESC)
        self.assertEqual(app.page, 'title')
        app = RecordedSurface(Campaign(self.path))
        app.key('1')
        self.assertEqual((app.page, app.story_scene.scene_id), ('story-scene', 'panther-joins'))
        button = app.story_scene.primary_button()
        self.assertIn('Hold the gate', button[2])
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'gate')
        app.key(ESC)
        self.assertEqual(app.page, 'title')
        app.key('1')
        self.finish_linear_scene(app)
        self.assertEqual(app.page, 'map')
        self.assertNotIn('pending_story_after', Campaign(self.path).data)
        self.assertEqual(Campaign(self.path).next_node, 'guardhouse')

    def test_future_recruits_stay_hidden_until_their_resumable_story_handoff(self):
        for operation,name in RECRUIT_HANDOFFS.items():
            with self.subTest(recruit=name):
                app=self.fixture(operation)
                app.stage()
                app._b_battle.phase='win'
                app.record()
                app.page='result'
                app.reset()
                app.result()
                self.assertNotIn(name, ' '.join(app.out))
                app.key('s');app.reset();app.draw_squad()
                self.assertNotIn(name,' '.join(app.out))
                self.assertNotIn(name,Campaign(self.path).data['teammates'])
                resumed=RecordedSurface(Campaign(self.path))
                resumed.key('1')
                self.assertEqual(resumed.page,'story-scene')
                self.finish_linear_scene(resumed)
                self.assertIn(name,Campaign(self.path).data['teammates'])
                self.assertIn('joined your roster',resumed.notice)

    def test_classic_trials_only_open_in_battle_practice(self):
        app=self.fixture('castle-gate')
        app.key(ESC);app.key('s')
        self.assertEqual(app.squad_names(),['Joker','Mona','Skull'])
        app.key(ESC);app.key('t')
        self.assertEqual(app.page,'map')
        app.reset();app.draw_map()
        self.assertNotIn('T CLASSIC TRIALS',' '.join(app.out))
        self.assertNotIn('Panther',' '.join(app.out))
        testing=RecordedSurface(Campaign(self.path))
        testing.begin_extra('practice');testing.key('t')
        self.assertEqual(testing.page,'trials')

    def test_completed_coda_returns_to_explicit_end_menu_and_reopens_it(self):
        app=self.fixture('laboratory-choice')
        app.stage();app._b_battle.phase='win';app.record();app.page='result'
        app.key('\n');self.finish_linear_scene(app)
        self.assertEqual(app.page,'campaign-complete')
        self.assertNotIn('pending_story_after',Campaign(self.path).data)
        app.reset();app.draw_campaign_complete()
        for label in ('CAMPAIGN COMPLETE','Return to Title','Replay Operations'):
            self.assertIn(label,' '.join(app.out))
        app.key('2')
        self.assertEqual(app.page,'map')
        reopened=RecordedSurface(Campaign(self.path));reopened.key('1')
        self.assertEqual(reopened.page,'campaign-complete')
        reopened.key('\n')
        self.assertEqual(reopened.page,'title')

    def test_mural_action_selection_keeps_optional_continue_on_its_own_row(self):
        scene=StoryScene('pyramid-inspect')
        self.assertTrue(scene.mouse_enabled())
        self.assertTrue(any('CONTINUE TO COMBAT' in r[2] for r in scene.choice_buttons()))
        scene.key(C.KEY_DOWN);scene.key('\n')
        self.assertEqual(scene.beat,'fragment1')
        scene.key(C.KEY_DOWN);scene.key('\n')
        self.assertEqual(scene.beat,'fragment2')
        self.assertEqual(scene.clues,{PYRAMID_MOTIF})
        self.assertTrue(scene.key('\n'))

    def test_satanael_art_is_native_at_both_supported_sizes(self):
        for w,h in ((64,25),(99,35)):
            renders=[cinema.paint(SATANAEL_CUT,t,w,h) for t in (.3,.89,1.75,2.28)]
            self.assertEqual([stage for stage,_ in renders],['city','manifest','charge','shell'])
            for _,rows in renders:
                self.assertEqual(len(rows),h)
                self.assertTrue(all(sum(len(run) for run,_ in row)==w for row in rows))

    def finish_linear_scene(self, app):
        for _ in range(16):
            if app.page != 'story-scene':
                return
            beat = app.story_scene.scene.beats[app.story_scene.beat]
            app.key('\n' if beat.enter else beat.choices[0][0])
        self.fail('Story did not reach a handoff.')

    def test_mural_skip_does_not_write_and_exact_recall_survives_reopen(self):
        app = self.fixture('pyramid-murals')
        before = self.path.read_bytes()
        app.key('\n')
        self.assertEqual(app.story_scene.scene_id, 'pyramid-inspect')
        app.key('\n')
        self.assertEqual(app.page, 'battle')
        self.assertEqual(before, self.path.read_bytes())

        app.page = 'brief'
        app.key('\n')
        app.key('2')
        self.assertEqual(before, self.path.read_bytes())
        app.key('1')
        self.assertEqual(Campaign(self.path).data['story_clues'], [PYRAMID_MOTIF])
        app.key(ESC)
        self.assertEqual(app.page, 'brief')
        app = RecordedSurface(Campaign(self.path))
        app.key('1')
        app.ch = next(i for i,c in enumerate(CHAPTERS) if c['id'] == 'pyramid')
        app.key('4')
        save = self.path.read_bytes()
        app.key('c')
        self.assertEqual(app.story_scene.scene_id, 'pyramid-recall')
        beat = app.story_scene.scene.beats['start']
        self.assertEqual((beat.heading, beat.body), PYRAMID_FRAGMENTS[0])
        app.key('\n')
        beat = app.story_scene.scene.beats[app.story_scene.beat]
        self.assertEqual((beat.heading, beat.body), PYRAMID_FRAGMENTS[1])
        app.key(ESC)
        self.assertEqual(app.page, 'brief')
        self.assertEqual(save, self.path.read_bytes())
        self.assertIsNone(story_offer('pyramid-boss', 'review'))
        self.assertEqual(StoryScene('pyramid-recognition').beat, 'unseen')
        self.assertEqual(StoryScene('pyramid-recognition', seen_clues=[PYRAMID_MOTIF]).beat, 'start')

    def test_maruki_hear_him_out_is_not_acceptance_and_esc_does_not_commit(self):
        app = self.fixture('laboratory-choice')
        before = self.path.read_bytes()
        app.key('\n')
        self.assertEqual(app.story_scene.scene_id, 'maruki-offer')
        app.key('1')
        self.assertEqual(app.story_scene.beat, 'hear')
        app.key('2')
        self.assertEqual(app.story_scene.beat, 'sumire')
        app.key(ESC)
        self.assertEqual(app.page, 'brief')
        self.assertEqual(self.path.read_bytes(), before)
        app.key('\n')
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'hear')
        app.key('3')
        self.assertEqual(app.story_scene.beat, 'reject')
        app.key('\n')
        self.assertEqual(app.page, 'battle')
        self.assertEqual(self.path.read_bytes(), before)

    def test_futaba_can_act_without_clue_and_a_cleared_coda_can_be_revisited(self):
        app = self.fixture('pyramid-boss')
        app.key('\n')
        self.assertEqual(app.story_scene.beat, 'unseen')
        app.key('1')
        app.key('\n')
        self.assertEqual(app.page, 'battle')
        app._b_battle.round = 3
        on_round(app._b_battle)
        self.assertTrue(app._b_battle.actions('story-special'))
        app = self.fixture('laboratory-choice')
        app.store.clear('laboratory-choice', 'S')
        original = self.path.read_bytes()
        app.key('c')
        self.assertEqual(app.story_scene.scene_id, 'maruki-coda')
        app.key('1')
        self.assertEqual(app.story_scene.beat, 'hold')
        for _ in range(2):
            app.key('\n')
        self.assertEqual(app.page, 'brief')
        self.assertEqual(original, self.path.read_bytes())

    def test_all_beats_fit_compact_and_wide_chrome(self):
        app = RecordedSurface(Campaign(self.path))
        for app.w, app.h in ((65, 25), (100, 35)):
            for scene_id, scene in SCENES.items():
                view = StoryScene(scene_id)
                for stage, beat in scene.beats.items():
                    with self.subTest(width=app.w, scene=scene_id, beat=stage):
                        view.beat = stage
                        app.reset()
                        view.draw(app)
                        self.assertEqual(sum(beat.heading in call[2] for call in app.calls), 1)
                        self.assertTrue(all(0 <= row < app.h-1 and col + len(label) <= app.w-1
                                            for row,col,label,*_ in app.calls))
                        self.assertEqual(sum('ESC ' in t for row,col,t,*_ in app.calls if row == app.h-2), 1)


if __name__ == '__main__':
    unittest.main()
