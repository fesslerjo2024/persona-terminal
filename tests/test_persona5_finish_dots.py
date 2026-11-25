"""All supported Persona 5 finish/support cues use native, animated microdot art."""
import unittest

from persona_terminal.persona5 import cinema
from persona_terminal.persona5 import cutins


def picture(frame):
    return tuple(''.join(run for run,_ in row) for row in frame)


def population(frame):
    return sum(sum('\u2801' <= ch <= '\u28ff' for ch in row) for row in picture(frame))


class FinishDotTests(unittest.TestCase):
    def test_all_finish_and_oracle_frames_are_native_and_change_with_time(self):
        titles=[card[0] for card in (*cutins.ALL_OUT.values(),cutins.ORACLE,cutins.ORACLE_SUPPORT,cutins.FINAL_GUARD)]
        closings=set()
        for w,h in ((65,25),(96,35)):
            for title in titles:
                with self.subTest(title=title,w=w,h=h):
                    samples=[cinema.paint(title,t,w,h,cast=('Joker','Noir','Mona'),targets=2)[1]
                             for t in (.22,.73,1.44,cinema.duration(title)-.06)]
                    for frame in samples:
                        self.assertEqual(len(frame),h)
                        self.assertEqual({len(row) for row in picture(frame)},{w})
                        self.assertGreater(population(frame),w*h*.029)
                    self.assertEqual(len(set(samples)),4)
                    if w==96:closings.add(samples[-1])
        self.assertEqual(len(closings),len(titles))

    def test_contextual_oracle_cast_and_payload_targets_actually_change_picture(self):
        for title,t in ((cutins.ORACLE_SUPPORT[0],1.6),(cutins.FINAL_GUARD[0],1.6)):
            with self.subTest(title=title):
                solo=cinema.paint(title,t,65,25,cast=('Mona',))
                team=cinema.paint(title,t,65,25,cast=('Joker','Mona','Noir','Violet'))
                self.assertNotEqual(solo,team)
        title=cutins.ORACLE[0]
        self.assertNotEqual(cinema.paint(title,1.2,96,35,targets=1),
                            cinema.paint(title,1.2,96,35,targets=4))
