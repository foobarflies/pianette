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
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

configobj = pianette.config.get_configobj('street-fighter-alpha-3', 'player1')

# Instanciate the global Pianette
# Its responsibility is to translate Piano actions to Console actions
pianette = Pianette(configobj=configobj)

# Instanciate the global GPIO Controller
# Its responsibility is to feed the Pianette based on GPIO inputs
gpio_controller = GPIOController(configobj=configobj, pianette=pianette)

# Make the Pianette object listen to GPIO inputs
pianette.enable_source("gpio")

# Run the main loop of interactive Pianette
Debug.println("NOTICE", "Entering main loop")
pianette.cmd.cmdloop()
