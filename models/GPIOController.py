from utils import *

import RPi.GPIO as GPIO

"""
# Global GPIO Pin to Piano Note Mapping
"""
PIANO_NOTE_FOR_GPIO_PIN = {   
    # Bank 1, Octave -1
    5: "LEFT",    # Do
    6: "LEFT2",   # Ré
    13: "CL",     # Mi
    19: "DOWN",   # Fa
    26: "CL2",    # Sol

    # Bank 2, Octave -1
    21: "RIGHT",  # La
    20: "CL3",    # Sib
    16: "RIGHT2", # Si
    12: "CL4",    # Do
    25: None,

    # Bank 3, Octave 1
    24: "S",      # Do
    23: "O",      # Ré
    18: "CR",     # Mib
    15: "X",      # Mi
    14: "S2",     # Fa

    # Bank 4, Octave 1
    2: "CR2",     # Solb
    3: "O2",      # Sol
    4: "T",       # La
    17: "CR3",    # Sib
    27: "T2",     # Si

    # N/A : "SELECT",
    # N/A : "START",
}

class GPIOController:

  # GPIO Pin 22 is used for the reset key
  RESET_KEY = 22

  def __init__(self, stateController, app):
    self.stateController = stateController
    if (app):
      self.app = app

    Debug.println("INFO", "Attaching pins ...")

    ## Attach a callback to the RESET pin when it brought LOW
    Debug.println("SUCCESS", "Pin %s => RESET switch" % self.RESET_KEY )
    GPIO.setup(self.RESET_KEY, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(self.RESET_KEY, GPIO.FALLING, callback=self.gpio_reset, bouncetime=300)

    ## Attach a callback to each INPUT pin
    for pin, button in PIANO_NOTE_FOR_GPIO_PIN.items():
      Debug.println("SUCCESS", "Pin %s => %s" % (pin, button) )
      try:
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)
      except Exception:
        Debug.println("FAIL", "Pin %s (%s) already in use." % (pin, button))

  # Callback for the RESET button
  def gpio_reset(self, channel):

    Debug.println("INFO", "Pin %s activated : RESET" % (channel) )
    self.stateController.raiseFlag("RESET")

    if (self.app):
      # Updates the UI to reflect the trigger
      self.app.updateLabel("RESET")
      self.app.flashButton("RESET")

  # Callback for all action pins = keys
  def gpio_callback(self,channel):

    command = PIANO_NOTE_FOR_GPIO_PIN[channel]

    Debug.println("INFO", "Pin %s activated : Button %s" % (channel, command) )
    self.stateController.raiseFlag(command)

    if (self.app):
      # Updates the UI to reflect the trigger
      self.app.updateLabel(command)
      self.app.flashButton(command)

