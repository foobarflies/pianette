import RPi.GPIO as GPIO

class GPIOController:

  # Mapping
  KEYS  = {   
            # Bank 1, Octave -1
            5: "DOWN",
            6: "S",
            13: "O",
            19: "X",
            26: "LEFT",

            # Bank 2, Octave 0
            21: "T",
            20: "UP",
            16: "O",
            12: "X",
            25: "LEFT",

            # Bank 3, Octave 1
            24: "T",
            23: "S",
            18: "DOWN",
            15: "X",
            14: "RIGHT",

            # Bank 4, Octave 2
            2: "T",
            3: "S",
            4: "O",
            17: "UP",
            27: "RIGHT",

            # N/A : "SELECT",
            # N/A : "START",
          }

  # GPIO 22 is used for the reset key
  RESET_KEY = 22

  def __init__(self, stateController, app):
    self.stateController = stateController
    if (app):
      self.app = app

    ## Attach a callback to the RESET pin when it brought LOW
    print("Attaching single pin %s for RESET switch" % RESET_KEY )
      GPIO.setup(RESET_KEY, GPIO.IN, pull_up_down = GPIO.PUD_UP)
      GPIO.add_event_detect(RESET_KEY, GPIO.FALLING, callback=self.gpio_reset, bouncetime=300)

    ## Attach a callback to each INPUT pin
    for pin, button in self.KEYS.items():
      print("Attaching pin %s for button %s" % (pin, button) )
      GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
      GPIO.add_event_detect(pin, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)

  # Callback for the RESET button
  def gpio_reset(self, channel):

    print("Pin %s activated : RESET" % (channel) )
    self.stateController.raiseFlag("RESET")

    if (self.app):
      # Updates the UI to reflect the trigger
      self.app.updateLabel("RESET")
      self.app.flashButton("RESET")

  # Callback for all action pins = keys
  def gpio_callback(self,channel):

    command = self.KEYS[channel]

    print("Pin %s activated : Button %s" % (channel, command) )
    self.stateController.raiseFlag(command)

    if (self.app):
      # Updates the UI to reflect the trigger
      self.app.updateLabel(command)
      self.app.flashButton(command)

