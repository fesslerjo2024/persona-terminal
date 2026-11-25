"""Non-blocking screen presentation for changes to Persona 3 resource meters."""
from math import ceil
from time import monotonic

HOLD_SECONDS=.12
DRAIN_SECONDS=.40
TOTAL_SECONDS=HOLD_SECONDS+DRAIN_SECONDS


def meter_cells(value,maximum,width):
    """Keep zero, nonzero and full distinct at compact widths."""
    width=max(0,width)
    value=max(0,min(value,maximum))
    if not value or not width:return 0
    if value==maximum:return width
    return max(1,min(width-1,round(width*value/maximum)))


class MeterTrails:
    """Track presentation-only decreases; callers own the exact resources."""
    def __init__(self):
        self._losses={}

    @staticmethod
    def _remaining(elapsed):
        phase=max(0.,min(1.,(elapsed-HOLD_SECONDS)/DRAIN_SECONDS))
        return 1.-phase*phase*(3.-2.*phase)

    def record(self,key,before,after,now=None):
        """Start a trail on a real net loss, or clear it on recovery."""
        if before==after:return
        if after>before:
            self._losses.pop(key,None)
            return
        now=monotonic() if now is None else now
        old=self._losses.get(key)
        if old is not None:
            start,target,begun=old
            before=max(before,target+(start-target)*self._remaining(now-begun))
        self._losses[key]=(before,after,now)

    def active(self,now=None,*,settle=0.):
        now=monotonic() if now is None else now
        return any(now-begun<TOTAL_SECONDS+settle for _,_,begun in self._losses.values())

    def segments(self,key,current,maximum,width,now=None):
        """Return counts for steady meter, animated trail and empty track."""
        width=max(0,width)
        steady=meter_cells(current,maximum,width)
        loss=self._losses.get(key)
        if not width or loss is None:return steady,0,width-steady
        now=monotonic() if now is None else now
        before,after,begun=loss
        if current!=after or now-begun>=TOTAL_SECONDS:return steady,0,width-steady
        previous=meter_cells(before,maximum,width)
        # Even a loss below one visual cell is a visible color change.
        if previous==steady and steady:steady-=1
        tail=min(width-steady,ceil(max(0,previous-steady)*self._remaining(now-begun)))
        return steady,tail,width-steady-tail
