# Pianette = Piano + Manette

A full-fledged retro-engineering of a Playstation 2 Game Pad Controller that asynchronously listens to commands from various sources (GPIO, API, etc ...) and sends Serial commands to an `ATMEGA328P` acting as a fake SPI Slave for the Console running any configured game.

_Written in Python_

You can find more info on [this article](http://www.foobarflies.io/pianette/) we wrote and on the corresponding [hacknernews discussion](https://news.ycombinator.com/item?id=9071205).

## Running Pianette

`sudo` is required to have access to GPIO pins on the **Raspberry Pi B+**.

In command line, run :

    sudo -i PYTHONIOENCODING="utf-8" ./main.py --enable-source gpio --enable-source api --select-game 'street-fighter-alpha-3' --select-player 1

> The initialisation process is quite verbose to display all warnings and errors encountered.

## Adding a new game

Games are actually Python _modules_ that are imported on-demand, with a specific configuration and directory structure.

All games reside in the `config/games` directory. The following structure must be respected :

```
config/
|-- games/
|   |-- name-of-the-game/
|   |   |-- __init__.py
|   |   |-- game.py
|   |   |-- general.ini
|   |   |-- player1.py
|   |   |-- player2.py
```

`__init__.py` must be present, but it's actually just an empty file. 

`game.py` defines custom functions that may be needed to play the game. It can be empty too. It must define functions in its global scope.

Any function defined in this file will be accessible in the `game` namespace :

```python
# file : game.py
# coding: utf-8
from pianette.utils import Debug
def my_function(*args, **kwargs):
  cmd = kwargs['cmd']
  game_configobj = kwargs['config']

  Debug.println("NOTICE", "Just playing a ✕")
  cmd.onecmd("console.play ✕")
```

This function can be called with `game.my-function optional-parameter`  or `game.my_function optional-parameter` (_we prefer and encourage the first version using hyphens_).

The config files (`.ini`) must define a couple of compulsory keys :

In `general.ini` :

```ini
[Game]

[[name-of-the-game]]

# Can be empty, but the key must be defined

[[[Mappings]]]

# Can be empty, but the key must be defined
```

In `player1.ini` and `player1.ini`:

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

## Pianette cycles

A cycle is a **single loop during which Pianette collects events from all its enabled sources to create a complete representation of a sequence of buttons that it then sends to the SPI port of the console**.

This sequence emulates a real console controller.

The timing of the sequence is fixed and has been configured to match the behavior of the console.

To replicate the "combo" functionality (i.e. playing a sequence of buttons in a deterministic order giving a result that is more interesting than the separate playing of each buttons in a row), the loop has a grace period (_configured as a number of Pianette cycles_) during which **Pianette** listens to other incoming events to decide if the current representation should wait on future events before being sent to the console.

## Available namespaces and commands

**Pianette** allows for different namespaces of commands to be used : `console`, `game`, `piano`, `pianette` and `time`.

### console

> NB : Some character replacements are available in this namespace for ease of use. Even if actual UTF-8 values are prefered when possible, you can use the replacement without affecting the functionality. 
> 
> ↑, ↓, ←, →, □, △, ✕ and ◯ can be replaced with UP, DOWN, LEFT, RIGHT, SQUARE, TRIANGLE, CROSS and CIRCLE respectively

### `console.hit`

Plays a controller button sequence for a single **Pianette** cycle.

**Example** :

    pianette: console.hit ✕ + □

**Note** : The `+` operator is used to create a synchronous sequence of buttons

### `console.play`

Plays a controller button sequence for a full **Pianette** cycle.

**Example** :

    pianette: console.play → + □

### `console.reset`

Sends the **RESET** combo to the console , that is `START + RESET`. In most cases, this will reset the game status in the console and come back to the main starting menu.

This method doesn't accept any arguments.

**Example** :

    pianette: console.reset

### pianette

### `pianette.enable-source`

Enables a configured source. Once enabled, **Pianette** can accept events from the source. Currently supported sources are `api` and `gpio`.

**Example** :

    pianette: pianette.enable-source gpio

### `pianette.disable-source`

Disables a previsouly enabled and configured source. Once enabled, **Pianette** cannot accept events from this source.

> An example use case is to disable the `gpio` source when running a script along side, so the user cannot disturb the script

### `pianette.select-game`

Selects an available game. If the module is not defined or the game not present, it will gracefully fails. If the module is present but that some configuration items are missing, an exception will be raised.

**Example** :

    pianette: pianette.select-game street-fighter-alpha-3

> You must give the exact module / folder name as an argument of this function

### `pianette.dump-state`

Dumps the full state of the configuration. This is mostly a debug function; it accepts no arguments.

**Example** :

    pianette: pianette.dump-state

### piano

> NB : Some character replacements are available in this namespace for ease of use. Even if actual UTF-8 values are prefered when possible, you can use the replacement without affecting the functionality. 
> 
> Specifically, ♯ and ♭ can be replaced with # and b.
> Chords aliases are also defined in the **[[Alias]]** configuration block in `piano.ini`.

### `piano.play`

Plays a chord, a pedal or a single note.

**Example** :

    pianette: piano.play C3 + E♭3 + G3

**Note** : As for the `console` namespace, the `+` operator is used to create a synchronous sequence of keys

### `piano.hold`

Holds a note, a pedal or a chord as long as `piano.release`  is not called on the same sequence. The notes will be then added to every cycle afterwards.

**Example** :

    pianette: piano.hold sostenato


### `piano.release`

Release a previously held note, pedal or chord.

**Example** :

    pianette: piano.release sostenato


> The hold and release methods are primarily used to take advantage of the pedals.

### game

This namespace is populated with the custom functions defined in `game.py` for each game module. Commands defined in the game's configuration files are also added to this namespace.

> If no game is selected, this namespace doesn't have any command available.

### time

This namespace only provides the `time.sleep {duration_in_seconds}` function that allows to pace the inputs as needed.

## The Pianette API

Pianette exposes an API

> The API is considered a source, so in order for it to work, you must enable it at launch or with the command `pianette.enable-source api`.

By default, the API base url is `http://127.0.0.1:5000/`. You can change the port in the configuration (`pianette.ini`).

### Endpoints

#### POST `/`

The endpoint is relatively simple and allows you to send any namespaced command as a POST parameter named `data`:

      curl -X POST -F 'data=console.play START + RESET' /

#### POST `/namespace/command`

This endpoint is a kind of alias for the first one. It allows you to limit the errors and send strongly-namespaced commands more easily.

      curl -X POST -F 'data=crash-nitro-kart' /pianette/select-game

### The web interface

The web interface relies on the API to work, and thus is only available when the API is enabled. It offers a backend to control pianette, as well as virtual controllers that can be used to play remotely on the console.

> In order for the web interface to work properly, the `[[Hosts]]` key of `pianette.ini` must be defined and the IP (or hostname) of the different pianette instances on the network must be set. If you only have one instance, you can define `player-1 = 127.0.0.1` only.

#### The virtual controller

The virtual controller is a #TODO

#### The admin backend

TODO


## Installation

### ATMEGA (Arduino)

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

### Installing needed pip packages

The necessary Python packages have been freezed, so you can install them easily with :

    pip install -r requirement.txt

And additionnally on the Pi :
    
    pip install -r requirement-rpi.txt

### Installing Pianette as a service

For ease of use, we provide a simple init script to start Pianette as a service on compatible systems :

    sudo service pianette start|stop|restart|status

See the `pianette_initd_script.sh` script, to put in `/etc/init.d/` or wherever seems adequate.

### Limitations

#### Python version

For [Flask](http://flask.pocoo.org/) to run correctly, we need **Python3.3.6**. It is recommended to use **pyenv** to use it, which can be installed via :

    curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

and then :

    pyenv install 3.3.6

## Team

  - **Coox** — [http://coox.org](http://coox.org)
  - **Tchap** — [http://tchap.me](http://tchap.me)

## License

**MIT**. See the [License file](https://github.com/tchapi/pianette/blob/master/LICENSE).
