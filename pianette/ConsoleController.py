# coding: utf-8

import glob
import serial
import time
import random

from pianette.utils import Debug

# Number of µsecs that we need to wait between commands from controller
usecs_between_data = 1

class ConsoleController:

  serialConnection = None;

  def __init__(self, psx_controller_state):
    self.psx_controller_state = psx_controller_state
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
      (0b00000001 if self.psx_controller_state.state["SELECT"] else 0) |
      (0b00001000 if self.psx_controller_state.state["START"] else 0) |
      (0b00010000 if self.psx_controller_state.state["UP"] else 0) |
      (0b00100000 if self.psx_controller_state.state["RIGHT"] else 0) |
      (0b01000000 if self.psx_controller_state.state["DOWN"] else 0) |
      (0b10000000 if self.psx_controller_state.state["LEFT"] else 0)
    ) ^ 0xff

    stateByte2 = (
      (0b00000001 if self.psx_controller_state.state["L2"] else 0) |
      (0b00000010 if self.psx_controller_state.state["R2"] else 0) |
      (0b00000100 if self.psx_controller_state.state["L1"] else 0) |
      (0b00001000 if self.psx_controller_state.state["R1"] else 0) |
      (0b00010000 if self.psx_controller_state.state["T"] else 0) |
      (0b00100000 if self.psx_controller_state.state["O"] else 0) |
      (0b01000000 if self.psx_controller_state.state["X"] else 0) |
      (0b10000000 if self.psx_controller_state.state["S"] else 0)
    ) ^ 0xff

    # Send the command out to the Arduino controller through serial connection
    if (self.serialConnection):
      self.serialConnection.write(bytes([stateByte1, stateByte2]))
    # else: 
    #  Debug.println("INFO", "Bytes lost %d %d" % (stateByte1, stateByte2))
