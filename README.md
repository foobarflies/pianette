# Virtual & GPIO Game Console Controller

A graphical emulator of a Game Pad Controller that asynchronously listens to GPIO `EDGE_RISING` inputs from sensors and sends Serial commands to an `ATMEGA328P` acting as a fake SPI Slave for the Console.

_Written in Python 3._

## Installation

### ATMEGA

The `ArduinoSPISlave.ino` sketch must be loaded onto the Arduino, connected via serial. The port is of no consequence as the program will poll the open `/dev/ttyACM*`ports and choose the first one available.

### Blacklisting

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

And to remove modules at boot time in `/etc/modules`, especially sound-related modules.

### Run

`sudo`is required to have access to GPIO pins on the Raspberry Pi.

In command line, run :

    sudo ./main-nogui.py

If you have a graphical environment, you can run:

    sudo ./main.py

> NB : if you are running an X server over an SSH connection, you must first copy your `.Xauthority` file to root's home :

    sudo cp ~/.Xauthority /root/home/.


### Test Script

A test script is available to verify that all GPIOs can be accessed. Run with `sudo ./testGPIO.py` and trigger each pin to see if it calls back.

### Street Fighter Alpha 3 Specifics

#### Timing

Fighting buttons timings :

  - ☓ : 270 ms
  - ◼ : 200 ms
  - ▲ : 370 ms
  - ◯ : 400 ms

If two antinomic buttons are pressed at the same time, the following rules apply :

  - Up & Down => Up will be triggered
  - Right & Left => Left will be triggered

#### List of keys and combos

  - ☓ (Cross) : `0xFF 0xBF`
  - ◯ (Circle) : `0xFF 0xDF`
  - ◼ (Square) : `0xFF 0x7F`
  - ▲ (Triangle) : `0xFF 0xEF`

  - START : `xF7 0xFF`
  - SELECT : `xF7 0xFE`

  - ▲ : `0xEF 0xFF`
  - ▼ : `0xBF 0xFF`
  - ◀ : `0x7F 0xFF`
  - ▶ : `0xDF 0xFF`

  - ▼ + ▶ = ◢ : `0x9F 0xFF`
  - ▼ + ◀ = ◣ : `0x3F 0xFF`
  - ▲ + ▶ = ◥  : `0xCF 0xFF`
  - ▲ + ◀ = ◤ : `0x6F 0xFF`

  - ▼ + (▶|◀) + ◼ (Hadouken) : _timed combo_
  - ▼ + (▶|◀) + ☓ (Tatsumaki) : _timed combo_
