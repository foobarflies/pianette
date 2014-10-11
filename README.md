### Virtual & GPIO Game Console Controller
- - -

A graphical emulator of a Game Pad Controller that asynchronously listens to GPIO `EDGE_RISING` inputs from sensors and sends Serial commands to an ATMEGA328P acting as a fake SPI Slave for the Console.

> TODO :

  - Modify the Arduino sketch to have a better LEFT/RIGHT (keep the button pressed longer)
  - Acknowledge from Arduino to make sure the correct info is transmitted
  - Change the interface for something more lookalike to a real controller
  - In `rd.c` : load `main.pyw` on startup
