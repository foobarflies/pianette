#!/usr/bin/env python3

from models import *
from utils import *

# Read config
import configparser
config = configparser.ConfigParser()
config.read('conf.ini')

# Set GPIO Mode
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Just to be sure ...
# THIS LINE WILL HOPEFULLY ISSUE A WARNING THAT CAN BE IGNORED
GPIO.cleanup()

# This holds the controller state at any moment
ctrlState = ControllerState(config['DEFAULT']['player'])

# Instantiate the console controller that will send out the state to the console when needed
consoleCtrl = ConsoleController(ctrlState)

# Start the thread that permantently writes the controller state
import threading
def csThreadWorker():
  while True:
    lock = threading.Lock()
    lock.acquire()
    consoleCtrl.sendStateBytes()
    lock.release()

csThread = threading.Thread(target=csThreadWorker)
csThread.daemon = True
csThread.start()

# Start the timing thread
csTimedBuffer = ControllerStateTimedBuffer(ctrlState, consoleCtrl)
csTimedBufferThread = threading.Thread(target=csTimedBuffer.popStateBuffers)
csTimedBufferThread.daemon = True
csTimedBufferThread.start()

# Now loads the GPIO Controller that will set state flags depending on the GPIO inputs
gpioCtrl = GPIOController(ctrlState, False)

# Run main loop
Debug.println("NOTICE", "Entering main loop")

while (True):
  with ReadChar() as rc:
    char = rc
    # FIX ME FIX ME if char in {allowed_chars} ??
    if ord(char) > 32:
      print("{} ".format(char))
      ctrlState.toggleFlag(char)
    if ord(char) == 3: # ^C
      # Cleanup GPIOs
      GPIO.cleanup()
      # FIX ME Stop threads ??
      sys.exit()
  pass
