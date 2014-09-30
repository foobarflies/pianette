import RPi.GPIO as GPIO

class SNESGPIOController:

  # Pinout
  KEY_1 = 21

  def __init__(self, app, snesController):
    self.app = app
    self.snesController = snesController
    GPIO.setmode(GPIO.BCM)

# FOR EACH PIN
    # Flex Sensor : needs PULLUP with other side to GND
    GPIO.setup(SNESGPIOController.KEY_1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.add_event_detect(SNESGPIOController.KEY_1, GPIO.RISING, callback=self.detect, bouncetime=300)
# ENDFOR

# Will need to be extended for combos...
  def chooseCommandFromChannel(self, channel):
    if (channel == SNESGPIOController.KEY_1):
      return "A"

  def detect(self,channel):
    print("Channel %s activated" % channel)
    self.snesController.sendSNESCommand(self.chooseCommandFromChannel(channel))


