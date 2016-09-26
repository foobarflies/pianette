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

def select_mode(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        mode = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a mode (Versus or Arcade)")
        return

    if mode == "Versus":
        cmd.onecmd("console.play → ✕")
    else: 
        cmd.onecmd("console.play ✕")

def select_fighting_handicap(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        handicap = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a handicap (between ▶ and ▶▶▶▶▶▶▶▶)")
        return
    
    cmd.onecmd("console.play ← ; ← ; ← ; ← ; ← ; ← ; ← ; ← ; " + ((max(1, min(8, len(handicap))) - 1) * "→ ; ") + "✕")

def select_fighting_style(*args, **kwargs):
    cmd = kwargs['cmd']
    try:
        style = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a style (A-ISM, X-ISM or V-ISM)")
        return

    if style == "V-ISM":
        cmd.onecmd("console.play ↓")
    elif style == "X-ISM":
        cmd.onecmd("console.play ↑")
    elif style == "A-ISM":
        pass
    else:
        Debug.println("WARNING", "%s is not an available fighting style" % style)
        return

    cmd.onecmd("console.play ✕")

def select_stage(*args, **kwargs):
    cmd = kwargs['cmd']
    config = kwargs['config']
    try:
        stage = args[0][0]
    except IndexError:
        Debug.println("WARNING", "You must define a stage")
        return

    if (stage == "{random}"):
        # Select a random stage in supported-stages
        stage = random.choice(config.get('supported-stages'))
    elif not stage in config.get('supported-stages'):
        Debug.println("WARNING", "This stage is not supported")
        return

    Debug.println("NOTICE", "Choosing stage '%s'" % stage)

    cmd.onecmd("console.play %s ; ✕" % config.get("Stages").get(stage))
