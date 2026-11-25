"""Curses drawing primitives shared by the suite and its live campaign."""
import curses as C
from .reel_palette import IDS as SCENE_PIGMENTS
from .terminal_constants import CYAN, DIM, ENTER, GOLD, GREEN, RED, WHITE


class MenuSurface:
    """Shared list drawing and navigation; no combat imports."""

    def _b_put(self,y,x,msg,color=WHITE,bold=False,reverse=False,width=None):
        if width is not None:msg=msg[:max(0,width)]
        self.put(y,x,msg,color,bold,reverse)

    def _b_list(self,rows,y,x,w,h,idx,shortcut=True,details=True,marks=()):
        """Rows are (title, detail, enabled); return selected row."""
        if not rows:
            self._b_put(y,x,'Nothing available.',DIM,width=w)
            return
        i=max(0,min(idx,len(rows)-1))
        step=2 if details and h>=len(rows)*2 and self.w>=78 else 1
        visible=max(1,h//step)
        start=min(max(0,i-visible//2),max(0,len(rows)-visible))
        for n,row in enumerate(rows[start:start+visible],start):
            title,detail,enabled=row
            a=n==i
            p=('▶' if a else ' ')+' '+((f'{n+1:>2} ' if n<9 else '   ') if shortcut else '')
            color=CYAN if a else WHITE if enabled else DIM
            row_y=y+(n-start)*step
            mark=marks[n] if marks else None
            if mark:
                glyph,ink=mark
                room=max(0,w-len(p)-2)
                name,sep,badges=title.partition(' [')
                badge=(sep+badges)[:room]
                name=name[:max(0,room-len(badge))]
                self._b_put(row_y,x,p,color,a,a,width=w)
                self._b_put(row_y,x+len(p),name,ink,a)
                self._b_put(row_y,x+len(p)+len(name),badge,WHITE if enabled else DIM)
                self._b_put(row_y,x+len(p)+len(name)+len(badge)+1,glyph,ink,a)
            elif not enabled:
                self._b_put(row_y,x,p,color,a,a,width=w)
                self._b_put(row_y,x+len(p),title,DIM,width=w-len(p))
            else:
                line=(p+title)[:w].ljust(w)
                self._b_put(row_y,x,line,color,a,a,width=w)
            if step==2:self._b_put(y+(n-start)*step+1,x+len(p),detail,DIM,width=w-len(p))
        return rows[i]

    @staticmethod
    def _b_nav(k,i,n):
        if k in (C.KEY_UP,'k','K'):return (i-1)%max(1,n)
        if k in (C.KEY_DOWN,'j','J'):return (i+1)%max(1,n)
        if k==C.KEY_HOME:return 0
        if k==C.KEY_END:return max(0,n-1)
        if k==C.KEY_PPAGE:return max(0,i-5)
        if k==C.KEY_NPAGE:return min(max(0,n-1),i+5)
        return i

    @staticmethod
    def _b_commit(k,i,n):
        if k in ENTER:return i
        if isinstance(k,str) and k in '123456789' and int(k)<=n:return int(k)-1
        return None

    def draw_scene_rows(self,rows):
        """Paint to the current terminal bounds, not a fixed picture box."""
        inks={'queen':CYAN,'noir':GOLD,'foe':RED,'rope':DIM,
              'rail':RED,'face':WHITE,'dim':DIM,'flash':GOLD,
              'red':RED,'gold':GOLD,'cyan':CYAN,'green':GREEN,'white':WHITE,
              **SCENE_PIGMENTS}
        shade={'dim','rope','slate','navy','forest','ochre','wine','ink','indigo','plum','umber','moss'}
        for y,row in enumerate(rows):
            x=0
            for run,ink in row:
                if run.strip():self._b_put(y,x,run,inks[ink],ink not in shade)
                x+=len(run)



class TerminalSurface(MenuSurface):
    @staticmethod
    def _mouse(mask):
        try:C.mousemask(mask)
        except C.error:pass  # Keyboard remains available with no mouse reporting.

    def put(self,y,x,text,color=WHITE,b=False,reverse=False):
        if 0<=y<self.h and 0<=x<self.w-1:
            try:
                self.s.addnstr(y,x,str(text),self.w-1-x,
                               C.color_pair(color)|(C.A_BOLD if b else 0)|(C.A_REVERSE if reverse else 0))
            except C.error:pass

    def mid(self,y,text,color=WHITE,b=False):
        self.put(y,max(0,(self.w-len(text))//2),text,color,b)
