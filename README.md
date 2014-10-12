### Virtual & GPIO Game Console Controller
- - -

A graphical emulator of a Game Pad Controller that asynchronously listens to GPIO `EDGE_RISING` inputs from sensors and sends Serial commands to an ATMEGA328P acting as a fake SPI Slave for the Console.

Written in Python 3.

#### Blacklisting

In order for SPI and i2c pins to work, it is compulsory to blacklist all modules that might be using it :

in `/etc/modprobe.d/raspi-blacklist.conf` :

    blacklist spi-bcm2708
    blacklist i2c-bcm2708

    blacklist regmap-spi
    blacklist regmap-i2c

    blacklist snd-pcm
    blacklist snd-bcm2835
    blacklist snd-seq
    blacklist snd-timer
    blacklist snd-seq-device
    blacklist snd-soc-core
    blacklist snd-soc-pcm512x
    blacklist snd-soc-wm8804
    blacklist snd-soc-bcm2708-i2s

    blacklist leds-gpio

#### test.py

Test script to verify that all GPIOs can be accessed. Run with `sudo ./test.py` and trigger each pin to see if it calls back.


#### TODO 

  - Modify the Arduino sketch to have a better LEFT/RIGHT (keep the button pressed longer)
  - Acknowledge from Arduino to make sure the correct info is transmitted
  - Change the interface for something more lookalike to a real controller
  - In `rd.c` : load `main.pyw` on startup
