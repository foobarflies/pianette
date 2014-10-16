from utils import *

import glob
import serial
import threading
import time
import random

usleep = lambda x: time.sleep(x/1000000.0)

# Number of µsecs that we need to wait between commands from controller
usecs_between_data = 1

class ConsoleController:

  serialConnection = None;

  def __init__(self, stateController):
    self.stateController = stateController
    # Tries to find correct Serial port
    open_ports = self.getSerialPorts()

    # Opens first port available
    try:
      self.serialConnection = serial.Serial(open_ports[0], 115200)
      Debug.println("INFO", "SPI Slave detected at %s, waiting for the port to initialize." % open_ports[0])
      time.sleep(3) # DIRTY but apparently required for the serial port to get fully ready
      Debug.println("SUCCESS", "SPI Slave initialized.")
    except Exception:
      self.serialConnection = None
      Debug.println("WARNING", "No ConsoleController SPI Slave detected.")
    
    # Seeds random for stage selection
    random.seed()

    # Start the thread that permantently writes the controller state
    csThread = threading.Thread(target=self.sendStateBytesWorker)
    csThread.daemon = True
    csThread.start()

  def getSerialPorts(self):

    temp_list = glob.glob ('/dev/ttyACM*')
    result = []
    for a_port in temp_list:
        try:
            s = serial.Serial (a_port)
            s.close ()
            result.append (a_port)
        except serial.SerialException:
            pass
    return result

  # Single buttons
  def sendX(self):
    self.serialConnection.write(b'\xFF\xBF')
  def sendO(self):
    self.serialConnection.write(b'\xFF\xDF')
  def sendSquare(self):
    self.serialConnection.write(b'\xFF\x7F')
  def sendTriangle(self):
    self.serialConnection.write(b'\xFF\xEF')

  def sendStart(self):
    self.serialConnection.write(b'\xF7\xFF')
  def sendSelect(self):
    self.serialConnection.write(b'\xF7\xFE')

  def sendUp(self):
    self.serialConnection.write(b'\xEF\xFF')
  def sendDown(self):
    self.serialConnection.write(b'\xBF\xFF')
  def sendLeft(self):
    self.serialConnection.write(b'\x7F\xFF')
  def sendRight(self):
    self.serialConnection.write(b'\xDF\xFF')

  # Simple movement combos
  def sendDownRight(self):
    # RIGHT + DOWN
    self.serialConnection.write(b'\x9F\xFF')
  def sendDownLeft(self):
    # LEFT + DOWN
    self.serialConnection.write(b'\x3F\xFF')
  def sendUpRight(self):
    # RIGHT + UP
    self.serialConnection.write(b'\xCF\xFF')
  def sendUpLeft(self):
    # LEFT + UP
    self.serialConnection.write(b'\x6F\xFF')

  # Send a reset byte couple, going back to the menus
  def sendReset(self):
    self.serialConnection.write(b'\x00\x00')

  # Methods 
  def restartFresh(self):
    # Back to main menu
    self.sendReset()
    usleep(usecs_between_data)
    self.sendStart()
    usleep(usecs_between_data)
    # Choose "VERSUS" mode
    self.chooseVersusModeFromMenu()
    self.newGameFromVersusMenu()
    
  def restartSuperFresh(self):
    # Back to start
    self.sendReset()
    usleep(usecs_between_data)
    self.restartFresh()
    
  def chooseVersusModeFromMenu(self):
    self.sendLeft()
    usleep(usecs_between_data)
    self.sendX()
    usleep(usecs_between_data)

  def newGameFromVersusMenu(self):
    # Choose random character
    if (self.stateController.playerOne == True):
      self.sendRight()
    else:
      self.sendLeft()
    usleep(usecs_between_data)
    self.sendUp()
    usleep(usecs_between_data)
    self.sendUp()
    usleep(usecs_between_data)
    # Acknowledge handicap
    self.sendX()
    usleep(usecs_between_data)
    # Acknowledge Battle field - we choose a random stage going right >>
    stage = random.randint(1, 10)
    for x in xrange(1,stage):
      self.sendRight()
      usleep(usecs_between_data)
    self.sendX()
    usleep(usecs_between_data)

    # Wait two seconds for cinematic
    time.sleep(2)

    # FIGHT !!!!

  def sendStateBytes(self):
    stateByte1 = (
      (0b00000001 if self.stateController.state["SELECT"] else 0) |
      (0b00001000 if self.stateController.state["START"] else 0) |
      (0b00010000 if self.stateController.state["UP"] else 0) |
      (0b00100000 if self.stateController.state["RIGHT"] else 0) |
      (0b01000000 if self.stateController.state["DOWN"] else 0) |
      (0b10000000 if self.stateController.state["LEFT"] else 0)
    ) ^ 0xff

    stateByte2 = (
      (0b00010000 if self.stateController.state["T"] else 0) |
      (0b00100000 if self.stateController.state["O"] else 0) |
      (0b01000000 if self.stateController.state["X"] else 0) |
      (0b10000000 if self.stateController.state["S"] else 0)
    ) ^ 0xff

    # Send the command out to the Arduino controller through serial connection
    if (self.serialConnection):
      self.serialConnection.write(bytes([stateByte1, stateByte2]))
    # else: 
    #  Debug.println("INFO", "Bytes lost %d %d" % (stateByte1, stateByte2))

  def sendStateBytesWorker(self):
    while True:
      lock = threading.Lock()
      lock.acquire()
      self.sendStateBytes()
      lock.release()
