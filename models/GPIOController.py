import RPi.GPIO as GPIO

class GPIOController:

  # Mapping
  KEYS  = { 15 : "T",
            3 : "S",
            # 5 : "X",
            # 6 : "O",
            # 7 : "TOP",
            # 8 : "BOTTOM",
            # 9 : "RIGHT"
            # 10 : "LEFT",
            # 11 : "SELECT",
            # 12 : "START",
            # We can have doubles : two GPIO that trigger the same controller keys
          }

  def __init__(self, stateController, app):
    self.stateController = stateController
    self.app = app

    ## Attach a callback to each INPUT pin
    for pin, button in self.KEYS.items():
      print("Attaching pin %s for button %s" % (pin, button) )
      GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
      GPIO.add_event_detect(pin, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)

  def gpio_callback(self,channel):

    command = self.KEYS[channel]

    print("Pin %s activated : Button %s" % (channel, command) )
    self.stateController.raiseFlag(command)

    # Updates the UI to reflect the trigger
    self.app.updateLabel(command)
    self.app.flashButton(command)
    # Debug
    # print(self.stateController)

