#!/usr/bin/env python3

from pianette.ControllerState import ControllerState
from pianette.GPIOController import GPIOController
from pianette.Pianette import Pianette
from pianette.PianoState import PianoState
from pianette.cmd import PianetteCmd
from pianette.utils import Debug

Debug.println("INFO", " ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " |            PIANETTE            | ")
Debug.println("INFO", " ################################## ")
Debug.println("INFO", " ")

# Read config
import configparser, os
config = configparser.ConfigParser()
main_base = os.path.dirname(__file__)
config_file = os.path.join([main_base, "conf.ini"])
Debug.println("INFO", "Reading configuration file %s ..." % ("/".join(config_file)))
config.read("/".join(config_file))

# Parse config for GPIO
notes_state = {}
GPIO_PIN_ATTACHMENTS = {}
for key in config['LAYOUT']:
  if (config['LAYOUT'][key] is not None):
    notes_state[config['LAYOUT'][key]] = False
    GPIO_PIN_ATTACHMENTS[int(key)] = { "note": config['LAYOUT'][key] }

# Add reset pin
GPIO_PIN_ATTACHMENTS[int(config['RESET']['gpio'])] = { "pull_up_down": 22, "event": 32, "command": "RESET" }

# This holds the Piano state at any moment
piano_state = PianoState(notes_state)

# This holds the PSX controller state at any moment
psx_controller_state = ControllerState(int(config['GAMEPLAY']['player']))

# Start the pianette
pianette = Pianette(piano_state, psx_controller_state)

# Instanciate the global GPIO Controller
# Its responsibility is to set piano and controller states based on GPIO inputs
gpio_controller = GPIOController(piano_state, psx_controller_state, GPIO_PIN_ATTACHMENTS)

# Run main loop
Debug.println("NOTICE", "Entering main loop")
PianetteCmd(piano_state, psx_controller_state).cmdloop()
