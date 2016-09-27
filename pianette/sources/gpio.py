# coding: utf-8

import pianette.errors
import re
import time
import warnings

from pianette.utils import Debug

import RPi.GPIO

RPi.GPIO.setwarnings(True)
RPi.GPIO.cleanup()

class GPIOConfigUtil:

    # Channels

    CHANNEL_LABELING_BCM = "BCM"

    supported_channel_labelings = [ CHANNEL_LABELING_BCM ]

    @staticmethod
    def is_supported_channel_labeling(channel_labeling):
        return channel_labeling in GPIOConfigUtil.supported_channel_labelings

    rpi_gpio_mode_for_channel_labeling = {
        CHANNEL_LABELING_BCM: RPi.GPIO.BCM,
    }

    @staticmethod
    def get_rpi_gpio_mode_for_channel_labeling(channel_labeling):
        if not GPIOConfigUtil.is_supported_channel_labeling(channel_labeling):
            raise PianetteGPIOConfigError("Unsupported GPIO channel labeling '%s'" % (channel_labeling))

        if channel_labeling not in GPIOConfigUtil.rpi_gpio_mode_for_channel_labeling.keys():
            raise PianetteGPIOConfigError("Undefined GPIO mode for channel labeling '%s'" % (channel_labeling))

        return GPIOConfigUtil.rpi_gpio_mode_for_channel_labeling.get(channel_labeling, None)

    @staticmethod
    def get_rpi_gpio_channel(channel, channel_labeling):
        if not GPIOConfigUtil.is_supported_channel_labeling(channel_labeling):
            raise PianetteGPIOConfigError("GPIO channel labeling '%s' is not supported" % (channel_labeling))

        rpi_gpio_channel = None

        if channel_labeling == GPIOConfigUtil.CHANNEL_LABELING_BCM:
            match = re.search('GPIO(?P<rpi_gpio_channel>\d+)', channel)
            if match:
                rpi_gpio_channel = int(match.group('rpi_gpio_channel'))

        if rpi_gpio_channel is None:
            raise PianetteConfigError("Undefined RPi.GPIO channel for channel '%s' using labeling '%s'" % (channel, channel_labeling))

        return rpi_gpio_channel

    # Resistors

    RESISTOR_PULL_DOWN = "pull-down"
    RESISTOR_PULL_UP = "pull-up"
    RESISTOR_NONE = "none"

    supported_resistors = [ RESISTOR_PULL_DOWN, RESISTOR_PULL_UP, RESISTOR_NONE ]

    @staticmethod
    def is_supported_resistor(resistor):
        return resistor in GPIOConfigUtil.supported_resistors

    rpi_gpio_pull_up_down_for_resistor = {
        RESISTOR_PULL_DOWN: RPi.GPIO.PUD_DOWN,
        RESISTOR_PULL_UP: RPi.GPIO.PUD_UP,
        RESISTOR_NONE: None,
    }

    @staticmethod
    def get_rpi_gpio_pull_up_down_for_resistor(resistor):
        if not GPIOConfigUtil.is_supported_resistor(resistor):
            raise PianetteGPIOConfigError("Unsupported GPIO resistor '%s'" % (resistor))

        if resistor not in GPIOConfigUtil.rpi_gpio_pull_up_down_for_resistor.keys():
            raise PianetteGPIOConfigError("Undefined GPIO pull-up-down for resistor '%s'" % (resistor))

        return GPIOConfigUtil.rpi_gpio_pull_up_down_for_resistor.get(resistor, None)

    # Events

    EVENT_FALLING = "Falling"
    EVENT_RISING = "Rising"

    supported_events = [ EVENT_FALLING, EVENT_RISING ]

    @staticmethod
    def is_supported_event(event):
        return event in GPIOConfigUtil.supported_events

    rpi_gpio_event_for_event = {
        EVENT_FALLING: RPi.GPIO.FALLING,
        EVENT_RISING: RPi.GPIO.RISING,
    }

    @staticmethod
    def get_rpi_gpio_event_for_event(event):
        if not GPIOConfigUtil.is_supported_event(event):
            raise PianetteGPIOConfigError("Unsupported GPIO event '%s'" % (event))

        if event not in GPIOConfigUtil.rpi_gpio_event_for_event.keys():
            raise PianetteGPIOConfigError("Undefined GPIO event for event '%s'" % (event))

        return GPIOConfigUtil.rpi_gpio_event_for_event.get(event, None)

    # Polling

    POLLING_STATUS_HIGH = "High"
    POLLING_STATUS_LOW = "Low"

    supported_polling_statuses = [ POLLING_STATUS_HIGH, POLLING_STATUS_LOW ]

    @staticmethod
    def is_supported_polling_status(polling_status):
        return polling_status in GPIOConfigUtil.supported_polling_statuses

    rpi_gpio_input_for_polling_status = {
        POLLING_STATUS_HIGH: RPi.GPIO.HIGH,
        POLLING_STATUS_LOW: RPi.GPIO.LOW,
    }

    @staticmethod
    def get_rpi_gpio_input_for_polling_status(polling_status):
        if not GPIOConfigUtil.is_supported_polling_status(polling_status):
            raise PianetteGPIOConfigError("Unsupported GPIO polling status '%s'" % (polling_status))

        if polling_status not in GPIOConfigUtil.rpi_gpio_input_for_polling_status.keys():
            raise PianetteGPIOConfigError("Undefined GPIO input for polling status '%s'" % (polling_status))

        return GPIOConfigUtil.rpi_gpio_input_for_polling_status.get(polling_status, None)

    POLLING_EVENT_FALLING = "Falling"
    POLLING_EVENT_RISING = "Rising"

    supported_polling_events = [ POLLING_EVENT_FALLING, POLLING_EVENT_RISING ]

    @staticmethod
    def is_supported_polling_event(polling_event):
        return polling_event in GPIOConfigUtil.supported_polling_events

    polling_events = {
        POLLING_EVENT_FALLING: {
          'from': rpi_gpio_input_for_polling_status[POLLING_STATUS_HIGH],
          'to': rpi_gpio_input_for_polling_status[POLLING_STATUS_LOW]
        },
        POLLING_EVENT_RISING: {
          'from': rpi_gpio_input_for_polling_status[POLLING_STATUS_LOW],
          'to': rpi_gpio_input_for_polling_status[POLLING_STATUS_HIGH]
        }
    }

    @staticmethod
    def get_matching_polling_event(from_status, to_status):
        matching_polling_events = [ polling_event
                                    for polling_event in GPIOConfigUtil.polling_events.keys()
                                    if GPIOConfigUtil.polling_events.get(polling_event).get('from') == from_status
                                    and GPIOConfigUtil.polling_events.get(polling_event).get('to') == to_status
                                  ]
        if not matching_polling_events:
            return None
        return matching_polling_events.pop(0)

class gpio:
    def __init_using_configobj(self, configobj=None):
        self.configobj = configobj

        if not configobj:
            raise PianetteConfigError("Undefined configobj")

        # Global
        gpio_configobj = configobj.get("GPIO")
        if not gpio_configobj:
            raise PianetteConfigError("Undefined GPIO section in configobj")

        # Without a channel labeling, we can't configure anything else, so we're done
        channel_labeling = gpio_configobj.get("channel-labeling")
        if not channel_labeling:
            Debug.println("NOTICE", "GPIO Channel Labeling not defined, skipping configobj" % (channel))
            return

        RPi.GPIO.setmode(GPIOConfigUtil.get_rpi_gpio_mode_for_channel_labeling(channel_labeling))
        Debug.println("NOTICE", "GPIO Channel Labeling set to '%s'" % (channel_labeling))

        # Input
        gpio_input_configobj = gpio_configobj.get("Input")
        if gpio_input_configobj:
            # It's okay to ignore "already in use" warnings for the following channels
            runtime_warning_safe_rpi_gpio_channels = [ GPIOConfigUtil.get_rpi_gpio_channel(channel, channel_labeling) for channel in gpio_input_configobj.get("runtime-warning-safe-channels", []) ]

            default_gpio_pull_up_down = None
            if gpio_input_configobj.get("default-resistor", None) is not None:
                default_gpio_pull_up_down = GPIOConfigUtil.get_rpi_gpio_pull_up_down_for_resistor(gpio_input_configobj.get("default-resistor"))

            gpio_input_supported_channels = gpio_input_configobj.get("supported-channels")
            for channel in gpio_input_supported_channels:
                rpi_gpio_channel = GPIOConfigUtil.get_rpi_gpio_channel(channel, channel_labeling)
                rpi_gpio_pull_up_down = default_gpio_pull_up_down

                if gpio_input_configobj.get("Resistors", None is not None) and gpio_input_configobj.get("Resistors").get(channel, None) is not None:
                    rpi_gpio_pull_up_down = GPIOConfigUtil.get_rpi_gpio_pull_up_down_for_resistor(gpio_input_configobj.get("Resistors").get(channel))

                gpio_setup_kargs = {}
                if rpi_gpio_pull_up_down is not None:
                    gpio_setup_kargs["pull_up_down"] = rpi_gpio_pull_up_down

                # We want to be able to catch warnings, expecially the RuntimeWarning when a channel is already in use
                warnings.filterwarnings('error', category=RuntimeWarning)
                try:
                    # Attempt to set channel as Input
                    RPi.GPIO.setup(rpi_gpio_channel, RPi.GPIO.IN, **gpio_setup_kargs)
                    # Allow potential RuntimeWarning to be thrown while within the try statement
                    time.sleep(0.025)

                except ValueError:
                    Debug.println("FAIL", "GPIO Channel '%s' is not supported" % (channel))
                    raise
                except RuntimeWarning:
                    if rpi_gpio_channel in runtime_warning_safe_rpi_gpio_channels:
                        Debug.println("WARNING", "GPIO Channel '%s' already in use" % (channel))
                    else:
                        Debug.println("FAIL", "GPIO Channel '%s' already in use" % (channel))
                        raise
                except:
                    raise
                finally:
                    warnings.filterwarnings('default', category=RuntimeWarning)

                # Verify that channel is indeed set as Input
                mode = RPi.GPIO.gpio_function(rpi_gpio_channel)
                if (mode != RPi.GPIO.IN):
                    Debug.println("FAIL", "GPIO Channel '%s' could not be set as Input" % (channel))
                    raise PianetteGPIOConfigError("GPIO Channel could not be set as Input")

                Debug.println("SUCCESS", "GPIO Channel '%s' set as Input" % (channel) )

            # Input events
            gpio_input_events_configobj = gpio_input_configobj.get("Events", {})

            for event in gpio_input_events_configobj.keys():
                rpi_gpio_event = GPIOConfigUtil.get_rpi_gpio_event_for_event(event)

                for channel, commands in gpio_input_events_configobj[event].items():
                    rpi_gpio_channel = GPIOConfigUtil.get_rpi_gpio_channel(channel, channel_labeling)

                    bouncetime = 250
                    if rpi_gpio_channel == 22:
                        bouncetime = 500 # HACK to prevent multiple play.reset events
                    RPi.GPIO.add_event_detect(rpi_gpio_channel, rpi_gpio_event, callback=self.define_command_callback(commands), bouncetime=bouncetime)

            # Polling
            self.polling_status_callbacks = {}
            self.polling_event_callbacks = {}
            self.last_polled_gpio_inputs = {}

            gpio_input_polling_configobj = gpio_input_configobj.get("Polling", {})

            gpio_input_polling_statuses_configobj = gpio_input_polling_configobj.get("Statuses", {})
            for polling_status in gpio_input_polling_statuses_configobj.keys():
                for channel, commands in gpio_input_polling_statuses_configobj[polling_status].items():
                    rpi_gpio_channel = GPIOConfigUtil.get_rpi_gpio_channel(channel, channel_labeling)
                    self.polling_status_callbacks[rpi_gpio_channel] = {
                        GPIOConfigUtil.get_rpi_gpio_input_for_polling_status(polling_status): self.define_command_callback(commands)
                    }
                    self.last_polled_gpio_inputs[rpi_gpio_channel] = None

            gpio_input_polling_events_configobj = gpio_input_polling_configobj.get("Events", {})
            for polling_event in gpio_input_polling_events_configobj.keys():
                for channel, commands in gpio_input_polling_events_configobj[polling_event].items():
                    rpi_gpio_channel = GPIOConfigUtil.get_rpi_gpio_channel(channel, channel_labeling)
                    self.polling_event_callbacks[rpi_gpio_channel] = {
                        polling_event: self.define_command_callback(commands)
                    }
                    self.last_polled_gpio_inputs[rpi_gpio_channel] = None

        # Output
        gpio_output_configobj = gpio_configobj.get("Output")
        if gpio_output_configobj:
            Debug.println("FAIL", "GPIO Channels could not be set as Output" % (channel))
            raise PianetteGPIOConfigError("GPIO Channels could not be set as Output")

    def __init__(self, configobj=None, pianette=None):
        self.__init_using_configobj(configobj=configobj)
        self.pianette = pianette

    def __del__(self):
        self.disable()

    def disable(self):
        # Cleanup GPIOs on object destruction
        RPi.GPIO.cleanup()

    # Callback method for Piano Notes
    def define_command_callback(self, commands):
        def command_callback(channel):
            self.pianette.inputcmds(commands, source="gpio")

        return command_callback

    def poll(self):
        channel_inputs = {}
        channels_with_events = []

        for channel in self.last_polled_gpio_inputs.keys():
            polled_gpio_input = RPi.GPIO.input(channel)
            channel_inputs[channel] = polled_gpio_input

            if self.last_polled_gpio_inputs[channel] is not None:
                matching_polling_event = GPIOConfigUtil.get_matching_polling_event(self.last_polled_gpio_inputs[channel], polled_gpio_input)
                if (matching_polling_event is not None
                    and channel in self.polling_event_callbacks
                    and matching_polling_event in self.polling_event_callbacks[channel]
                   ):
                    channels_with_events.append(channel)
                    Debug.println('INFO', 'Invoking polling event callback for channel %d, input %d, event %s' % (channel, polled_gpio_input, matching_polling_event))
                    self.polling_event_callbacks[channel][matching_polling_event](channel)

            self.last_polled_gpio_inputs[channel] = polled_gpio_input

            if (channel not in channels_with_events
                and channel in self.polling_status_callbacks
                and polled_gpio_input in self.polling_status_callbacks[channel]
               ):
                Debug.println('INFO', 'Invoking polling callback for channel %d, input %d' % (channel, polled_gpio_input))
                self.polling_status_callbacks[channel][polled_gpio_input](channel)
