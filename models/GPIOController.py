import RPi.GPIO as GPIO

class GPIOController:

  # Pinout
  KEY_1 = 15
  KEY_2 = 3

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
            # We can have doubles
          }

  def __init__(self, stateController, app):
    self.stateController = stateController
    self.app = app

    for pin, button in self.KEYS.items():
      GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
      GPIO.add_event_detect(pin, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)

    # FORCE Flex Sensor : needs PULLUP with other side to GND
    #GPIO.setup(GPIOController.KEY_1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    #GPIO.add_event_detect(GPIOController.KEY_1, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)

  def gpio_callback(self,channel):

    command = self.KEYS[channel]

    print("Pin %s activated : Button %s" % (channel, command) )
    self.stateController.raiseFlag(command)

    # Updates the UI to reflect the trigger
    self.app.updateLabel(command)
    self.app.flashButton(command)

