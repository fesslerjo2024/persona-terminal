"""Curses drawing primitives shared by the suite and its live campaign."""
import curses as C
from battle_ui import BattleUI, WHITE


class TerminalSurface(BattleUI):
    def put(self,y,x,text,color=WHITE,b=False,reverse=False):
        if 0<=y<self.h and 0<=x<self.w-1:
            try:
                self.s.addnstr(y,x,str(text),self.w-1-x,
                               C.color_pair(color)|(C.A_BOLD if b else 0)|(C.A_REVERSE if reverse else 0))
            except C.error:pass

    def mid(self,y,text,color=WHITE,b=False):
        self.put(y,max(0,(self.w-len(text))//2),text,color,b)
