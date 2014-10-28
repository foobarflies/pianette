# coding: utf-8

from pianette.utils import Debug

class ControllerState:

  def __init__(self, configobj=None):
      self.configobj = configobj

      self.state = {}
      try:
          self.state = { k: False for k in self.configobj['Console']['supported-controls'] }
      except KeyError:
          pass

  def __str__(self):
    state_string = ""
    for control, state in self.state.items():
      if (state == True):
        state_string += control + " "

    return state_string

  def raiseFlag(self, flag):
    self.state[flag] = True

  def clearFlag(self, flag):
    self.state[flag] = False

  def toggleFlag(self, flag):
    self.state[flag] = not self.state[flag]

  def clearFlags(self):
    for control, state in self.state.items():
      self.state[control] = False
