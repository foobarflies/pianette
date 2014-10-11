import serial

class ControllerState:

  serialConnection = False;

  # Mapping
  state = { "T" : False,
            "S" : False,
            "X" : False,
            "O" : False,
            "TOP" : False,
            "BOTTOM" : False,
            "RIGHT" : False,
            "LEFT" : False,
            "SELECT" : False,
            "START" : False,
          }

  def __init__(self):

    self.serialConnection = serial.Serial('/dev/ttyACM0', 115200)

  def __str__(self):

    state_string = ""
    for button, state in self.state.items():
      if (state == True):
        state_string += button + " "

    return state_string

  def raiseFlag(self, flag):
    self.state[flag] = True

    # Sends the command out to the Arduino
    # FIX ME ONLY a CHAR here
    self.serialConnection.write(flag);

  def clearFlag(self, flag):
    self.state[flag] = False

  def clearFlags(self):
    for button, state in self.state.items():
      self.state[button] = False
