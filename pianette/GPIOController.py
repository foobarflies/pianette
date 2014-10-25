# coding: utf-8

from pianette.utils import Debug
import warnings

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# We want to be able to catch warnings, expecially the RuntimeWarning when a pin is already attached
warnings.filterwarnings('error')

# Just to be sure ...
# THIS LINE WILL ISSUE A WARNING THAT CAN HOPEFULLY BE IGNORED
# GPIO.cleanup()


class GPIOController:
    
    # Global GPIO Pin Mapping
    GPIO_PIN_ATTACHMENTS = None

    def __init__(self, piano_state, controller_state, GPIO_PIN_ATTACHMENTS):
        self.piano_state = piano_state
        self.controller_state = controller_state
        self.GPIO_PIN_ATTACHMENTS = GPIO_PIN_ATTACHMENTS

        # Attach callbacks to pins
        Debug.println("INFO", "Attaching event callbacks to pins ...")

        for pin, attachment in self.GPIO_PIN_ATTACHMENTS.items():
            if attachment:
                pull_up_down = attachment.get("pull_up_down", GPIO.PUD_DOWN)
                event = attachment.get("event", GPIO.RISING)

                callback = None
                callback_description = None

                if "note" in attachment:
                    callback = self.gpio_pin_note_callback
                    callback_description = "Note %s" % attachment["note"]
                elif "command" in attachment:
                    callback = self.gpio_pin_command_callback
                    callback_description = "Command %s" % attachment["command"]
                if callback is None:
                    Debug.println("FAIL", "Could not attach event callback for pin %2d" % (pin))
                    raise Exception()

                try:
                    GPIO.setup(pin, GPIO.IN, pull_up_down = pull_up_down)
                    GPIO.add_event_detect(pin, event, callback=callback, bouncetime=300)
                except Exception:
                    if (pin in {14, 15, 18}): # UART Pins, we can override
                        Debug.println("WARNING", "UART Pin %2d already in use. Overriding ..." % (pin))
                    else: # Nope nope nope nope, nope.
                        Debug.println("FAIL", "Pin %2d already in use." % (pin))
                        raise
                Debug.println("SUCCESS", "Pin %2d attached to %s" % (pin, callback_description) )
            else:
                Debug.println("WARNING", "Pin %2d not attached" % (pin) )


        self.gpio_check()

    def __del__(self):
        # Cleanup GPIOs on object destruction
        GPIO.cleanup()

    # Check pin function
    def gpio_check(self):
        for pin, attachment in self.GPIO_PIN_ATTACHMENTS.items():
            mode = GPIO.gpio_function(pin)
            if (mode == GPIO.IN):
                Debug.println("INFO", "Pin %2d : INPUT" % pin)

            if (mode == GPIO.OUT):
                Debug.println("INFO", "Pin %2d : OUTPUT" % pin)

            if (mode == GPIO.I2C):
                Debug.println("INFO", "Pin %2d : I2C" % pin)

            if (mode == GPIO.SPI):
                Debug.println("INFO", "Pin %2d : SPI" % pin)

            if (mode == GPIO.HARD_PWM):
                Debug.println("INFO", "Pin %2d : HARD_PWM" % pin)

            if (mode == GPIO.SERIAL):
                Debug.println("INFO", "Pin %2d : SERIAL" % pin)

            if (mode == GPIO.UNKNOWN):
                Debug.println("INFO", "Pin %2d : UNKNOWN" % pin)

    # Callback method for PSX Controller Commands
    def gpio_pin_command_callback(self, channel):
        command = self.GPIO_PIN_ATTACHMENTS[channel]["command"]
        Debug.println("INFO", "Pin %2d activated : triggering PSX Controller Command %s" % (channel, command) )
        self.controller_state.raiseFlag("RESET")

    # Callback method for Piano Notes
    def gpio_pin_note_callback(self,channel):
        note = self.GPIO_PIN_ATTACHMENTS[channel]["note"]
        Debug.println("INFO", "Pin %2d activated : triggering Piano Note %s" % (channel, note) )
        self.piano_state.raise_note(note)
