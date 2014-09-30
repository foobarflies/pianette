from tkinter import *
from time import sleep

class SNESControllerWindow(Frame):


  def __init__(self, base, snesController):
    super(SNESControllerWindow, self).__init__(base)

    self.snesController = snesController

    self.grid()
    self.createButtons()
    self.createUtilityButtons()

  def createUtilityButtons(self):
# Quit button
    self.BUTTON_QUIT = Button(self)
    self.BUTTON_QUIT["text"] = "Quit"
    self.BUTTON_QUIT["command"] = lambda: self.snesController.quitController()	
    self.BUTTON_QUIT.grid(row=5	, column=4, columnspan=2)

# Label for commands
    self.LABEL_CMD = Label(self)
    self.LABEL_CMD["text"] = ""
    self.LABEL_CMD["relief"] = SUNKEN
    self.LABEL_CMD.grid(row=0, column=4	, columnspan=2, padx=1, pady=1)

# Placeholder for swag
    self.LABEL_PLACEHOLDER = Label(self)
    self.LABEL_PLACEHOLDER["text"] = "  "
    self.LABEL_PLACEHOLDER.grid(row=1, column=4	, columnspan=2)

  def createButtons(self):

# A Button
    self.BUTTON_A = Button(self)
    self.BUTTON_A["bg"] = "red"
    self.BUTTON_A["activebackground"] = "red"
    self.BUTTON_A["fg"] = "white"
    self.BUTTON_A["height"] = 1
    self.BUTTON_A["width"] = 1
    self.BUTTON_A["text"] = "A"
    self.BUTTON_A["command"] = lambda: self.snesController.sendSNESCommand("A")
    self.BUTTON_A.grid(row=3, column=10)
# B Button
    self.BUTTON_B = Button(self)
    self.BUTTON_B["bg"] = "yellow"
    self.BUTTON_B["activebackground"] = "yellow"
    self.BUTTON_B["fg"] = "white"
    self.BUTTON_B["height"] = 1
    self.BUTTON_B["width"] = 1
    self.BUTTON_B["text"] = "B"
    self.BUTTON_B["command"] = lambda: self.snesController.sendSNESCommand("B")
    self.BUTTON_B.grid(row=4, column=9	)
# X Button
    self.BUTTON_X = Button(self)
    self.BUTTON_X["bg"] = "blue"
    self.BUTTON_X["activebackground"] = "blue"
    self.BUTTON_X["fg"] = "white"
    self.BUTTON_X["height"] = 1
    self.BUTTON_X["width"] = 1
    self.BUTTON_X["text"] = "X"
    self.BUTTON_X["command"] = lambda: self.snesController.sendSNESCommand("X")
    self.BUTTON_X.grid(row=2, column=9)
# Y Button
    self.BUTTON_Y = Button(self)
    self.BUTTON_Y["bg"] = "green"
    self.BUTTON_Y["activebackground"] = "green"
    self.BUTTON_Y["fg"] = "white"
    self.BUTTON_Y["height"] = 1
    self.BUTTON_Y["width"] = 1
    self.BUTTON_Y["text"] = "Y"
    self.BUTTON_Y["command"] = lambda: self.snesController.sendSNESCommand("Y")
    self.BUTTON_Y.grid(row=3, column=8)

# Movement Buttons
    self.BUTTON_LEFT = Button(self)
    self.BUTTON_LEFT["height"] = 1
    self.BUTTON_LEFT["width"] = 1
    self.BUTTON_LEFT["text"] = "◀"
    self.BUTTON_LEFT["command"] = lambda: self.snesController.sendSNESCommand("LEFT")
    self.BUTTON_LEFT.grid(row=3, column=1)
    self.BUTTON_RIGHT = Button(self)
    self.BUTTON_RIGHT["height"] = 1
    self.BUTTON_RIGHT["width"] = 1
    self.BUTTON_RIGHT["text"] = "▶"
    self.BUTTON_RIGHT["command"] = lambda: self.snesController.sendSNESCommand("RIGHT")
    self.BUTTON_RIGHT.grid(row=3, column=3)
    self.BUTTON_TOP = Button(self)
    self.BUTTON_TOP["height"] = 1
    self.BUTTON_TOP["width"] = 1
    self.BUTTON_TOP["text"] = "▲"
    self.BUTTON_TOP["command"] = lambda: self.snesController.sendSNESCommand("TOP")
    self.BUTTON_TOP.grid(row=2, column=2)
    self.BUTTON_BOTTOM = Button(self)
    self.BUTTON_BOTTOM["height"] = 1
    self.BUTTON_BOTTOM["width"] = 1
    self.BUTTON_BOTTOM["text"] = "▼"
    self.BUTTON_BOTTOM["command"] = lambda: self.snesController.sendSNESCommand("BOTTOM")
    self.BUTTON_BOTTOM.grid(row=4, column=2)

# Select and Start
    self.BUTTON_START = Button(self)
    self.BUTTON_START["bg"] = "grey"
    self.BUTTON_START["activebackground"] = "grey"
    self.BUTTON_START["fg"] = "white"
    self.BUTTON_START["height"] = 1
    self.BUTTON_START["text"] = "START"
    self.BUTTON_START["font"] = ('Helvetica', '7')
    self.BUTTON_START["command"] = lambda: self.snesController.sendSNESCommand("START")
    self.BUTTON_START.grid(row=3, column=5)
    self.BUTTON_SELECT = Button(self)
    self.BUTTON_SELECT["bg"] = "grey"
    self.BUTTON_SELECT	["activebackground"] = "grey"
    self.BUTTON_SELECT["fg"] = "white"
    self.BUTTON_SELECT["height"] = 1
    self.BUTTON_SELECT["text"] = "SEL"
    self.BUTTON_SELECT["font"] = ('Helvetica', '7')
    self.BUTTON_SELECT["command"] = lambda: self.snesController.sendSNESCommand("SELECT")
    self.BUTTON_SELECT.grid(row=3, column=7)

  def getButtonForCommand(self, command):

    buttons = {"A" : self.BUTTON_A,
             "B" : self.BUTTON_B,
             "X" : self.BUTTON_X,
             "Y" : self.BUTTON_Y,
             "SELECT" : self.BUTTON_SELECT,
             "START" : self.BUTTON_START,
             "LEFT" : self.BUTTON_LEFT,
             "RIGHT" : self.BUTTON_RIGHT,
             "TOP" : self.BUTTON_TOP,
             "BOTTOM" : self.BUTTON_BOTTOM,
    }

    return buttons[command]

  def updateLabel(self, command):
    self.LABEL_CMD["text"] = command

  def flashButton(self, command):
    button = self.getButtonForCommand(command)
    button.flash()


