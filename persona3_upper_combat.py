"""Upper Arqa and the July Full Moon, scaled to the terminal combat loop."""

FOES={
    'bronze':('Bronze Dice',104,'Strike',25,{'Strike':'null','Electric':'weak'},''),
    'vicious':('Vicious Raven',101,'Fire',26,{'Fire':'drain','Ice':'weak','Wind':'resist'},''),
    'maniacal-book':('Maniacal Book',110,'Dark',25,{'Fire':'weak','Ice':'resist','Light':'null'},''),
    'steel-gigas':('Steel Gigas',119,'Strike',28,{'Strike':'resist','Electric':'weak'},''),
    'jealous-cupid':('Jealous Cupid',111,'Pierce',26,{'Ice':'weak','Wind':'null'},''),
    'dark-eagle':('Dark Eagle',120,'Wind',27,{'Wind':'weak','Light':'drain','Dark':'null'},''),
    'servant-tower':('Servant Tower',255,'Electric',26,
        {'Dark':'weak','Fire':'null','Light':'null','Electric':'repel','Ice':'resist','Wind':'resist'},'upper-tower'),
    'enslaved-cupid':('Enslaved Cupid',107,'Pierce',24,{'Electric':'weak'},''),
    'lascivious-lady':('Lascivious Lady',255,'Slash',26,
        {'Fire':'null','Ice':'null','Electric':'null','Wind':'null','Light':'null','Dark':'null','Strike':'vulnerable'},'upper-lady'),
    'profligate-gigas':('Profligate Gigas',125,'Strike',30,{'Wind':'weak','Strike':'vulnerable'},''),
    'fleetfooted':('Fleetfooted Cavalry',334,'Wind',32,{'Wind':'drain','Light':'null','Dark':'null'},'upper-cavalry'),
    'hierophant':('Hierophant',418,'Light',29,{'Light':'null','Dark':'null'},'hierophant'),
    'lovers':('Lovers',467,'Pierce',27,{'Fire':'null','Pierce':'resist','Electric':'resist'},'lovers'),
}

ENCOUNTERS={
    'upper-patrol':('Upper Arqa Patrol',('bronze','vicious')),
    'upper-patrol-50':('Relay Gallery Patrol',('maniacal-book','steel-gigas')),
    'upper-patrol-56':('Upper Landing Patrol',('jealous-cupid','dark-eagle')),
    'upper-servant':('Servant Tower • 47F',('servant-tower','enslaved-cupid','enslaved-cupid')),
    'upper-lady':('Lascivious Lady • 54F',('lascivious-lady','profligate-gigas','profligate-gigas')),
    'upper-cavalry':('Fleetfooted Cavalry • 60F',('fleetfooted',)),
    'hotel-hierophant':('Champs de Fleurs • Hierophant',('hierophant',)),
    'hotel-lovers':('Champs de Fleurs • Lovers',('lovers',)),
}
HOTEL=('hotel-hierophant','hotel-lovers')
PERSONAS={
    'Take-Minakata':(('Zionga','Assault Dive','Rakukaja'),{'Fire':'weak','Ice':'weak','Electric':'resist'}),
    'Naga':(('Zionga','Torrent Shot','Sukukaja'),{'Wind':'weak','Electric':'null'}),
    'Sati':(('Agilao','Marin Karin','Patra'),{'Ice':'weak','Fire':'resist'}),
    'Principality':(('Kouga','Media','Rakunda'),{'Dark':'weak','Light':'null'}),
}
SKILLS={
    'Zionga':('hit','Electric',46,7,'one',0),
    'Agilao':('hit','Fire',47,7,'one',0),
    'Kouga':('hit','Light',47,8,'one',0),
    'Assault Dive':('hit','Strike',48,0,'one',10),
    'Torrent Shot':('hit','Pierce',47,0,'one',9),
    'Marin Karin':('ailment','charm',0,5,'one',0),
    'Media':('heal','',35,9,'team',0),
}
PERSONA_LEARNS={'Take-Minakata':((9,'Tarunda'),),'Naga':((9,'Rakunda'),),'Sati':((9,'Maragi'),),
                'Principality':((9,'Sukukaja'),)}
ITEMS={'Dis-Charm':('clear-charm',0)}
ROLES={'upper-tower','upper-lady','upper-cavalry','hierophant','lovers'}
CONTROLLED={'charm','fear'}
HIEROPHANT_CYCLE=('light','fear-pair','dive','light','dive','fear-single')


def _doctrine_targets(b,beat):
    # Formation slots, not current HP/Guard, determine the marks. A KO may
    # remove a mark but cannot redirect it onto someone never telegraphed.
    n=len(b.allies)
    shift=2*(beat//len(HIEROPHANT_CYCLE))
    stage=HIEROPHANT_CYCLE[beat%len(HIEROPHANT_CYCLE)]
    if stage=='fear-pair':indexes=(shift%n,(shift-1)%n)
    elif stage=='fear-single':indexes=((shift+1)%n,)
    else:return ()
    return tuple(b.allies[i] for i in dict.fromkeys(indexes) if b.allies[i].alive)


def hold_status(b,target,status):
    if not target.alive or target.guard or target.status or (target.enemy and target.role in ROLES):
        return False
    target.status=status;target.status_until=b.round+1
    b._say(f'{target.label} is affected by {status.upper()}.')
    return True


def step_afflicted(b,u):
    """Expire scripted ailments, and give a charmed foe one friendly-fire turn."""
    if u.status_until and b.round>u.status_until:
        b._say(f'{u.label} shakes off {u.status}.')
        u.status='';u.status_until=0
    if not u.enemy or u.status!='charm':return False
    friends=[v for v in b.enemies if v.alive and v is not u]
    if not friends:return False
    target=min(friends,key=lambda v:v.hp)
    b._say(f'{u.label} turns on {target.label}.')
    b._hit(u,target,u.element,u.power,False)
    return True


def threat(b):
    body=next((u for u in b.enemies if u.alive and u.role in ROLES),None)
    if body is None:return ''
    beats=b._upper_beat.get(body.name,0)
    if body.role=='upper-tower':
        if any(u.alive for u in b.enemies if u is not body):
            return 'Servant Tower coordinates with the Cupids.'
        return ''
    if body.role=='upper-lady':
        return ('Lascivious Lady can Charm. Keep Patra ready.' if beats else
                'Lascivious Lady blocks magic. Strike or use Theurgy.')
    if body.role=='upper-cavalry':
        return ('GALE CHARGE / Guard the incoming Wind.' if beats%3==0 else
                'Fleetfooted Cavalry may raise its evasion.')
    if body.role=='hierophant':
        marked=_doctrine_targets(b,beats)
        if marked:return 'DOOMSDAY DOCTRINE / Guard: '+', '.join(u.label for u in marked)+'.'
        return ''
    if any(u.status=='charm' and u.alive for u in b.allies):
        return 'HEARTBREAKER / Cure Charm before the next strike.'
    if beats==0:
        target=next((u.label for u in reversed(b.allies) if u.alive),'The last ally')
        return f'HOLY ARROW / {target} should Guard.'
    if beats%3==2:
        return 'SEXY DANCE / Guard against group Charm.'
    return 'Lovers can Charm. Patra and Dis-Charm can clear it.'


def _hit_team(b,actor,element,power,*,without_more=False):
    extra=False
    for target in b.allies:
        if target.alive:extra=b._hit(actor,target,element,power,False) or extra
        if not b.allies[0].alive:break
    return extra and not without_more


def enemy_turn(b,u,bonus):
    """None delegates to ordinary AI; scripted turns use a normal ally window."""
    if u.role not in ROLES or bonus:return None
    beat=b._upper_beat.get(u.name,0)
    b._upper_beat[u.name]=beat+1
    live=[a for a in b.allies if a.alive]
    if not live:return False
    if u.role=='upper-tower':
        if beat%3!=1:return None
        if any(v.alive for v in b.enemies if v is not u):
            b._say('Servant Tower coordinates an Electric volley.')
            return _hit_team(b,u,'Electric',17)
        return None
    if u.role=='upper-lady':
        if beat%3!=1:return None
        target=min(live,key=lambda a:(a.guard,bool(a.status),a.hp))
        b._say('Lascivious Lady casts Marin Karin.')
        hold_status(b,target,'charm')
        return False
    if u.role=='upper-cavalry':
        if beat%3==0:
            b._say('Fleetfooted Cavalry releases the charged Gale Slash.')
            return _hit_team(b,u,'Wind',30)
        if beat%3==1:
            b.modify_stat(u,'agility',1);b._say('Fleetfooted Cavalry raises its evasion.')
            return False
        return None
    if u.role=='hierophant':
        stage=HIEROPHANT_CYCLE[beat%len(HIEROPHANT_CYCLE)]
        if stage=='light':
            b._say('Hierophant casts Makouga.')
            return _hit_team(b,u,'Light',19)
        if stage.startswith('fear'):
            b._say('Hierophant pronounces Doomsday Doctrine.')
            for target in _doctrine_targets(b,beat):hold_status(b,target,'fear')
            return False
        target=min(live,key=lambda a:(a.guard,a.hp))
        b._say('Hierophant uses Assault Dive.')
        return b._hit(u,target,'Strike',32,False)
    if beat==0:
        target=live[-1]
        b._say(f'Lovers uses Holy Arrow on {target.label}.')
        b._hit(u,target,'Pierce',26,False)
        hold_status(b,target,'charm')
        return False
    charmed=[a for a in live if a.status=='charm']
    if charmed:
        b._say('Lovers targets charmed allies with Heartbreaker.')
        for target in charmed:
            b._hit(u,target,'Almighty',49,False,ignore_affinity=True)
            target.status='';target.status_until=0
            if not b.allies[0].alive:break
        return False
    if 3*u.hp<=2*u.max_hp and 'lovers-diarama' not in b._upper_beat:
        b._upper_beat['lovers-diarama']=1
        b._recover(u,'heal',48)
        b._say('Lovers uses Diarama once.')
        return False
    if beat%3==2:
        b._say('Lovers uses Sexy Dance.')
        for target in sorted(live,key=lambda a:a.hp,reverse=True)[:2]:hold_status(b,target,'charm')
        return False
    if 2*u.hp<=u.max_hp:
        target=min(live,key=lambda a:(a.guard,a.hp))
        b._say('Lovers uses Agidyne.')
        return b._hit(u,target,'Fire',38,False)
    target=min(live,key=lambda a:(a.guard,bool(a.status),a.hp))
    b._say('Lovers casts Marin Karin.')
    hold_status(b,target,'charm')
    return False
