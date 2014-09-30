#!/usr/bin/python3

from tkinter import *
from models import *
import RPi.GPIO as GPIO
	
class SNESController:

  def sendSNESCommand(self, command):
    global app
    print("Command :", command)
    app.updateLabel(command)
    app.flashButton(command)

  def quitController(self):
    global appWindow
    appWindow.destroy()

snesCtrl = SNESController()

appWindow = Tk()
appWindow.title = "SNES Controller"

# Set fullscreen
appWindow.geometry("{0}x{1}+0+0".format(appWindow.winfo_screenwidth(), appWindow.winfo_screenheight()))
appWindow.focus_set()  # <-- move focus to this widget
appWindow.bind("<Escape>", lambda e: e.widget.destroy())

# Inject the controller in the "view"
app = SNESControllerWindow(appWindow, snesCtrl)

# Now loads the GPIO Controller
snesGPIO = SNESGPIOController(app, snesCtrl)

# Run main loop
appWindow.mainloop()

# Cleanup
GPIO.cleanup()


