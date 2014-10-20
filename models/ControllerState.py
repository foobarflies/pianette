from utils import *

class ControllerState:

  # Mapping
  state = {
            # Single buttons
            "T" : False,
            "S" : False,
            "S2" : False,
            "X" : False,
            "O" : False,
            "O2" : False,
            "UP" : False,
            "DOWN" : False,
            "RIGHT" : False,
            "RIGHT2" : False,
            "LEFT" : False,
            "LEFT2" : False,

            # Combo enablers, left and right
            "CR" : False,
            "CR2" : False,
            "CR3" : False,
            "CR4" : False,
            "CL" : False,
            "CL2" : False,
            "CL3" : False,

            # Control buttons
            "SELECT" : False,
            "START" : False,

            # Special Flag for restarting a game
            "RESET": False,
          }

  playerOne = True

  def __init__(self, player):
    if (player == 1):
      self.setPlayerOne()
      Debug.println("INFO", "Player is #1")
    else:
      self.setPlayerTwo()
      Debug.println("INFO", "Player is #2")

  def __str__(self):

    state_string = ""
    for button, state in self.state.items():
      if (state == True):
        state_string += button + " "

    return state_string

  def raiseFlag(self, flag):
    self.state[flag] = True

  def clearFlag(self, flag):
    self.state[flag] = False

  def toggleFlag(self, flag):
    self.state[flag] = not self.state[flag]

  def clearFlags(self):
    for button, state in self.state.items():
      self.state[button] = False

  def setPlayerOne(self):
    self.playerOne = True

  def setPlayerTwo(self):
    self.playerOne = False
