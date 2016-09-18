# Pianette = Piano + Manette

A command-line emulator of a Playstation 2 Game Pad Controller that asynchronously listens to GPIO `EDGE_RISING` inputs from sensors and sends Serial commands to an `ATMEGA328P` acting as a fake SPI Slave for the Console running Street Fighter Alpha 3.

_Written in Python 3.3.6_

You can find more info on [this article](http://www.foobarflies.io/pianette/) we wrote and on the corresponding [hacknernews discussion](https://news.ycombinator.com/item?id=9071205).

## Using Python 3.3.6

For Flask to run correclty, we need Python3.3.6. It is recommended to use **pyenv** to use it, which can be installed via :

    curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

then :

    pyenv install 3.3.6

## Run

`sudo` is required to have access to GPIO pins on the **Raspberry Pi B+**.

In command line, run :

    sudo ./main.py

> The initialisation process is quite verbose to display all warnings and errors encountered.

## Adding a new game

Games are actually Python _modules_ that are imported on-demand, with a specific configuration and directory structure.

All games reside in the `config/games` directory. The following structure must be respected :

```
config/
|-- games/
|   |-- this-fantastic-game/
|   |   |-- __init__.py
|   |   |-- game.py
|   |   |-- general.ini
|   |   |-- player1.py
|   |   |-- player2.py
```

`__init__.py` must be present, but it's actually just an empty file. 

`game.py` defines custom functions that may be needed to play the game. It can be empty too. It must define functions in its global scope.

Any function defined in this file will be accessible in the `game` namespace :

```
# file : game.py
# coding: utf-8
from pianette.utils import Debug
def my_function(*args, **kwargs):
  cmd = kwargs['cmd']
  game_configobj = kwargs['config']

  Debug.println("NOTICE", "Just playing a ✕")
  cmd.onecmd("console.play ✕")
```

This function can be called with `game.my-function optional-parameter`  or `fame.my_function optional-parameter` (we prefer and encourage the first version using hyphens).

The config files (`.ini`) must define a couple of compulsory keys :

In `general.ini` :

```ini
[Game]

[[name-of-the-game]]

# Can be empty, but the key must be defined

[[[Mappings]]]

# Can be empty, but the key must be defined
```

In `player1.ini` and `player1.ini`2:

```ini
[Game]

[[name-of-the-game]]

[[[Commands]]]

# Can be empty, but the key must be defined

[[[Player 1]]]

[[[[Mappings]]]]

# Can be empty, but the key must be defined
```

> `name-of-the-game` must be the exact name of the module folder.

With this structure, you are able to select your game with `--select-game name-of-the-game`. And with the console :

    pianette: pianette.select-game name-of-the-game

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

    # Spawn a getty on Raspberry Pi serial line
    # T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100

Let's reboot and the serial port will now be free for our exclusive use. Note that Python will still issue a `RuntimeWarning` to indicate that you are overriding the pin's default state. This is ok, and taken into account in `GPIOController.py` anyway. 

>  Thanks to **Ted B Hale** for that : _http://raspberrypihobbyist.blogspot.fr/2012/08/raspberry-pi-serial-port.html_

### Reset GPIO state on reboot

To reset all gpio states on boot to limit electric pressure on the bus, add the following cron to the `root` crontab (`sudo crontab -e`) :

    @reboot sudo /home/pi/pianette/reset_GPIO_on_reboot.py

### Team

  - Coox — [http://coox.org](http://coox.org)
  - Tchap — [http://tchap.me](http://tchap.me)

### License

MIT. See License file.
