#!/usr/bin/env python3

# Resets all the GPIO to inputs to prevent
# electric pressure on the logic bus.
# Only GPIO 02 and 03 should remain High
# because of the hardware pull-up resistor
# on these pins

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pins = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,14,15,18,23,24,25,8,7,12,16,20,21]

try:
  for i in pins:
    GPIO.setup(i, GPIO.IN)
finally:
  GPIO.cleanup()
