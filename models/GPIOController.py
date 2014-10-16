# coding=utf-8

from utils import *

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# Just to be sure ...
# THIS LINE WILL ISSUE A WARNING THAT CAN HOPEFULLY BE IGNORED
GPIO.cleanup()

"""
# Global GPIO Pin Mapping
"""
GPIO_PIN_ATTACHMENTS = {
    # Bank 1
    5: { "note": "C3" },   # "LEFT"
    6: { "note": "D3" },   # "LEFT2"
    13: { "note": "E3" },  # "CL"
    19: { "note": "F3" },  # "DOWN"
    26: { "note": "G3" },  # "CL2"

    # Bank 2
    21: { "note": "A4" },  # "RIGHT"
    20: { "note": "B♭4" }, # "CL3"
    16: { "note": "B4" },  # "RIGHT2"
    12: { "note": "C" },   # "CL4"
    25: None,
    22: { "pull_up_down": GPIO.PUD_UP, "event": GPIO.FALLING, "command": "RESET" },

    # Bank 3
    24: { "note": "C5" },  # "S"
    23: { "note": "D5" },  # "O"
    18: { "note": "E♭5" }, # "CR"
    15: { "note": "E5" },  # "X"
    14: { "note": "F5" },  # "S2"

    # Bank 4
    2: { "note": "G♭5" },  # "CR2"
    3: { "note": "G5" },   # "O2"
    4: { "note": "A6" },   # "T"
    17: { "note": "B♭6" }, # "CR3"
    27: { "note": "B6" },  # "T2"
}

class GPIOController:
    def __init__(self, piano_state, controller_state):
        self.piano_state = piano_state
        self.controller_state = controller_state

        # Attach callbacks to pins
        Debug.println("INFO", "Attaching event callbacks to pins ...")

        for pin, attachment in GPIO_PIN_ATTACHMENTS.items():
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
                    Debug.println("FAIL", "Pin %2d already in use." % (pin))
                    raise
                Debug.println("SUCCESS", "Pin %2d attached to %s" % (pin, callback_description) )
            else:
                Debug.println("SUCCESS", "Pin %2d not attached" % (pin) )

    def __del__(self):
        # Cleanup GPIOs on object destruction
        GPIO.cleanup()

    # Callback method for PSX Controller Commands
    def gpio_pin_command_callback(self, channel):
        command = GPIO_PIN_ATTACHMENTS[channel]["command"]
        Debug.println("INFO", "Pin %2d activated : triggering PSX Controller Command %s" % (channel, command) )
        self.controller_state.raiseFlag("RESET")

    # Callback method for Piano Notes
    def gpio_pin_note_callback(self,channel):
        note = GPIO_PIN_ATTACHMENTS[channel]["note"]
        Debug.println("INFO", "Pin %2d activated : triggering Piano Note %s" % (channel, note) )
        self.piano_state.play_note(note)
