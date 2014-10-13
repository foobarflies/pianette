#!/usr/bin/env python3

from models import *

"""
Implementation of a way to get a single character of input
without waiting for the user to hit <Enter>.
(OS is Linux, Ubuntu 14.04)
"""

import tty, sys, termios

class ReadChar():
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

import RPi.GPIO as GPIO

# Read config
import configparser
config = configparser.ConfigParser()
config.read('conf.ini')

GPIO.setmode(GPIO.BCM)

# Just to be sure
# THIS LINE WILL HOPEFULLY ISSUE A WARNING THAT CAN BE IGNORED
GPIO.cleanup()

# This holds the controller state at any moment
ctrlState = ControllerState(config['DEFAULT']['player'])

# Instantiate the console controller that will send out the state to the console when needed
consoleCtrl = ConsoleController(ctrlState)

# Now loads the GPIO Controller that will set state flags depending on the GPIO inputs
# It needs the app to flash the buttons
gpioCtrl = GPIOController(ctrlState, False)

# Run main loop
while (True):
  with ReadChar() as rc:
    char = rc
    # FIX ME FIX ME
    if ord(char) <= 32:
      print("You entered character with ordinal {}.".format(ord(char)))
    else:
      print("You entered character '{}'.".format(char))
    if char in "^C^D":
      # Cleanup GPIOs
      GPIO.cleanup()
      sys.exit()
  pass



