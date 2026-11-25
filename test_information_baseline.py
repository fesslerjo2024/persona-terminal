import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import campaign_data
from campaign_combat import build_stage
from campaign_state import Campaign, DEFAULT_SAVE
from test_animation_gallery import Surface


class InformationBaselineTests(unittest.TestCase):
    def test_default_save_keeps_established_path(self):
        self.assertEqual(DEFAULT_SAVE.name,'campaign-save.json')
        self.assertEqual(Campaign().path,DEFAULT_SAVE)

    def test_title_names_the_product_once(self):
        with tempfile.TemporaryDirectory() as d:
            app=Surface(Campaign(Path(d)/'absent.json'))
            app.title()
            self.assertEqual(sum('Persona 5 Terminal' in row for row in app.out),1)
            self.assertFalse(any('INFILTRATION  /  FIGHT-ONLY' in row for row in app.out))

    def test_briefing_uses_actual_solo_deployment_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'absent.json'
            app=Surface(Campaign(path))
            app.start_testing()
            node=next(n for n in campaign_data.NODES if n.get('party_size')==1)
            app.node=node
            app.ch=next(i for i,ch in enumerate(app.chapters) if node in ch['nodes'])
            app.brief()
            lines=[line for line in app.out if 'SQUAD:' in line]
            self.assertEqual(len(lines),1)
            self.assertTrue(lines[0].endswith('SQUAD: Joker'))
            self.assertEqual([p.name for p in build_stage(app.store,node['id'],1).allies],['Joker'])
            self.assertFalse(path.exists())

    def test_map_shortcut_text_only_in_footer_at_both_widths(self):
        with tempfile.TemporaryDirectory() as d:
            app=Surface(Campaign(Path(d)/'absent.json'))
            app.start_testing()
            for width,height in ((65,25),(96,34)):
                app.w,app.h=width,height
                with patch.object(app,'put',wraps=app.put) as draw:
                    app.draw_map()
                messages=[args for args,_ in draw.call_args_list]
                for label in ('G ANIMATION GALLERY','T CLASSIC TRIALS','ESC TITLE'):
                    rows=[y for y,x,text,*_ in messages if label in text]
                    self.assertEqual(rows,[height-2])
                self.assertFalse(any('Enter for briefing' in text for _,_,text,*_ in messages))
