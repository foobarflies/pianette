#!/usr/bin/env python3

# Virtual & GPIO Game Console Controller

# A command-line emulator of a Game Pad Controller 
# that asynchronously listens to GPIO EDGE_RISING
# inputs from sensors and sends Serial commands to 
# an ATMEGA328P acting as a fake SPI Slave for the Console.

# Written in Python 3.

import pianette.config

#from pianette.GPIOController import GPIOController
from pianette.Pianette import Pianette
from pianette.PianetteCmd import PianetteCmd
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

configobj = pianette.config.get_configobj('street-fighter-alpha-3', 'player2')
print(configobj)
# Instanciate the global Pianette
# Its responsibility is to translate Piano actions to Console actions
pianette = Pianette(configobj=configobj)

# Instanciate the global GPIO Controller
# Its responsibility is to feed the Pianette based on GPIO inputs
gpio_controller = GPIOController(configobj=configobj, pianette=pianette)

# Parse config for GPIO
GPIO_PIN_ATTACHMENTS = {}
for key in config['LAYOUT']:
  GPIO_PIN_ATTACHMENTS[int(key)] = { "note": config['LAYOUT'][key] }

# Add reset pin
GPIO_PIN_ATTACHMENTS[int(config['RESET']['gpio'])] = { "pull_up_down": 22, "event": 32, "command": "RESET" }

# Run the main loop of interactive Pianette
Debug.println("NOTICE", "Entering main loop")
PianetteCmd(configobj=configobj, pianette=pianette).cmdloop()
