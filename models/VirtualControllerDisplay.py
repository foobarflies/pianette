from tkinter import *
from time import sleep

class VirtualControllerDisplay(Frame):

  def __init__(self, base, stateController):
    super(VirtualControllerDisplay, self).__init__(base)

    self.stateController = stateController
    self.base = base # appWindow

    self.grid()
    self.createButtons()
    self.createUtilityButtons()
    print("  # VirtualControllerDisplay : INFO : Gui created.")

  def createUtilityButtons(self):
# Quit button
    self.BUTTON_QUIT = Button(self)
    self.BUTTON_QUIT["text"] = "Quit"
    self.BUTTON_QUIT["command"] = lambda: self.base.destroy()
    self.BUTTON_QUIT.grid(row=7, column=5)

# Reset button
    self.BUTTON_RESET = Button(self)
    self.BUTTON_RESET["text"] = "Reset"
    self.BUTTON_RESET["command"] = lambda: self.buttonAction("RESET")  
    self.BUTTON_RESET.grid(row=7, column=6)

# Label for commands
    self.LABEL_CMD = Label(self)
    self.LABEL_CMD["text"] = "..."
    self.LABEL_CMD["relief"] = SUNKEN
    self.LABEL_CMD["font"] = ('Helvetica', '16')
    self.LABEL_CMD.grid(row=1, column=5	, columnspan=2, padx=1, pady=1, sticky="we")

# Placeholder for swag
    self.LABEL_PLACEHOLDER = Label(self)
    self.LABEL_PLACEHOLDER["text"] = "  "
    self.LABEL_PLACEHOLDER.grid(row=0, column=4	, columnspan=2)

# Placeholder for swag
    self.LABEL_PLACEHOLDER = Label(self)
    self.LABEL_PLACEHOLDER["text"] = "  "
    self.LABEL_PLACEHOLDER.grid(row=2, column=4	, columnspan=2)

# Placeholder for swag
    self.LABEL_PLACEHOLDER = Label(self)
    self.LABEL_PLACEHOLDER["text"] = "  "
    self.LABEL_PLACEHOLDER["font"] = ('Helvetica', '30')
    self.LABEL_PLACEHOLDER.grid(row=6, column=4	, columnspan=2)

  def createButtons(self):

# O Button
    self.BUTTON_O = Button(self)
    self.BUTTON_O["bg"] = "darkGray"
    self.BUTTON_O["activebackground"] = "darkGray"
    self.BUTTON_O["fg"] = "red"
    self.BUTTON_O["height"] = 1
    self.BUTTON_O["width"] = 1
    self.BUTTON_O["text"] = "◯"
    self.BUTTON_O["command"] = lambda: self.buttonAction("O")
    self.BUTTON_O.grid(row=4, column=9)
# X Button
    self.BUTTON_X = Button(self)
    self.BUTTON_X["bg"] = "darkGray"
    self.BUTTON_X["activebackground"] = "darkGray"
    self.BUTTON_X["fg"] = "blue"
    self.BUTTON_X["height"] = 1
    self.BUTTON_X["width"] = 1
    self.BUTTON_X["text"] = "✕"
    self.BUTTON_X["command"] = lambda: self.buttonAction("X")
    self.BUTTON_X.grid(row=5, column=8)
# TRIANGLE Button
    self.BUTTON_T = Button(self)
    self.BUTTON_T["bg"] = "darkGray"
    self.BUTTON_T["activebackground"] = "darkGray"
    self.BUTTON_T["fg"] = "green"
    self.BUTTON_T["height"] = 1
    self.BUTTON_T["width"] = 1
    self.BUTTON_T["text"] = "△"
    self.BUTTON_T["command"] = lambda: self.buttonAction("T")
    self.BUTTON_T.grid(row=3, column=8)
# SQUARE Button
    self.BUTTON_S = Button(self)
    self.BUTTON_S["bg"] = "darkGray"
    self.BUTTON_S["activebackground"] = "darkGray"
    self.BUTTON_S["fg"] = "pink"
    self.BUTTON_S["height"] = 1
    self.BUTTON_S["width"] = 1
    self.BUTTON_S["text"] = "▢"
    self.BUTTON_S["command"] = lambda: self.buttonAction("S")
    self.BUTTON_S.grid(row=4, column=7)

# Movement Buttons
    self.BUTTON_LEFT = Button(self)
    self.BUTTON_LEFT["bg"] = "darkSlateGray"
    self.BUTTON_LEFT["activebackground"] = "darkSlateGray"
    self.BUTTON_LEFT["height"] = 1
    self.BUTTON_LEFT["width"] = 1
    self.BUTTON_LEFT["text"] = "◀"
    self.BUTTON_LEFT["command"] = lambda: self.buttonAction("LEFT")
    self.BUTTON_LEFT.grid(row=4, column=1)
    self.BUTTON_RIGHT = Button(self)
    self.BUTTON_RIGHT["bg"] = "darkSlateGray"
    self.BUTTON_RIGHT["activebackground"] = "darkSlateGray"
    self.BUTTON_RIGHT["height"] = 1
    self.BUTTON_RIGHT["width"] = 1
    self.BUTTON_RIGHT["text"] = "▶"
    self.BUTTON_RIGHT["command"] = lambda: self.buttonAction("RIGHT")
    self.BUTTON_RIGHT.grid(row=4, column=3)
    self.BUTTON_UP = Button(self)
    self.BUTTON_UP["bg"] = "darkSlateGray"
    self.BUTTON_UP["activebackground"] = "darkSlateGray"
    self.BUTTON_UP["height"] = 1
    self.BUTTON_UP["width"] = 1
    self.BUTTON_UP["text"] = "▲"
    self.BUTTON_UP["command"] = lambda: self.buttonAction("UP")
    self.BUTTON_UP.grid(row=3, column=2)
    self.BUTTON_DOWN = Button(self)
    self.BUTTON_DOWN["bg"] = "darkSlateGray"
    self.BUTTON_DOWN["activebackground"] = "darkSlateGray"
    self.BUTTON_DOWN["height"] = 1
    self.BUTTON_DOWN["width"] = 1
    self.BUTTON_DOWN["text"] = "▼"
    self.BUTTON_DOWN["command"] = lambda: self.buttonAction("DOWN")
    self.BUTTON_DOWN.grid(row=5, column=2)

# Select and Start
    self.FRAME_MIDDLE = Frame(self)
    self.FRAME_MIDDLE.grid(row=4, column=5, columnspan=2, sticky="we")
    self.FRAME_MIDDLE.grid_propagate(0)

    self.BUTTON_START = Button(self.FRAME_MIDDLE)
    self.BUTTON_START["bg"] = "grey"
    self.BUTTON_START["activebackground"] = "grey"
    self.BUTTON_START["fg"] = "white"
    self.BUTTON_START["height"] = 1
    self.BUTTON_START["text"] = "START"
    self.BUTTON_START["font"] = ('Helvetica', '7')
    self.BUTTON_START["command"] = lambda: self.buttonAction("START")
    self.BUTTON_START.pack(side=LEFT)
    self.BUTTON_SELECT = Button(self.FRAME_MIDDLE)
    self.BUTTON_SELECT["bg"] = "grey"
    self.BUTTON_SELECT["activebackground"] = "grey"
    self.BUTTON_SELECT["fg"] = "white"
    self.BUTTON_SELECT["height"] = 1
    self.BUTTON_SELECT["text"] = "SEL"
    self.BUTTON_SELECT["font"] = ('Helvetica', '7')
    self.BUTTON_SELECT["command"] = lambda: self.buttonAction("SELECT")
    self.BUTTON_SELECT.pack(side=LEFT)
 
  def buttonAction(self, command):
    self.stateController.raiseFlag(command)
    self.updateLabel(command)
    self.flashButton(command)

  def getButtonForCommand(self, command):

    buttons = { "O" : self.BUTTON_O,
                "X" : self.BUTTON_X,
                "T" : self.BUTTON_T,
                "S" : self.BUTTON_S,
                "SELECT" : self.BUTTON_SELECT,
                "START" : self.BUTTON_START,
                "LEFT" : self.BUTTON_LEFT,
                "RIGHT" : self.BUTTON_RIGHT,
                "UP" : self.BUTTON_UP,
                "DOWN" : self.BUTTON_DOWN,
                "RESET" : self.BUTTON_RESET,
              }

    return buttons[command]

  def updateLabel(self, command):
    self.LABEL_CMD["text"] = command
    self.base.update()

  def flashButton(self, command):
    button = self.getButtonForCommand(command)
    button.flash()


