# coding: utf-8

from pianette.utils import Debug

class ControllerState:

  # Mapping
  state = {
            # Directions
            "UP" : False,
            "DOWN" : False,
            "RIGHT" : False,
            "LEFT" : False,

            # Buttons
            "T" : False,
            "S" : False,
            "X" : False,
            "O" : False,
            "R1" : False,
            "L1" : False,
            "R2" : False,
            "L2" : False,

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
