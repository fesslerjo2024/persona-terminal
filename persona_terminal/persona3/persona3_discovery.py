"""Scene routing and presentation for the campaign's story discoveries."""
from datetime import timedelta
from importlib import import_module
from time import monotonic
from textwrap import wrap

from persona_terminal.shared.terminal_constants import ESC, WHITE

MODULE_FOR={
    **dict.fromkeys(('arrival','fuuka','bunker'),'persona3_spring_discoveries'),
    **dict.fromkeys(('villa','shore','recording'),'persona3_recording_discoveries'),
    **dict.fromkeys(('pharos-visit','shinjiro','club','medea'),'persona3_autumn_discoveries'),
    **dict.fromkeys(('bridge','roof','pharos-farewell'),'persona3_winter_discoveries'),
}
_PROMISE=('promise',{
    'promise':('JANUARY 31 / BEFORE THE CLIMB','dorm',
        ('Yukari: If we forget what happens tonight, let’s still meet after graduation.',
         'Aigis looks up. “On the school roof?”'),
        (('Promise to be there','reply'),('Admit you’re scared','reply_scared'))),
    'reply':('JANUARY 31 / THE PROMISE','dorm',
        ('Makoto nods. One by one, everyone says they’ll be there.',),
        (('Go to Tartarus',None),)),
    'reply_scared':('JANUARY 31 / THE PROMISE','dorm',
        ('Yukari admits she’s scared, too. She asks again anyway. This time, everyone answers.',),
        (('Go to Tartarus',None),)),
})


def scene(key):
    if key=='promise':
        return _PROMISE
    if key in ('station-aftermath','bridge-aftermath'):
        module=import_module('.persona3_station_scene' if key=='station-aftermath' else '.persona3_betrayal_scene', __package__)
        return module.ENTRY,module.SCENE
    return import_module(f'.{MODULE_FOR[key]}', __package__).SCENES[key]


def draw(app, node, elapsed, *, day=None, key=''):
    title,art,body,choices=node
    footer='↑↓ SELECT  ENTER CHOOSE  ESC TITLE' if len(choices)>1 else 'ENTER CONTINUE  ESC TITLE'
    app.frame(title,footer,status=day.strftime('%m/%d  %a').upper() if day else '')
    if art=='arrival':
        from .persona3_opening import TRANSITION_SECONDS
        app.art('arrival',TRANSITION_SECONDS,height=7)
    elif art=='villa-shore':
        from .persona3_yabbashah import shore
        app.draw_scene_rows(shore(0 if key=='villa' else 1,app.w-5,7),top=5,left=2)
    elif art=='club':
        from .persona3_club_art import render
        app.draw_scene_rows(render(app.w-5,7),top=5,left=2)
    else:
        app.ending_art(art,height=7,seconds=elapsed if art in ('station-alley','tartarus-roof') else None)
    row=12
    for paragraph in body:
        for line in wrap(paragraph,app.w-8):
            app.put(row,4,line,WHITE)
            row+=1
    app.choices(tuple(label for label,_ in choices),max(16,row+1),4,step=1)


class DiscoveryRoute:
    def discover(self,key):
        self.discovery_key=key
        self.discovery_step, self.discovery_nodes=scene(key)
        self.discovery_started=monotonic()
        self.go('discovery')

    def draw_discovery(self):
        day=self.record.day
        if self.discovery_key=='bridge':
            from .persona3_winter_discoveries import BRIDGE_NEXT_DAY
            if self.discovery_step in BRIDGE_NEXT_DAY:day+=timedelta(days=1)
        elif self.discovery_key=='medea' and self.discovery_step!='morning':
            day-=timedelta(days=1)
        draw(self,self.discovery_nodes[self.discovery_step],
             monotonic()-self.discovery_started,day=day,key=self.discovery_key)

    def _discovery_key(self,k):
        if k==ESC:self.exit=True;return
        choices=self.discovery_nodes[self.discovery_step][3]
        pick=self.choose(k,len(choices))
        if pick is None:return
        _,target=choices[pick]
        if target is not None:
            self.discovery_step=target
            self.i=0
        else:
            self._finish_discovery()

    def _finish_discovery(self):
        key=self.discovery_key
        if key=='arrival':
            from .persona3_state import AWAKENING
            if self.write(self.store.commit,phase='awakening',day=AWAKENING):self.resume()
        elif key=='fuuka':
            self.recovery_seen=True
            self.open_battle('emperor-empress')
        elif key in ('villa','shore'):
            if self.write(self.store.trip_next):self.resume()
        elif key=='pharos-farewell':
            self.start_aftermath()
        elif key=='roof':
            if self.write(self.store.ending_next):
                self.ending_index=0
                self.resume()
        elif self.write(self.store.finish_discovery):
            if self.record.phase=='calendar':self.go('calendar')
            else:self.resume()
