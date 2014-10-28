# Virtual & GPIO Game Console Controller

A command-line emulator of a Game Pad Controller that asynchronously listens to GPIO `EDGE_RISING` inputs from sensors and sends Serial commands to an `ATMEGA328P` acting as a fake SPI Slave for the Console.

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

### Disabling Serial port pins (UART)

In order to properly use pins `14`, `15`, and `18` that are used for `UART`, we must disable the boot up and diagnostic output to the serial port :

    sudo vi /boot/cmdline.txt

This :

    dwc_otg.lpm_enable=0 console=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait fbcon=map:10 4dpi.sclk=48000000 4dpi.compress=1

becomes :

    dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait fbcon=map:10 4dpi.sclk=48000000 4dpi.compress=1

Second, we need to disable the login prompt :

    sudo vi /etc/inittab

And comment out the last line :

    #Spawn a getty on Raspberry Pi serial line
    # T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100

Let's reboot and the serial port will now be free for our exclusive use. Note that Python will still issue a `RuntimeWarning` to indicate that you are overriding the pin's default state. This is ok, and taken into account in `GPIOController.py` anyway. 

>  Thanks to **Ted B Hale** for that : _http://raspberrypihobbyist.blogspot.fr/2012/08/raspberry-pi-serial-port.html_

### Update

To update the repository on a target Raspberry Pi, just run:

    ./update.sh

### Run

`sudo` is required to have access to GPIO pins on the Raspberry Pi.

In command line, run :

    sudo ./main-nogui.py

### Street Fighter Alpha 3 Specifics

#### Timing

Fighting buttons timings :

  - ✕ : 270 ms
  - □ : 200 ms
  - △ : 370 ms
  - ◯ : 400 ms

If two antinomic buttons are pressed at the same time, the following rules apply :

  - Up & Down => Up will be triggered
  - Right & Left => Left will be triggered

#### List of keys and combos

  - ✕ (Cross) : `0xFF 0xBF`
  - ◯ (Circle) : `0xFF 0xDF`
  - □ (Square) : `0xFF 0x7F`
  - △ (Triangle) : `0xFF 0xEF`

  - START : `xF7 0xFF`
  - SELECT : `xF7 0xFE`

  - ↑ : `0xEF 0xFF`
  - ↓ : `0xBF 0xFF`
  - ← : `0x7F 0xFF`
  - → : `0xDF 0xFF`

  - ↓ + → = ↘ : `0x9F 0xFF`
  - ↓ + ← = ↙ : `0x3F 0xFF`
  - ↑ + → = ↗  : `0xCF 0xFF`
  - ↑ + ← = ↖ : `0x6F 0xFF`

  - ↓, (↘|↙), (→|←) + □ (Hadouken) : _timed combo_
  - ↓, (↙|↘), (←|→) + ✕ (Tatsumaki) : _timed combo_
