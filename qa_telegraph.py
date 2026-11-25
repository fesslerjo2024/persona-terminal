"""Read-only 65x25 boss-telegraph keyboard QA (optional pexpect dependency).

Launches the real campaign app with a temporary absent save, enters Testing Mode,
and mirrors the actions in a second deterministic engine instance for telemetry.
Neither instance opens the default save. Run: python -B qa_telegraph.py [--no-wakaba]
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import hashlib
import os
import re
import sys
import time
import pexpect

from campaign_combat import build_stage
from campaign_data import CHAPTERS
from campaign_state import TestingCampaign

ROOT=Path(__file__).resolve().parent
ENTER,ESC,RIGHT='\r','\x1b','\x1bOC'
CONTROL=re.compile(r'\x1b(?:\[[0-?]*[ -/]*[@-~]|\([ -~]|\)[ -~]|[=>78DEHMNOc]|\][^\x07]*\x07)')

class Screen:
    def __init__(self,rows,cols):
        self.rows,self.cols=rows,cols
        self.lines=[[' ']*cols for _ in range(rows)]
        self.y=self.x=0
        self.top,self.bottom=0,rows-1
        self.pending=''
        self.unsupported=set()
    def chars(self,txt):
        for c in txt:
            if c=='\r':self.x=0
            elif c=='\n':self.y=min(self.rows-1,self.y+1)
            elif c=='\b':self.x=max(0,self.x-1)
            elif c=='\t':self.x=min(self.cols-1, (self.x//8+1)*8)
            elif ord(c)>=32 and self.y<self.rows and self.x<self.cols:
                self.lines[self.y][self.x]=c
                self.x+=1
    def handle(self,t):
        if not t.startswith('\x1b['):
            return
        seq=t[2:-1]
        end=t[-1]
        if seq.startswith(('?','>')) or end in 'mthl':
            return
        a=[int(x) if x else 0 for x in seq.split(';')] if seq else []
        n=a[0] if a and a[0] else 1
        if end in 'fH':
            self.y=n-1
            self.x=(a[1] if len(a)>1 and a[1] else 1)-1
        elif end in 'dG': 
            if end=='d':self.y=n-1
            else:self.x=n-1
        elif end in 'ABCD':
            if end=='A':self.y=max(0,self.y-n)
            if end=='B':self.y=min(self.rows-1,self.y+n)
            if end=='C':self.x=min(self.cols,self.x+n)
            if end=='D':self.x=max(0,self.x-n)
        elif end=='K':
            if not a or a[0]==0:self.lines[self.y][self.x:]=[' ']*(self.cols-self.x)
            elif a[0]==1:self.lines[self.y][:self.x+1]=[' ']*(self.x+1)
            elif a[0]==2:self.lines[self.y]=[' ']*self.cols
        elif end=='J':
            if a and a[0]==2:self.lines=[[' ']*self.cols for _ in range(self.rows)]
            else:
                self.lines[self.y][self.x:]=[' ']*(self.cols-self.x)
                self.lines[self.y+1:]=[[' ']*self.cols for _ in self.lines[self.y+1:]]
        elif end=='r':
            self.top=(a[0] if a and a[0] else 1)-1
            self.bottom=(a[1] if len(a)>1 and a[1] else self.rows)-1
            self.y=self.x=0
        elif end in 'P@':
            line=self.lines[self.y]
            if end=='P':
                line[self.x:]= (line[self.x+n:]+[' ']*n)[:self.cols-self.x]
            else:
                line[self.x:]= ([' ']*n+line[self.x:])[:self.cols-self.x]
        elif end in 'STLM':
            a=self.y if end in 'LM' else self.top
            b=self.bottom+1
            old=self.lines[a:b]
            blanks=[[' ']*self.cols for _ in range(min(n,len(old)))]
            self.lines[a:b]=old[n:]+blanks if end in 'SM' else blanks+old[:max(0,len(old)-n)]
        elif end=='X':
            self.lines[self.y][self.x:self.x+n]=[' ']*min(n,self.cols-self.x)
        elif end=='b':
            if self.x>0:self.chars(self.lines[self.y][self.x-1]*n)
        else:
            self.unsupported.add(t)
    def feed(self,txt):
        txt=self.pending+txt
        self.pending=''
        while txt:
            esc=txt.find('\x1b')
            if esc==-1:self.chars(txt);return
            self.chars(txt[:esc])
            txt=txt[esc:]
            m=CONTROL.match(txt)
            if not m:
                self.pending=txt
                return
            self.handle(m[0])
            txt=txt[len(m[0]):]
    def dump(self):return '\n'.join(''.join(line).rstrip() for line in self.lines)

class Terminal:
    def __init__(self,save,seed):
        self.screen=Screen(25,65)
        self.proc=pexpect.spawn(sys.executable,['-B',str(ROOT/'campaign.py'),'--save',str(save),'--seed',str(seed)],
            cwd=ROOT,env={**os.environ,'TERM':'xterm-256color','ESCDELAY':'25'},encoding='utf8',dimensions=(25,65))
        self.need('', 'NEW GAME', .4)

    def keys(self,key='',delay=.18):
        if key:self.proc.send(key)
        until=time.monotonic()+delay
        while (left:=until-time.monotonic())>0:
            try:self.screen.feed(self.proc.read_nonblocking(65536,timeout=left))
            except pexpect.TIMEOUT:break
        return self.screen.dump()

    def need(self,key,expected,delay=.18):
        screen=self.keys(key,delay)
        if expected not in screen:screen=self.keys('',.42)
        assert expected in screen,(expected,screen)
        return screen

    def close(self):
        try:self.proc.send('q');self.proc.expect(pexpect.EOF,timeout=3)
        finally:self.proc.close()

    def launch(self,node,b):
        ch,index=next((i,j) for i,c in enumerate(CHAPTERS) for j,n in enumerate(c['nodes']) if n['id']==node)
        self.need('3','TESTING MODE')
        if ch:self.need(RIGHT*ch,CHAPTERS[ch]['id'].upper()+' MAP')
        self.need(str(index+1),'OPERATION BRIEF')
        return self.need(ENTER,'NOW '+b.actor.name)

def actions(term,b,screen,aid,expected_hint=None):
    target=b.targets(aid)[0] if aid=='attack' else None
    old=b.actor.name
    status=b.act(aid,target)
    assert status is None,(aid,status)
    key={'guard':'4','attack':'21','story-special':'9'}[aid]
    screen=term.need(key,'NOW '+b.actor.name,.23)
    if expected_hint:assert expected_hint in screen,screen
    return screen,old

def line(screen,fragment):
    return next((row.strip() for row in screen.splitlines() if fragment in row),None)

def bank(seed,mode,save):
    b=build_stage(TestingCampaign(),'bank-boss',seed)
    term=Terminal(save,seed)
    try:
        screen=term.launch('bank-boss',b)
        opener=b.actor.name
        before_steps=0
        while not b.story_intent.startswith('MARCH OF THE PIGGY'):
            screen,_=actions(term,b,screen,'guard')
            before_steps+=1
            assert before_steps<20
        warning=line(screen,'MARCH OF THE PIGGY')
        assert warning and 'Guard or 9: offer bait.' in warning,screen
        actor=b.actor.name;rnd=b.round
        hp={u.name:u.hp for u in b.allies}
        doses=b.items['Medicine']
        opportunity=[]
        if mode=='bait':
            screen,name=actions(term,b,screen,'story-special')
            opportunity.append(name)
            assert b.items['Medicine']==doses-1 and 'pending' not in b._boss_state
            screen=term.need('l','The Medicine distracts Piggytron.')
            assert 'The charge stops.' in ' '.join(screen.split())
            term.need('l','NOW')
            # Check the visible supply decrement as well, not just engine data.
            term.need('5',f'Medicine ×{doses-1}')
        else:
            while b.story_intent.startswith('MARCH OF THE PIGGY'):
                screen,name=actions(term,b,screen,'guard' if mode=='guard' else 'attack')
                opportunity.append(name)
                assert len(opportunity)<=len(b.allies)+1
            screen=term.need('l','March of the Piggy')
            if mode=='guard':assert '[GUARD]' in screen
            assert b.items['Medicine']==doses
        if mode!='bait':term.need('l','NOW')
        status=term.need('i','FIELD STATUS')
        for u in b.allies:
            assert any(row.strip().startswith(u.name) and f'HP {u.hp}/{u.max_hp}' in row
                       for row in status.splitlines()),(u.name,u.hp,status)
        assert not save.exists()
        loss={u.name:hp[u.name]-u.hp for u in b.allies}
        print(f'Bank {mode}: opener={opener}; first warning round {rnd}, {actor} after {before_steps} inputs; '
              f'actors={opportunity}; HP loss={loss}; Medicine {doses}->{b.items["Medicine"]}; "{warning}"')
        return hp,loss,warning
    finally:term.close()

def pressure(seed,save):
    """Use strongest available damage from the *same* stock roster."""
    b=build_stage(TestingCampaign(),'bank-boss',seed)
    term=Terminal(save,seed)
    try:
        screen=term.launch('bank-boss',b)
        hits=[]
        while b.wave==1 and b.phase=='turn' and not b.story_intent.startswith('MARCH OF THE PIGGY'):
            foe=b.enemies[0]
            choices=[]
            for index,(aid,label,_) in enumerate(b.actions('skills')):
                spec=b._spec(aid)
                if spec['kind']!='damage':continue
                target=foe if spec['target']=='enemy' else None
                if b.action_block(aid,target):continue
                choices.append((spec['power'],index,aid,label,target))
            assert choices and len(hits)<14,(b.actor.name,b.log)
            power,index,aid,label,target=max(choices,key=lambda row:row[0])
            old=b.actor.name
            assert b.act(aid,target) is None
            screen=term.keys('1'+str(index+1)+('1' if target else ''),.23)
            if 'NEXT FORMATION INCOMING' in screen:screen=term.keys('',.72)
            if b.phase=='turn' and 'NOW '+b.actor.name not in screen:screen=term.keys('',.42)
            assert b.phase!='turn' or 'NOW '+b.actor.name in screen,screen
            hits.append(f'{old}: {label}')
        warn=line(screen,'MARCH OF THE PIGGY')
        assert bool(warn)==bool(b.wave==1 and b.story_intent.startswith('MARCH OF THE PIGGY')),screen
        assert not save.exists()
        print(f'Bank direct damage: {hits}; warning={warn!r}; '
              f'Piggytron HP={b.enemies[0].hp if b.wave==1 else 0}; wave={b.wave}')
    finally:term.close()

def wakaba(seed,save):
    b=build_stage(TestingCampaign(),'pyramid-boss',seed)
    term=Terminal(save,seed)
    try:
        screen=term.launch('pyramid-boss',b);opener=b.actor.name
        assert line(screen,'WAKABA AIRBORNE') and 'Use skills or Gun.' in screen
        dive=None
        before_steps=0
        while not b.story_intent.startswith('BALLISTA READY'):
            if not dive and b.story_intent.startswith('SPHINX DIVE'):
                warn=line(screen,'SPHINX DIVE')
                assert warn and 'Guard before impact.' in warn
                dive=(b.round,b.actor.name,warn)
            screen,_=actions(term,b,screen,'guard')
            before_steps+=1
            assert before_steps<28
        ready=line(screen,'BALLISTA READY')
        assert ready and 'Press 9 to ground Wakaba.' in ready
        actor=b.actor.name;rnd=b.round;old=b.enemies[0].hp
        screen,_=actions(term,b,screen,'story-special','WAKABA GROUNDED')
        hits=old-b.enemies[0].hp
        assert hits==90
        log=term.need('l','The ballista hits.')
        assert 'Wakaba is grounded!' in log and 'Sphinx Dive' in log
        assert not save.exists()
        print(f'Wakaba: opener={opener}; dive={dive}; first ballista banner round {rnd}, {actor} after {before_steps} inputs; '
              f'ballista={hits} direct HP; "{ready}"')
    finally:term.close()

def sae(seed,save):
    b=build_stage(TestingCampaign(),'casino-heist',seed)
    term=Terminal(save,seed)
    try:
        screen=term.launch('casino-heist',b)
        opening=line(screen,'ROULETTE OPENING')
        assert opening and 'Guard and watch the wheel.' in opening
        hp=b.enemies[0].hp
        screen,_=actions(term,b,screen,'attack')
        assert b.enemies[0].hp==hp
        early=1
        while not b.story_intent.startswith('RIGGED ROULETTE'):
            screen,_=actions(term,b,screen,'guard')
            early+=1
            assert early<=8
        warning=line(screen,'RIGGED ROULETTE')
        assert warning and '9: Break the glass.' in warning
        control=b.actor.name
        screen,_=actions(term,b,screen,'story-special')
        assert b._boss_state.get('sae_open') and not b.actions('story-special')
        term.need('l','breaks the glass lid.')
        term.need('l','NOW')
        screen,_=actions(term,b,screen,'attack')
        lost=hp-b.enemies[0].hp
        assert lost>0
        term.need('l',f'Sae Leviathan takes {lost} damage')
        assert not save.exists()
        print(f'Sae: initial melee did zero; warning on {control} after {early} input(s); '
              f'actual 9 broke glass and next melee landed {lost} HP. "{opening}" / "{warning}"')
    finally:term.close()

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--seed',type=int,default=2)
    cli.add_argument('--no-wakaba',action='store_true')
    cli.add_argument('--no-sae',action='store_true')
    args=cli.parse_args()
    for name in ('battle_engine.py','battle_ui.py','weekend_bosses.py','campaign.py'):
        print(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),name)
    with TemporaryDirectory(prefix='phantom-telegraph-') as dr:
        save=Path(dr)/'absent.json'
        bait,guard,ignore=[bank(args.seed,m,save) for m in ('bait','guard','ignore')]
        assert bait[0]==guard[0]==ignore[0], (bait,guard,ignore)
        assert sum(bait[1].values())<sum(guard[1].values())<sum(ignore[1].values()),(bait,guard,ignore)
        pressure(args.seed,save)
        if not args.no_wakaba:wakaba(args.seed,save)
        if not args.no_sae:sae(args.seed,save)

if __name__=='__main__':main()
