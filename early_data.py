"""Reconstructed Castle–Museum–Bank baseline for the offline campaign.

This is new scenario text/balance, not recovered original implementation.
Original game footage used for story/encounter beats:
 https://www.youtube.com/watch?v=hAfuLund6uo (Royal bosses 00:00 / 11:22 / 20:08)
 https://www.youtube.com/watch?v=_6WfM7oUXz0 (Royal Museum infiltration)
 https://www.youtube.com/watch?v=ctGcRPWXRyg (Royal Bank, Queen and Showtime)
Tactical hints intentionally do not disclose undiscovered affinities.
"""
from battle_data import persona, shadow


def enemy(hp, sp, skills, affinity=None, behavior='balanced', *, immune=False):
    return shadow(hp, sp, skills, affinity, behavior, no_knockdown=immune)


ENEMY_ADDITIONS = {
    'Castle Guard': enemy(69, 16, ['Cleave', 'Garu'], {'Electric': 'weak'}, 'aggressive'),
    'Eligor': enemy(114, 26, ['Agi', 'Cleave'], {'Electric': 'weak', 'Fire': 'resist', 'Curse': 'resist'}),
    'Chapel Archangel': enemy(120, 28, ['Kouha', 'Cleave'], {'Electric': 'weak', 'Bless': 'resist', 'Curse': 'weak'}),
    'Kamoshida': enemy(300, 54, ['Cleave', 'Rakunda'], {'Physical': 'resist'}, 'castle-king', immune=True),
    'Trophy of Obsession': enemy(84, 0, [], {}, 'castle-trophy', immune=True),
    'Cognitive Mishima': enemy(51, 10, ['Agi'], {'Electric': 'weak'}, 'castle-war-beast'),
    'Cognitive Shiho': enemy(63, 13, ['Garu'], {'Fire': 'weak'}, 'castle-war-beast'),
    'Koppa Tengu': enemy(79, 20, ['Garu', 'Sukukaja'], {'Ice': 'weak', 'Wind': 'resist'}),
    'Ippon-Datara': enemy(121, 35, ['Agi', 'Cleave', 'Rakunda'], {'Ice': 'weak', 'Bless': 'weak', 'Fire': 'resist', 'Curse': 'resist'}),
    'Kurama Tengu': enemy(142, 36, ['Garula', 'Tarunda'], {'Ice': 'weak', 'Wind': 'resist'}),
    'Madarame’s Eyes': enemy(104, 0, [], {'Fire': 'drain', 'Ice': 'drain', 'Electric': 'drain', 'Wind': 'drain'}, 'museum-face', immune=True),
    'Madarame’s Nose': enemy(109, 0, [], {'Psy': 'drain', 'Nuclear': 'drain', 'Bless': 'drain', 'Curse': 'drain'}, 'museum-face', immune=True),
    'Madarame’s Mouth': enemy(113, 0, [], {'Physical': 'drain', 'Gun': 'drain'}, 'museum-face', immune=True),
    'Madarame': enemy(287, 48, ['Diarama', 'Makajam'], {}, 'museum-artist', immune=True),
    'Scarlet Copy': enemy(62, 14, ['Agi'], {'Fire': 'drain', 'Ice': 'weak'}, 'museum-copy'),
    'Cerulean Copy': enemy(62, 14, ['Bufu'], {'Ice': 'drain', 'Fire': 'weak'}, 'museum-copy'),
    'Golden Copy': enemy(62, 14, ['Zio'], {'Electric': 'drain', 'Wind': 'weak'}, 'museum-copy'),
    'Verdant Copy': enemy(62, 14, ['Garu'], {'Wind': 'drain', 'Electric': 'weak'}, 'museum-copy'),
    'Orobas': enemy(108, 32, ['Agilao', 'Tarunda', 'Marakukaja'], {'Ice': 'weak', 'Electric': 'resist', 'Fire': 'resist'}),
    'Orthrus': enemy(141, 32, ['Agilao', 'Cleave'], {'Ice': 'weak', 'Fire': 'drain'}, 'aggressive'),
    'Fuu-Ki': enemy(152, 37, ['Garula', 'Sukunda'], {'Electric': 'weak', 'Wind': 'drain'}),
    'Sui-Ki': enemy(149, 35, ['Bufula', 'Rakukaja'], {'Nuclear': 'weak', 'Ice': 'drain'}),
    'Kin-Ki': enemy(150, 34, ['Cleave', 'Rakunda'], {'Psy': 'weak', 'Physical': 'resist', 'Gun': 'resist'}),
    'Piggytron': enemy(297, 33, ['Molotov Cocktail', 'Cleave', 'Rakunda'], {'Gun': 'resist'}, 'bank-piggytron', immune=True),
    'Kaneshiro': enemy(242, 39, ['Eiha', 'Dazzler', 'Tarunda'], {}, 'bank-kaneshiro', immune=True),
    'Super VIP Bodyguard': enemy(126, 23, ['Headbutt', 'Rakukaja'], {'Physical': 'resist', 'Gun': 'resist'}, 'bank-bodyguard'),
    'Super VIP Hitman': enemy(105, 29, ['Cleave', 'Mazionga'], {'Physical': 'resist', 'Gun': 'resist'}, 'bank-hitman'),
}

PERSONA_ADDITIONS = {
    "Jack-o'-Lantern": persona(['Agi', 'Tarunda'], {'Fire': 'drain', 'Ice': 'weak', 'Wind': 'weak'},
                             'Fire • attack down'),
    'Pixie': persona(['Zio', 'Dia', 'Rakunda'],
                    {'Gun': 'weak', 'Ice': 'weak', 'Electric': 'resist', 'Bless': 'resist', 'Curse': 'weak'},
                    'Healing • opening coverage • defense down'),
    'Bicorn': persona(['Cleave', 'Garu', 'Tarunda'],
                     {'Electric': 'weak', 'Curse': 'resist'}, 'Physical • Wind • attack down'),
    'Silky': persona(['Bufu', 'Dormina', 'Dia'],
                    {'Fire': 'weak', 'Electric': 'weak', 'Ice': 'resist'}, 'Ice • sleep • spot healing'),
    'Oni': persona(['Cleave', 'Tempest Slash', 'Tarukaja'],
                  {'Physical': 'resist', 'Gun': 'resist'}, 'Physical • durable mask • attack up'),
    'Black Ooze': persona(['Eiga', 'Headbutt', 'Tarunda'],
                         {'Physical': 'resist', 'Gun': 'resist', 'Ice': 'resist', 'Electric': 'weak',
                          'Psy': 'weak', 'Bless': 'weak', 'Curse': 'null'}, 'Curse • mixed defenses • attack down'),
}


def stage(id_, title, map_mark, brief, story_before, story_after, hint, waves,
          reward=None, *, showtime_pairs=()):
    return dict(id=id_, title=title, map_mark=map_mark, brief=brief, story_before=story_before,
                story_after=story_after, hint=hint, waves=waves, reward=reward or {},
                showtime_pairs=showtime_pairs)


CASTLE = (
    stage('castle-gate', 'Castle Gate', '01 GATE', 'Find a way back through the castle’s outer defenses.',
          'The castle is an uglier reflection of Shujin. After the first escape, Joker, Mona, and Skull come back for Ann and have to fight their way through a gate that should not exist.',
          'Ann refuses to be cast as the king’s trophy. Carmen answers, Panther joins, and she can be equipped for the Guardhouse.',
          'Pick targets one at a time. Guard if Joker is under pressure and try a different attack if the first one fizzles.',
          (('Castle Guard',),), dict(teammates=('Panther',), credits=350, joker_hp=8, joker_sp=4, slots=1)),
    stage('guardhouse', 'Guardhouse', '02 GUARD', 'Break the prison patrol and locate a safe way in.',
          'Mona knows a service route, but the jailers are sweeping it. Skull wants to see what happened to the students inside.',
          'The Thieves now have a way in and out. Finding the students turned the patrol route into evidence.',
          'A knocked-down Shadow buys time. Save some SP for the end of the fight.',
          (('Castle Guard', 'Bicorn'),), dict(personas=('Bicorn',), skill_cards=('Dia',), credits=420, joker_hp=6, joker_sp=4)),
    stage('east-gallery', 'East Gallery', '03 EAST', 'Cross the gallery and link the lookout positions.',
          'The gallery patrol is checking every door. Panther recognizes the king’s boasts in the exhibits, but Mona keeps the team moving until there is a clearer path.',
          'The lookout route is clear. The group can deploy three teammates together from the tower onward.',
          'Use Analyze to track what you have tested. Avoid spending every turn on a single target while its ally keeps acting.',
          (('Eligor', 'Silky'),), dict(personas=('Silky',), skill_cards=('Dormina',), credits=480, joker_hp=6, joker_sp=4, squad_slots=1)),
    stage('treasure-route', 'Tower and Treasure Route', '04 TOWER', 'Clear the chapel and confirm the route to the Treasure.',
          'The team crosses the chapel and races the patrols upstairs. Mona keeps a mental map of the shortcuts.',
          'The Treasure route is secure. The calling card is the next move, not another reconnaissance trip.',
          'If your resources are low, guard and recover before the second formation rather than gambling on a clean sweep.',
          (('Chapel Archangel', "Jack-o'-Lantern"), ('Eligor',)), dict(personas=('Angel',), skill_cards=('Rakunda',), credits=600, joker_hp=8, joker_sp=6)),
    stage('throne-room', 'Kamoshida’s Throne Room', '05 KING', 'Deliver the calling card and take the crown.',
          'Shujin’s students have seen the card. In the castle, the king’s prize finally has a shape, but he will fight to keep it.',
          'The king falls and the crown is taken. Outside the Metaverse, Shujin has to hear what it spent so long ignoring.',
          'Break the trophy to deny recovery. When the king winds up a smash, guard before it lands.',
          (('Kamoshida', 'Trophy of Obsession'),), dict(personas=('Jack Frost',), skill_cards=('Tarunda',), credits=1300, joker_hp=12, joker_sp=7)),
)
MUSEUM = (
    stage('museum-entry', 'Museum Entry', '01 ENTRY', 'Reconnoiter the entrance and bypass the first patrol.',
          'Paintings, names and trophies fill Madarame’s museum. The Thieves realize the exhibition represents the work of people he treated as his property.',
          'The entrance is mapped. The next opening is above the public path, not through the front doors.',
          'Vary targets and damage types. A Shadow resisting one attack may be exposed to another.',
          (('Koppa Tengu', 'Pixie'),), dict(skill_cards=('Sukukaja',), credits=550, joker_hp=6, joker_sp=4)),
    stage('museum-security', 'Behind the Locked Door', '02 GRID', 'Cross the laser floor and cut the security control.',
          'The lights and sensors lead to a locked door that also exists outside the Metaverse. The atelier detour brings Yusuke to the questions nobody wanted to answer.',
          'Yusuke refuses to accept the story his mentor sold him. Goemon answers. Fox joins and can be equipped for the gallery.',
          'Take out support Shadows before they erase your progress. Use a safe turn to recover before moving on.',
          (('Ippon-Datara', 'Koppa Tengu'), ('Silky', 'Bicorn')), dict(teammates=('Fox',), personas=('High Pixie',), skill_cards=('Media',), credits=700, joker_hp=6, joker_sp=5)),
    stage('museum-gallery', 'Exhibition Gallery', '03 FOX', 'Confront the truth behind Madarame’s exhibits.',
          'With Fox on the team, the Thieves cross the reopened exhibition and look again at what the mentor took from his pupils.',
          'Fox puts the clues together. Now the team can follow the false displays back toward the real Sayuri.',
          'Create an opening and pass it to whoever can best exploit the next target. Don’t confuse the command menu with Analyze.',
          (('Ippon-Datara', 'Koppa Tengu', 'Koppa Tengu'),), dict(skill_cards=('Bufula',), credits=850, joker_hp=8, joker_sp=4, slots=1)),
    stage('museum-vault', 'Treasure Vault', '04 VAULT', 'Trace the framed corridors to the protected Treasure.',
          'The winding halls rearrange around copies and forged originals. The Thieves use the artwork as passageways while looking for the real vault.',
          'The route to the Sayuri is open. The only thing left before taking it is to make the ruler believe it can be stolen.',
          'Strong defenses don’t protect every target the same way. Switch tactics when a hit stops working.',
          (('Kurama Tengu', 'Koppa Tengu'), ('Shiki-Ouji',)), dict(personas=('Shiki-Ouji',), skill_cards=('Rakukaja',), credits=925, joker_hp=8, joker_sp=5)),
    stage('museum-heist', 'Calling Card and Heist', '05 CARD', 'Follow the secured route and move the Sayuri out.',
          'The card reaches the atelier. Back in the Palace, the Thieves use the overhead route to seize the painting instead of taking the bait at ground level.',
          'The route worked, but Madarame has not let the painting go. The team heads for the courtyard with the original.',
          'Leave yourself some recovery for the confrontation. Control or knock down the most active threat first.',
          (('Ippon-Datara', 'Nue'),), dict(personas=('Oni',), skill_cards=('Sukunda',), credits=1100, joker_hp=8, joker_sp=5)),
    stage('museum-throne', 'Madarame’s Courtyard', '06 FRAME', 'Break the false face and finish the pursuit.',
          'Madarame’s portrait pulls itself apart into living features. When that trick fails, he tries to bury the original under copies of himself.',
          'The counterfeit court collapses. Fox leaves with the Sayuri’s truth rather than the version sold at the exhibition.',
          'Different features feed on different hits. Test one target at a time, then use the colored copies to build an action chain.',
          (('Madarame’s Eyes', 'Madarame’s Nose', 'Madarame’s Mouth'),
           ('Madarame', 'Scarlet Copy', 'Cerulean Copy', 'Golden Copy', 'Verdant Copy')),
          dict(personas=('Orthrus',), skill_cards=('Diarama',), credits=1900, joker_hp=12, joker_sp=7)),
)

GUN_WITH_THE_WIND = ('Mona', 'Panther')
QUEEN_AND_SKULL = ('Skull', 'Queen')
BANK = (
    stage('bank-entry', 'Floating Bank Entry', '01 ENTRY', 'Reach the bank that hangs above Shibuya.',
          'Kaneshiro’s Palace looms above the streets it bleeds for money. Makoto gives the team a way inside and comes face-to-face with what obedience has bought her.',
          'Makoto breaks with the role others assigned her. Johanna answers; Queen joins and can be equipped for the service passage.',
          'Check your mask after every switch. An enemy can turn your own vulnerability into another attack.',
          (('Orobas', 'Orthrus'),), dict(teammates=('Queen',), personas=('Makami',), skill_cards=('Frei',), credits=1150, joker_hp=8, joker_sp=5, slots=1)),
    stage('bank-service', 'Service Passage', '02 SERVICE', 'Slip through staff access and map the way below the lobby.',
          'The main banking floor crawls with guards. The team heads through the service wing while Mona and Panther try out a joint finishing move.',
          'Staff access is mapped. The monitoring rooms are now the shortest route to the vault locks.',
          'The new two-person finisher depends on who you brought and when the chance appears. Keep both partners standing.',
          (('Oni', 'Orobas'), ('Fuu-Ki',)), dict(skill_cards=('Energy Drop',), credits=1250, joker_hp=8, joker_sp=5),
          showtime_pairs=(GUN_WITH_THE_WIND,)),
    stage('bank-security', 'Banker Passageway', '03 KEYS', 'Win the keys held in the monitoring rooms.',
          'The bank treats its strongest collectors like walking keys. You need to clear both locks before the next floor will accept you.',
          'Both security keys are recovered. The teller corridors open onto the underground vault.',
          'Keep track of what each keyholder resists instead of assuming the second will react like the first.',
          (('Fuu-Ki', 'Black Ooze'), ('Sui-Ki', 'Kin-Ki')), dict(personas=('Black Ooze',), skill_cards=('Freila',), credits=1500, joker_hp=8, joker_sp=5),
          showtime_pairs=(GUN_WITH_THE_WIND,)),
    stage('bank-vault', 'Underground PIN Vault', '04 PIN', 'Follow torn notes through the rotating vault.',
          'Each ring takes a short word that must be converted into a PIN. The team gathers the torn notes for RICH, REAP, HUGE and GOLD before committing to the elevator.',
          'The last lock turns. The vault is reachable on a heist; the Treasure still needs a calling card to take shape.',
          'Take opponents in an order you can sustain. Preserve both a healing option and an alternative to weapon damage.',
          (('Black Ooze', 'Orobas'), ('Kin-Ki', 'Sui-Ki', 'Oni')), dict(skill_cards=('Rakunda',), credits=1700, joker_hp=8, joker_sp=6),
          showtime_pairs=(GUN_WITH_THE_WIND,)),
    stage('bank-heist', 'Vault Breach', '05 CARD', 'Deliver the card and race down to the vault’s center.',
          'The card puts the moneylender on notice. The Thieves retrace the vault route now that the Treasure can be taken, with Skull and Queen ready to try a joint finisher.',
          'The vault team is through. Kaneshiro waits with a machine of his own and backup close at hand.',
          'Keep someone able to heal. A lucky opening does not make the machine or the counterattack harmless.',
          (('Kin-Ki', 'Fuu-Ki'), ('Orthrus', 'Black Ooze')), dict(skill_cards=('Mediarama',), credits=1850, joker_hp=8, joker_sp=6),
          showtime_pairs=(GUN_WITH_THE_WIND, QUEEN_AND_SKULL)),
    stage('bank-boss', 'Kaneshiro’s Vault Center', '06 VAULT', 'Stop Piggytron and clear Kaneshiro’s hired muscle.',
          'Kaneshiro puts his faith in Piggytron and the protection bought with his money. Neither is going to stand aside while the team takes the Treasure.',
          'The machine stops and the hired muscle folds. Shibuya is out of this collector’s grip, but his warning about another Metaverse user stays with the team.',
          'A spinning machine telegraphs an impact. After it falls, deal with the guard blocking your attacks and the hitman punishing open turns.',
          (('Piggytron',), ('Kaneshiro', 'Super VIP Bodyguard', 'Super VIP Hitman')),
          dict(skill_cards=('Mafreila',), credits=2800, joker_hp=14, joker_sp=8, slots=1),
          showtime_pairs=(GUN_WITH_THE_WIND, QUEEN_AND_SKULL)),
)

CHAPTERS = (
    dict(id='castle', title='Kamoshida’s Castle', brief='A prison beyond Shujin. Find the missing students and steal the king’s Treasure.',
         completion='Shujin hears Kamoshida’s confession. The Thieves take their first step as a team.', nodes=CASTLE),
    dict(id='museum', title='Madarame’s Museum', brief='Follow a trail of stolen work to the original Sayuri.',
         completion='The exhibition falls apart. Fox keeps the truth behind the Sayuri.', nodes=MUSEUM),
    dict(id='bank', title='Kaneshiro’s Bank', brief='Trace Shibuya’s extortion to the rotating vault.',
         completion='Kaneshiro’s extortion ends. A warning points the Thieves toward a larger Metaverse mystery.', nodes=BANK),
)
