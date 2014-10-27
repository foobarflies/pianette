#!/usr/bin/env python3

# Virtual & GPIO Game Console Controller

# A command-line emulator of a Game Pad Controller 
# that asynchronously listens to GPIO EDGE_RISING
# inputs from sensors and sends Serial commands to 
# an ATMEGA328P acting as a fake SPI Slave for the Console.

# Written in Python 3.

import pianette.config

from pianette.ControllerState import ControllerState
from pianette.GPIOController import GPIOController
from pianette.Pianette import Pianette
from pianette.PianoState import PianoState
from pianette.PianetteCmd import PianetteCmd
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

configobj = pianette.config.get_configobj('street-fighter-alpha-3', 'player2')

# Parse config for GPIO
notes_state = {}
piano_buffered_states = {}
GPIO_PIN_ATTACHMENTS = {}
for key in config['LAYOUT']:
  notes_state[config['LAYOUT'][key]] = False
  piano_buffered_states[config['LAYOUT'][key]] = []
  GPIO_PIN_ATTACHMENTS[int(key)] = { "note": config['LAYOUT'][key] }

# Add reset pin
GPIO_PIN_ATTACHMENTS[int(config['RESET']['gpio'])] = { "pull_up_down": 22, "event": 32, "command": "RESET" }

# This holds the Piano state at any moment
piano_state = PianoState(notes_state)

# This holds the PSX controller state at any moment
psx_controller_state = ControllerState(int(config['GAMEPLAY']['player']))

# Start the pianette
pianette = Pianette(piano_state, psx_controller_state, piano_buffered_states)

# Instanciate the global GPIO Controller
# Its responsibility is to set piano and controller states based on GPIO inputs
gpio_controller = GPIOController(piano_state, psx_controller_state, GPIO_PIN_ATTACHMENTS)

# Run main loop
Debug.println("NOTICE", "Entering main loop")
PianetteCmd(piano_state, psx_controller_state).cmdloop()
