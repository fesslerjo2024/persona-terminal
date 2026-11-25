"""Transient Casino route interactions, kept out of the campaign save."""
from dataclasses import dataclass, field

SLOT_COST = 5_000
JACKPOT = 50_000
CARD_COST = 50_000
REGISTRATION_COINS = 1_000
ARENA_PRIZE = 100_000
RAISED_TOLL = 1_000_000
CROW_PAYOUT = 450_000
CROW_SPARE_BALANCE = 451_000
# Royal's repeated dice wins and the crew's extra winnings are one action.
DICE_WINNINGS = 5_000


@dataclass(frozen=True)
class RouteAction:
    id: str
    label: str
    block: str = ''


@dataclass
class CasinoRoute:
    coins: int = REGISTRATION_COINS
    dice_override: bool = False
    dice_won: bool = False
    slot_hub: bool = False
    bypassed: set[str] = field(default_factory=set)
    jackpot: bool = False
    registered: bool = False
    door_checked: bool = False
    through_vent: bool = False
    bridge_deposit: int = 0
    stage: str = ''
    notice: str = ''
    pick: int = 0
    leaving: bool = False

    def open(self, stage):
        self.stage = stage
        self.pick = 0
        self.notice = ''
        self.leaving = False

    @property
    def bridge_toll(self):
        return RAISED_TOLL if self.bridge_deposit else ARENA_PRIZE

    def rows(self):
        o = RouteAction
        if self.stage == 'dice':
            return (
                o('override_dice', "Rewire the dice room", 'Crow already has control.' if self.dice_override else ''),
                o('play_dice', "Follow Crow’s signal", 'The house still controls the dice.' if not self.dice_override else
                  'The dice winnings have already been collected.' if self.dice_won else ''),
                o('leave_dice', 'Head to the Slot Room', f'Get {SLOT_COST:,} coins for the giant slot first.'
                  if self.coins < SLOT_COST else ''),
            )
        if self.stage == 'slots':
            return (
                o('scan', 'Inspect the terminal behind the slot', 'Oracle traced the two live panels.' if self.slot_hub else ''),
                *(o(panel, f'Bypass the {panel} panel',
                    'The panel is on standby. Find the main terminal first.' if not self.slot_hub else
                    f'The {panel} panel is offline.' if panel in self.bypassed else '')
                  for panel in ('red', 'green')),
                o('spin', f'Spin the giant slot  /  {SLOT_COST:,} coins',
                  'Jackpot already paid.' if self.jackpot else
                  'Both the red and green panels must be offline.' if len(self.bypassed)<2 else
                  f'The slot needs {SLOT_COST:,} coins.' if self.coins < SLOT_COST else ''),
                o('exchange', f'Buy the High Limit card  /  {CARD_COST:,} coins',
                  'Collect the jackpot before visiting the exchange.' if not self.jackpot else
                  'You already have the card.' if self.registered else
                  'Not enough coins for the card.' if self.coins < CARD_COST else ''),
            )
        if self.stage == 'darkness':
            options = [o('door', 'Check the service door',
                         'The door is locked from this side.' if self.door_checked else '')]
            if self.door_checked:
                options.append(o('vent', 'Crawl through the low vent',
                                 'The squad is already through.' if self.through_vent else ''))
            if self.through_vent:
                options.append(o('exit', 'Follow the lit passage'))
            return tuple(options)
        if self.stage == 'bridge':
            deposit = self.bridge_deposit
            return (
                o('prize', 'Present the arena prize',
                  'The arena prize is already counted.' if deposit else ''),
                o('payout', 'Re-scan the team card',
                  'Present the arena prize first.' if not deposit else
                  'Crow’s payout is already counted.' if deposit > ARENA_PRIZE else ''),
                o('spare', 'Scan Crow’s spare card',
                  'Re-scan the team card first.' if deposit <= ARENA_PRIZE else
                  'The spare card is already counted.' if deposit >= RAISED_TOLL else ''),
                o('cross', 'Lower the bridge and cross',
                  'The deposit is still short.' if deposit < RAISED_TOLL else ''),
            )
        raise ValueError(f'Unknown Casino route: {self.stage}')

    def choose(self, id):
        row = next((o for o in self.rows() if o.id == id), None)
        if row is None:
            if self.stage=='darkness' and id in ('vent','exit'):
                self.notice = 'Search this side of the wall first.'
                return False
            raise ValueError(f'Unknown Casino action: {id}')
        self.notice = row.block
        if row.block:
            return False
        if id == 'override_dice':
            self.dice_override = True
            self.notice = 'Oracle reroutes the control feed. Crow signals when to play.'
        elif id == 'play_dice':
            self.dice_won = True
            self.coins += DICE_WINNINGS
            self.notice = f'Crow and Skull bring the winnings back: +{DICE_WINNINGS:,} coins.'
        elif id == 'scan':
            self.slot_hub = True
            self.notice = 'Oracle finds two live controls: red and green.'
        elif id in ('red', 'green'):
            self.bypassed.add(id)
            self.notice = f'{id.title()} panel offline.'
        elif id == 'spin':
            self.jackpot = True
            self.coins += JACKPOT-SLOT_COST
            self.notice = f'Jackpot: {JACKPOT:,} coins.'
        elif id == 'exchange':
            self.registered = True
            self.coins -= CARD_COST
            return True
        elif id == 'door':
            self.door_checked = True
            self.notice = 'Locked. A draft catches your sleeve. Third Eye picks out a vent.'
        elif id == 'vent':
            self.through_vent = True
            self.notice = 'The squad drops onto the far ledge. A light marks the way out.'
        elif id == 'prize':
            self.bridge_deposit = ARENA_PRIZE
            self.notice = 'Sae raises the toll. Crow asks you to check the team card again.'
        elif id == 'payout':
            self.bridge_deposit += CROW_PAYOUT
            self.notice = 'Crow’s arena payout posted. He hands you a spare card for the rest.'
        elif id == 'spare':
            self.bridge_deposit += CROW_SPARE_BALANCE
            self.notice = 'The machine accepts both deposits.'
        else:  # Leave Dice, Darkness, or the Bridge of Judgment.
            return True
        return False



def draw_route_art(app,route):
    """Illustrate the existing giant-slot readout without replacing its digits."""
    if route.stage!='slots':return
    import persona5_story_art as art
    # The host owns row 7's exact result and left-hand actions. Keep the
    # cabinet right of every full label, including its selection prefix.
    x=max(round(app.w*.62),9+max(len(row.label) for row in route.rows()))
    art.draw(app,art.slot,x,8,app.w-x-3,8,hub=route.slot_hub,
             bypassed=route.bypassed,jackpot=route.jackpot)
