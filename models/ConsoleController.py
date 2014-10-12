import serial
import time

usleep = lambda x: time.sleep(x/1000000.0)

class ConsoleController:

  serialConnection = False;

  def __init__(self, stateController):
    self.stateController = stateController
    self.serialConnection = serial.Serial('/dev/ttyACM0', 115200)

  # Single buttons
  def sendX(self):
    ser.write(b'\xFF\xBF');
  def sendO(self):
    ser.write(b'\xFF\xDF');
  def sendSquare(self):
    ser.write(b'\xFF\x7F');
  def sendTriangle(self):
    ser.write(b'\xFF\xEF');

  def sendStart(self):
    ser.write(b'\xF7\xFF')
  def sendSelect(self):
    ser.write(b'\xF7\xFE')

  def sendUp(self):
    ser.write(b'\xEF\xFF');
  def sendDown(self):
    ser.write(b'\xBF\xFF');
  def sendLeft(self):
    ser.write(b'\x7F\xFF');
  def sendRight(self):
    ser.write(b'\xDF\xFF');

  def sendReset(self):
    ser.write(b'\x00\x00');

  # Methods 
  def restartFresh(self):
    # Back to main menu
    self.sendReset()
    usleep(1)
    # Choose "VERSUS" mode
    self.sendLeft())
    usleep(1)
    self.sendX()
    usleep(1)
    self.newGameFromVersusMenu()
    
  def restartSuperFresh(self):
    # Back to start
    self.sendReset()
    usleep(1)
    self.sendReset()
    usleep(1)
    self.restartFresh()
    
  def newGameFromVersusMenu(self):
    # Choose random character
    if (self.stateController.playerOne == True):
      self.sendRight()
    else:
      self.sendLeft()
    usleep(1)
    self.sendUp()
    usleep(1)
    self.sendUp()
    usleep(1)
    # Acknowledge handicap
    self.sendX()
    usleep(1)
    # Acknowledge Battle field
    # FIX ME PUT A RANDOM Left() here
    self.sendX()
    usleep(1)

    # We're in the fight !!!!

  def createStateBytes(self, channel):
    print("Sending state :", self.stateController)
    
    self.state_as_bytes = []

    self.state_as_bytes.append( # Data byte 1
      (0b00000001 if self.stateController.state["SELECT"] else 0) |
      (0b00001000 if self.stateController.state["START"] else 0) |
      (0b00010000 if self.stateController.state["TOP"] else 0) |
      (0b00100000 if self.stateController.state["RIGHT"] else 0) |
      (0b01000000 if self.stateController.state["BOTTOM"] else 0) |
      (0b10000000 if self.stateController.state["LEFT"] else 0)
    )

    self.state_as_bytes.append( # Data byte 2
      (0b00010000 if self.stateController.state["T"] else 0) |
      (0b00100000 if self.stateController.state["O"] else 0) |
      (0b01000000 if self.stateController.state["X"] else 0) |
      (0b10000000 if self.stateController.state["S"] else 0)
    )


    # Sends the command out to the Arduino
    # FIX ME ???
    ser.write(self.state_as_bytes)
    
