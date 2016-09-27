# coding: utf-8
from pianette.utils import Debug
import random

def select_character(*args, **kwargs):
    cmd = kwargs['cmd']
    config = kwargs['config']
    player_config = kwargs['player_config']

    try:
        character = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a character or pass {random}")
        return

    if (character == "{random}"):
        # Select a random character in supported-characters
        character = random.choice(config.get('supported-characters'))
    elif not character in config.get('supported-characters'):
        Debug.println("WARNING", "This character '%s' is not supported" % character)
        return

    # Choosing a deterministic character will only work for the first player to choose
    Debug.println("NOTICE", "_Probably_ choosing character %s" % character)
    # Process list of commands to obtain this character
    cmd.onecmd("console.play START %s ✕" % config.get("Positions").get(character))

def select_mode(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        mode = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a mode (Mutiplayer Race, Single Race or Team Race)")
        return

    if mode == "Mutiplayer Race":
        cmd.onecmd("console.play ↓ ; ↓ ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ;")
    elif mode == "Single Race":
        cmd.onecmd("console.play ↓ ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ;")
    elif mode == "Team Race":
        cmd.onecmd("console.play ↓ ; ✕ ; ; ; ; ; ; ; ↓ ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ;")
    else: 
        cmd.onecmd("console.play ↓ ; ↓ ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ; ✕ ; ; ; ; ; ; ;") # default to multiplayer

def select_track(*args, **kwargs):
    cmd = kwargs['cmd']
    config = kwargs['config']

    try:
        track = " ".join(args[0])
    except IndexError:
        Debug.println("WARNING", "You must define a track")
        return

    if (track == "{random}"):
        # Select a random track in supported-tracks
        track = random.choice(config.get('supported-tracks'))
    elif not track in config.get('supported-tracks'):
        Debug.println("WARNING", "This track '%s' is not supported" % track)
        return

    Debug.println("NOTICE", "Choosing track '%s'" % track)

    cmd.onecmd("console.play %s ; ; ; ; ; ✕ " % config.get("Tracks").get(track))
