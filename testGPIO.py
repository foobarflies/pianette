import RPi.GPIO as GPIO

class Test:

  # Mapping
  PINS  = {2,3,4,14,15,17,18,27,22,23,24,10,9,25,11,8,7,5,6,12,13,19,16,26,20,21}

  def __init__(self):

    ## Attach a callback to each INPUT pin
    for pin in self.PINS.items():
      print("Attaching pin GPIO%s ..." % pin )
      GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
      print("  Attaching event ...")
      GPIO.add_event_detect(pin, GPIO.RISING, callback=self.gpio_callback, bouncetime=300)
      print("  ... Done.")

  def gpio_callback(self,channel):

    print("Pin %s activated" % channel)


test = Test();

while (True):
  pass