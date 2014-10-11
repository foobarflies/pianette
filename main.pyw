#!/usr/bin/env python3

from tkinter import *
from models import *

import logging
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

appWindow = Tk()
appWindow.title("Virtual Controller")

# Set fullscreen [Not necessary when debugging]
# appWindow.geometry("{0}x{1}+0+0".format(appWindow.winfo_screenwidth(), appWindow.winfo_screenheight()))
appWindow.focus_set()  # <-- move focus to this widget
# Binds <Escape> key to quit the program
appWindow.bind("<Escape>", lambda e: e.widget.destroy())
# Removes the title bar and menu bar
appWindow.overrideredirect(True)

# This holds the controller state at any moment
ctrlState = ControllerState()

# The virtual controller can set state flags via the UI
app = VirtualControllerDisplay(appWindow, ctrlState)

# Instantiate the console controller that will send out the state to the console when needed
consoleCtrl = ConsoleController(ctrlState)

# Now loads the GPIO Controller that will set state flags depending on the GPIO inputs
# It needs the app to flash the buttons
gpioCtrl = GPIOController(ctrlState, app)

# Run main loop
appWindow.mainloop()

# Cleanup GPIOs
GPIO.cleanup()


