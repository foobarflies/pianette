import RPi.GPIO as GPIO
import logging
import time

usleep = lambda x: time.sleep(x/1000000.0)

class ConsoleController:

  # Declare pins for console dialog
  ATT_PIN = 8 # PSX Controller Yellow
  DATA_PIN = 9 # PSX Controller Brown
  CMD_PIN = 10 # PSX Controller Orange
  CLK_PIN = 11 # PSX Controller Blue
  ACK_PIN = 25 # PSX Controller Green

  # DATA : Signal from Controller to PSX.
  # This signal is an 8 bit serial transmission synchronous to the falling edge of clock (That is both the incoming and outgoing signals change on a high to low transition of clock. All the reading of signals is done on the leading edge to allow settling time.)
  
  # COMMAND : Signal from PSX to Controller.
  # This signal is the counter part of DATA. It is again an 8 bit serial transmission on the falling edge of clock.
  
  # VCC : VCC can vary from 5V down to 3V and the official SONY Controllers will still operate. The controllers outlined here really want 5V.
  # The main board in the PSX also has a surface mount 750mA fuse that will blow if you try to draw to much current through the plug (750mA is for both left, right and memory cards).
  
  # ATT : ATT is used to get the attention of the controller.
  # This signal will go low for the duration of a transmission. I have also seen this pin called Select, DTR and Command.

  # CLOCK : Signal from PSX to Controller.
  # Used to keep units in sync.

  # ACK : Acknowledge signal from Controller to PSX.
  # This signal should go low for at least one clock period after each 8 bits are sent and ATT is still held low. If the ACK signal does not go low within about 60 us the PSX will then start interogating other devices.
  # It should also be noted that this is a bus of sorts. This means that the wires are all tied together (except select which is seperate for each device). For the CLK, ATT, and CMD pins this does not matter as the PSX is always the originator. The DATA and ACK pins however can be driven from any one of four devices. To avoid contentions on these lines they are open collectors and can only be driven low.

  def __init__(self, stateController):
    logging.basicConfig(filename='/home/pi/Desktop/VirtualManette/log/commands.log', filemode='a', level=logging.INFO, format='%(asctime)s.%(msecs).03d : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    self.stateController = stateController

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(self.ATT_PIN, GPIO.IN)
    GPIO.setup(self.CLK_PIN, GPIO.IN)
    GPIO.setup(self.DATA_PIN, GPIO.OUT)
    GPIO.setup(self.ACK_PIN, GPIO.OUT)

    self.state_as_bytes_txn = False
    GPIO.add_event_detect(self.CLK_PIN, GPIO.FALLING, callback=self.sendStateBit)

    # ATT will go low to get the attention of the controller
    GPIO.add_event_detect(self.ATT_PIN, GPIO.FALLING, callback=self.sendState)

  def sendStateBit(self, channel):

    if (self.state_as_bytes_txn == False):
      return

    state_byte = self.state_as_bytes[self.state_as_bytes_txn_bytecount]
    state_bit = (state_byte >> self.state_as_bytes_txn_byte_bitcount) & 1

    print(" Sending bit 0b%d, bitcount : %d, bytecount : %d" % (state_bit, self.state_as_bytes_txn_byte_bitcount, self.state_as_bytes_txn_bytecount))
    GPIO.output(self.DATA_PIN, state_bit)

    self.state_as_bytes_txn_byte_bitcount+= 1
    if (self.state_as_bytes_txn_byte_bitcount == 8):
      print(" bitcount == 8, bytecount : %d" % self.state_as_bytes_txn_bytecount)
      self.state_as_bytes_txn_byte_bitcount = 0
      self.state_as_bytes_txn_bytecount+= 1

      if (self.state_as_bytes_txn_bytecount >= len(self.state_as_bytes)):
        # If end of sequence is reached, end transmission
        print('state_as_bytes transmission completed!')

        # Clears the Clock Pin callback for next iteration
        self.state_as_bytes_txn = False

      else:
        # Otherwise, send 4µs ACK after 12µs
        usleep(12)
        GPIO.output(self.ACK_PIN, 0)

        usleep(4)
        GPIO.output(self.ACK_PIN, 1)

  def sendState(self, channel):
    if (self.state_as_bytes_txn == True):
     return

    print("Sending state :", self.stateController)
    logging.info(self.stateController)
    
    self.state_as_bytes = [ 0xFF, 0x41, 0x5A ] # Controller ID

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

    self.state_as_bytes_txn_bytecount = 0
    self.state_as_bytes_txn_byte_bitcount = 0

    # Clears all the sent button for next iteration
    self.stateController.clearFlags()

    # BITBANG ALL THE SH*T !!!
    print('state_as_bytes starting transmission : %s' % ','.join(map(str,self.state_as_bytes)))

    self.state_as_bytes_txn = True

