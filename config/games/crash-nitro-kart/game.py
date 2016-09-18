# coding: utf-8
from pianette.utils import Debug
import random

def select_character(*args, **kwargs):
    cmd = kwargs['cmd']
    config = kwargs['config']
    player_config = kwargs['player_config']

    try:
        character = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a character or pass {random}")
        return

    if (character == "{random}"):
        # Select a random character in supported-characters
        character = random.choice(config.get('supported-characters'))
    elif not character in config.get('supported-characters'):
        Debug.println("WARNING", "This character is not supported")
        return

    Debug.println("NOTICE", "Choosing character %s" % character)
    # Process list of commands to obtain this character
    cmd.onecmd("console.play %s ✕" % player_config.get("Positions").get(character))
