from utils import *

import glob
import serial
import threading
import time
import random

usleep = lambda x: time.sleep(x/1000000.0)

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

    # Start the thread that permanently writes the controller state
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
      self.sendStateBytes()
