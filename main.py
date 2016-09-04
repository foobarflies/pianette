#!/usr/bin/env python3

# Pianette

# A command-line emulator of a PS2 Game Pad Controller 
# that asynchronously listens to GPIO EDGE_RISING
# inputs from sensors and sends Serial commands to 
# an ATMEGA328P acting as a fake SPI Slave for the Console.

# Written in Python 3.

import pianette.config
import sys

from pianette.GPIOController import GPIOController
from pianette.Pianette import Pianette
from pianette.PianetteArgumentParser import PianetteArgumentParser
from pianette.PianetteApi import PianetteApi
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

# FIX ME - introduce sys.argv[1] to choose player AND game?
configobj = pianette.config.get_configobj('piano', 'pianette', 'street-fighter-alpha-3', 'player1')

parser = PianetteArgumentParser(configobj=configobj)
args = parser.parse_args()

# Instanciate the global Pianette
# Its responsibility is to translate Piano actions to Console actions
pianette = Pianette(configobj=configobj)

pianette.select_game(args.selected_game)

sources = {
    "api": PianetteApi, # feed the Pianette from HTTP requests
    "gpio": GPIOController, # feed the Pianette from GPIO inputs
}
if args.enabled_sources is not None:
    for source in args.enabled_sources:
        sources[source](configobj=configobj, pianette=pianette)
        pianette.enable_source(source)

# Run the main loop of interactive Pianette
Debug.println("NOTICE", "Entering main loop")
pianette.cmd.cmdloop()
