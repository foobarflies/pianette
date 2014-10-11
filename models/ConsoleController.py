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
    logging.basicConfig(filename='/home/pi/Desktop/SNESTest/log/snesCommands.log', filemode='a', level=logging.INFO, format='%(asctime)s.%(msecs).03d : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    self.stateController = stateController

    GPIO.setup(ConsoleController.ATT_PIN, GPIO.IN)
    GPIO.setup(ConsoleController.CLK_PIN, GPIO.IN)
    GPIO.setup(ConsoleController.DATA_PIN, GPIO.OUT)
    GPIO.setup(ConsoleController.ACK_PIN, GPIO.OUT)

    # ATT will go low to get the attention of the controller
    GPIO.add_event_detect(ConsoleController.ATT_PIN, GPIO.FALLING, callback=self.sendState, bouncetime=300)

  def sendStateBit(self, channel):
    state_byte = self.state_as_bytes[self.state_as_bytes_txn_bytecount]
    state_bit = (state_byte >> self.state_as_bytes_txn_byte_bitcount) && 1

    GPIO.output(ConsoleController.DATA_PIN, state_bit)

    self.state_as_bytes_txn_byte_bitcount++
    if (self.state_as_bytes_txn_byte_bitcount == 8):
      self.state_as_bytes_txn_byte_bitcount = 0
      self.state_as_bytes_txn_bytecount++

      if (self.state_as_bytes_txn_bytecount > len(self.state_as_bytes)):
        # If end of sequence is reached, end transmission
        logging.info('state_as_bytes transmission completed!')

        # Clears all the sent button for next iteration
        self.stateController.clearFlags()

      else:
        # Otherwise, send 4µs ACK after 12µs
        usleep(12)
        GPIO.output(ConsoleController.ACK_PIN, 0)

        usleep(4)
        GPIO.output(ConsoleController.ACK_PIN, 1)

  def sendState(self, channel):
    print("Sending state :", self.stateController)
    logging.info(self.stateController)
    
    self.state_as_bytes = [ 0xFF, 0x41, 0x5A ] # Controller ID

    self.state_as_bytes.append( # Data byte 1
      (self.stateController.state["SELECT"] & 0b00000001) &
      (self.stateController.state["START"]  & 0b00001000) &
      (self.stateController.state["TOP"]    & 0b00010000) &
      (self.stateController.state["RIGHT"]  & 0b00100000) &
      (self.stateController.state["BOTTOM"] & 0b01000000) &
      (self.stateController.state["LEFT"]   & 0b10000000)
    )

    self.state_as_bytes.append( # Data byte 2
      (self.stateController.state["T"] & 0b00010000) &
      (self.stateController.state["O"] & 0b00100000) &
      (self.stateController.state["X"] & 0b01000000) &
      (self.stateController.state["S"] & 0b10000000)
    )

    self.state_as_bytes_txn_bytecount = 0
    self.state_as_bytes_txn_byte_bitcount = 0

    # BITBANG ALL THE SH*T !!!
    logging.info('state_as_bytes:' . self.state_as_bytes)
    logging.info('state_as_bytes transmission starting')

    GPIO.add_event_detect(ConsoleController.CLK_PIN, GPIO.FALLING, callback=self.sendStateBit)
