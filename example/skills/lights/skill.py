from pytlas import intent, training, translations, meta


@training('en')
def en_data(): return """
%[lights_on]
    turn the @[room]'s lights on would you
    turn lights on in the @[room]
    lights on in @[room] please
    turn on the lights in @[room]
    turn the lights on in @[room]
    enlight me in @[room]

%[lights_off]
    turn the @[room]'s lights off would you
    turn lights off in the @[room]
    lights off in @[room] please
    turn off the lights in @[room]
    turn the lights off in @[room]

~[basement]
    cellar

@[room](extensible=false)
    living room
    kitchen
    bedroom
    ~[basement]
"""


@training('fr')
def fr_data(): return """
%[lights_on]
    allume ~[light_or_lights] du @[room] veux-tu
    allume les lumières de la @[room#feminin]
    peux-tu allumer ~[light_or_lights] du @[room] s'il te plait
    peux-tu allumer ~[light_or_lights] dans la @[room#feminin] s'il te plait
    allume ~[light_or_lights] dans le @[room]
    allume ~[light_or_lights] dans la @[room#feminin] et le @[room]
    j'ai besoin de lumière dans le @[room]
    j'ai besoin d'un peu de lumière dans la @[room#feminin]

~[light_or_lights]
    la lumière
    les lumières

%[lights_off]
    éteint ~[light_or_lights] du @[room] veux-tu
    éteint les lumières de la @[room#feminin]
    peux-tu éteindre ~[light_or_lights] du @[room] s'il te plait
    peux-tu éteindre ~[light_or_lights] dans la @[room#feminin] s'il te plait
    éteint ~[light_or_lights] dans le @[room]
    éteint ~[light_or_lights] dans la @[room#feminin] et le @[room]
    coupe ~[light_or_lights] dans la @[room#feminin]

@[room](extensible=false)
    salon
    garage
    celier

@[room#feminin]
    cuisine
    chambre
    chambre d'ami
    salle de bain
    salle d'eau
"""


@translations('fr')
def fr_translations():
    return {
        "For which rooms?": "Pour quelles pièces ?",
        "Which rooms Sir?": "Quelles pièces monsieur ?",
        "Please specify some rooms": "Précisez pour quelles pièces",
        "Turning lights %s in %s": "Très bien, lumières %s pour les pièces %s"
    }


AVAILABLE_ROOMS = {
    'en': ['kitchen', 'bedroom'],
    'fr': ['cuisine', 'chambre']
}
""" Restrict room to managed ones
Sort of white list. Is should be defined in settings.
"""


def turn_lights(req, on):
    global AVAILABLE_ROOMS

    rooms = req.intent.slot('room')

    if not rooms:  # < no room defined ask for some
        return req.agent.ask('room', [
            req._('For which rooms?'),
            req._('Which rooms Sir?'),
            req._('Please specify some rooms'),
        ])

    for room in rooms:  # < check all room
        # < this one is not available
        if not room.value in AVAILABLE_ROOMS[req.lang]:
            return req.agent.ask('room',
                                 req._('Please choose a room  among?'),
                                 AVAILABLE_ROOMS[req.lang])

    # put your logic here

    room_list = ', '.join(room.value for room in rooms)
    action_name = 'on' if on else 'off'
    req.agent.answer(req._('Turning lights %s in %s') % (
        action_name, room_list), skill='lights', action=action_name, rooms=room_list)

    return req.agent.done()


@intent('lights_on')
def turn_on(req):
    return turn_lights(req, True)


@intent('lights_off')
def turn_off(req):
    return turn_lights(req, False)
