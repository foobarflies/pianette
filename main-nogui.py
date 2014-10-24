#!/usr/bin/env python3

from pianette.ControllerState import ControllerState
from pianette.GPIOController import GPIOController
from pianette.Pianette import Pianette
from pianette.PianoState import PianoState
from pianette.utils import Debug
from pianette.utils import ReadChar

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

# This holds the Piano state at any moment
piano_state = PianoState()

# This holds the PSX controller state at any moment
psx_controller_state = ControllerState(config['DEFAULT']['player'])

# Start the pianette
pianette = Pianette(piano_state, psx_controller_state)

# Instanciate the global GPIO Controller
# Its responsibility is to set piano and controller states based on GPIO inputs
gpio_controller = GPIOController(piano_state, psx_controller_state)

# Run main loop
Debug.println("NOTICE", "Entering main loop")

while (True):
  with ReadChar() as rc:
    char = rc
    # FIX ME FIX ME if char in {allowed_chars} ??
    if ord(char) > 32:
      Debug.println("INFO", "Key : {}".format(char))
      try:
        psx_controller_state.toggleFlag(char)
      except Exception:
        Debug.println("FAIL", "This key does not correspond to any ControllerState flag")
    if ord(char) == 3: # ^C
      Debug.println("WARNING", "Exiting ... Press CTRL+C again to quit.")
      # FIX ME Stop threads ??
      sys.exit()
  pass
