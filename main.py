#!/usr/bin/env python3

# Pianette

# A command-line emulator of a PS2 Game Pad Controller 
# that asynchronously listens to GPIO EDGE_RISING
# inputs from sensors and sends Serial commands to 
# an ATMEGA328P acting as a fake SPI Slave for the Console.

# Written in Python 3.

import importlib
import pianette.config
import sys

from pianette.Pianette import Pianette
from pianette.PianetteArgumentParser import PianetteArgumentParser
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

configobj = pianette.config.get_all_configobj()

parser = PianetteArgumentParser(configobj=configobj)
args = parser.parse_args()

# Instanciate the global Pianette
# Its responsibility is to translate Piano actions to Console actions
pianette = Pianette(configobj=configobj)

# We MUST select a player before we select a game.
# This allow for per-player mappings
# The game can be changed afterwards, but not the player, as we don't expect
# to be able to unplug the controller from the console.
pianette.select_player(args.selected_player)
pianette.select_game(args.selected_game)

class_names_by_sources = {
    'api': 'PianetteApi', # feed the Pianette from HTTP requests
    'gpio': 'GPIOController', # feed the Pianette from GPIO inputs
}

if args.enabled_sources is not None:
    for source in args.enabled_sources:
        try:
            source_class_name = class_names_by_sources[source]
        except KeyError:
            raise RuntimeError("Unsupported source '%s'" % (source))
        source_module = importlib.import_module('pianette.' + source_class_name)
        source_class = getattr(source_module, source_class_name)
        source_instance = source_class(configobj=configobj, pianette=pianette)
        pianette.enable_source(source, source_instance)

# Run the main loop of interactive Pianette
Debug.println("NOTICE", "Entering main loop")
pianette.cmd.cmdloop()
