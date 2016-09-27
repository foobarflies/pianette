# coding=utf-8

from copy import deepcopy
from pianette.ConsoleController import ConsoleController
from pianette.ControllerState import ControllerState
from pianette.PianetteCmd import PianetteCmd
from pianette.errors import PianetteConfigError
from pianette.Piano import Piano
from pianette.utils import Debug

import sys
import importlib
import threading
import time
import random

# Pianette Configuration

# Period of I/O cycle, in seconds
PIANETTE_CYCLE_PERIOD = 15/1000 # Seems to properly operate between 7 msecs and 26 msecs (PSX observation)

# Number of cycles before Inputs are processed and sent to Output
PIANETTE_PROCESSING_CYCLES = 2

# Number of cycles for the duration of a single console.play
PIANETTE_CONSOLE_PLAY_DURATION_CYCLES = 3

class Pianette:
    def get_notes_chord_bitid(self, notes):
        notes_bitids = []
        for note in notes:
            if note in self._note_bitids:
                notes_bitids.append(self._note_bitids[note])

        notes_chord_bitid = 0b0
        for bitid in notes_bitids:
            notes_chord_bitid |= bitid
        return notes_chord_bitid

    def get_ranked_chord_bitids_including_at_least_one_of_notes(self, notes, from_chord_bitids_pool = None):
        if from_chord_bitids_pool is None:
            from_chord_bitids_pool = self._ranked_chord_bitids
        notes_chord_bitid = self.get_notes_chord_bitid(notes)

        ranked_notes_chord_bitids = []
        for chord_bitid in from_chord_bitids_pool:
            if (chord_bitid & notes_chord_bitid):
                ranked_notes_chord_bitids.append(chord_bitid)

        return ranked_notes_chord_bitids

    def __init_using_configobj(self, configobj=None):
        self.configobj = configobj

        if not configobj:
            raise PianetteConfigError("Undefined configobj")

        # Global
        pianette_configobj = configobj.get("Pianette")
        if not pianette_configobj:
            raise PianetteConfigError("Undefined Pianette section in configobj")

        # Mappings: Piano Notes (input) => PSX Controller Combo (output)
        pianette_mappings_configobj = pianette_configobj.get("Mappings")
        if not pianette_configobj:
            raise PianetteConfigError("Undefined Mappings section in Pianette configobj")

        self.init_mappings(pianette_mappings_configobj)

    def init_mappings(self, mappings):
        self.pianette_buffered_states_mappings = []

        for piano_args_string, controls_string in mappings.items():
            if not isinstance(controls_string, str):
                # Not a string, probably a configuration sub-section
                pass
            else:
                # Assume that some arguments in piano and console commands include aliases for longer-to type arguments
                unpacked_piano_args_string = PianetteCmd.unpack_piano_args_string(piano_args_string)
                controls_string = PianetteCmd.unpack_console_args_string(controls_string)

                piano_args = unpacked_piano_args_string.replace("+", " ").split()
                piano_notes = [ piano_arg for piano_arg in piano_args if piano_arg in self.piano.get_supported_notes()]
                piano_pedals = [ piano_arg for piano_arg in piano_args if piano_arg in self.piano.get_supported_pedals()]
                if len(piano_pedals) > 1:
                    raise PianetteConfigError("Mapping '%s' includes more than one pedal, this is currently unsupported" % (piano_args_string))
                if len(piano_notes) > 0 and len(piano_pedals) > 0:
                    raise PianetteConfigError("Mapping '%s' includes mixes notes and pedal, this is currently unsupported" % (piano_args_string))

                duration_cycles = None
                if piano_pedals:
                    if len(controls_string.split()) > 1:
                        raise PianetteConfigError("Mapping '%s' includes more than one buffered command, this is currently unsupported for pedals" % (controls_string))
                    duration_cycles = 1

                self.pianette_buffered_states_mappings.append({
                    "piano_notes": piano_notes,
                    "piano_pedal": (piano_pedals[:1] or [None])[0], # First item or None
                    "psx_controller": self.get_buffered_states_for_controls_string(controls_string, duration_cycles)
                })

        # Assign a unique, combinable bitid to configured notes and pedals
        self._note_bitids = {}
        _current_note_bitid = 0b1
        for buffered_state_mapping in self.pianette_buffered_states_mappings:
            for note in buffered_state_mapping["piano_notes"]:
                if not note in self._note_bitids:
                    self._note_bitids[note] = _current_note_bitid
                    _current_note_bitid <<= 1

        self._pedal_bitids = {}
        _current_pedal_bitid = _current_note_bitid
        for buffered_state_mapping in self.pianette_buffered_states_mappings:
            if buffered_state_mapping["piano_pedal"] is not None:
                self._pedal_bitids[buffered_state_mapping["piano_pedal"]] = _current_pedal_bitid
                _current_pedal_bitid <<= 1

        # Structure Buffered States Mapping using Piano "Chords" bitids (combination of Note bitids)
        # Rank chords as follows:
        #   1- chords with more notes have a higher priority
        #   2- for an equal number of notes, chords declared first in config have a higher priority
        _ranked_chord_bitids_for_note_count = {}

        self._buffered_states_mapping_for_chord_bitid = {}
        for buffered_state_mapping in self.pianette_buffered_states_mappings:
            chord_bitid = 0b0
            note_count = len(buffered_state_mapping["piano_notes"])

            for note in buffered_state_mapping["piano_notes"]:
                chord_bitid |= self._note_bitids[note]

            self._buffered_states_mapping_for_chord_bitid[chord_bitid] = buffered_state_mapping
            chord_bitids = _ranked_chord_bitids_for_note_count.get(note_count, [])
            chord_bitids.append(chord_bitid)
            _ranked_chord_bitids_for_note_count[note_count] = chord_bitids

        self._ranked_chord_bitids = []
        for note_count in sorted(list(_ranked_chord_bitids_for_note_count.keys()), reverse = True):
            self._ranked_chord_bitids.extend(_ranked_chord_bitids_for_note_count[note_count])

        # Structure Buffered States Mapping using Pedal bitids
        self._buffered_states_mapping_for_pedal_bitid = {}
        for buffered_state_mapping in self.pianette_buffered_states_mappings:
            if buffered_state_mapping["piano_pedal"] is not None:
                self._buffered_states_mapping_for_pedal_bitid[self._pedal_bitids[buffered_state_mapping["piano_pedal"]]] = buffered_state_mapping

    def __init__(self, configobj=None):
        self.__init_using_configobj(configobj=configobj)

        self.piano = Piano(configobj=self.configobj)
        self.psx_controller_state = ControllerState(configobj=self.configobj)

        self.sources = {}

        self.selected_game = None

        # Instantiate the console controller that is responsible for sendint out the psx constroller state to the console
        self.console_controller = ConsoleController(self.psx_controller_state, configobj=self.configobj)

        # Upcoming state cycles for the Piano Notes (input)
        self.piano_buffered_note_states = { note: [] for note in self.piano.get_supported_notes() }

        # Upcoming state cycles for the Piano Pedals (input)
        self.piano_buffered_pedal_states = { pedal: [] for pedal in self.piano.get_supported_pedals() }

        # Upcoming state cycles for the Console Controls (output)
        self.psx_controller_buffered_states = {}
        try:
            self.psx_controller_buffered_states = { k: [] for k in self.configobj['Console']['supported-controls'] }
        except KeyError:
            pass

        # Run the Pianette!
        self._timer = None
        self._timer_interval = PIANETTE_CYCLE_PERIOD
        self._timer_is_running = False

        # Start the timer thread that will cycle buffered states at each interval
        self.start_timer()
        Debug.println("INFO", "Pianette buffered states timer thread started at %f secs interval" % self._timer_interval)

        # Create pianette command interface
        self.cmd = PianetteCmd(configobj=configobj, pianette=self)

    def __del__(self):
        if hasattr(self, '_timer'):
            self.stop_timer()

    def inputcmds(self, commands, source=None):
        if source is not None and self.is_source_enabled(source):
            Debug.println("INFO", "Running commands from source '%s'" % (source))
            for command in commands.split("\n"):
                if command.strip():
                    self.cmd.onecmd(command)
                    time.sleep(0.25)
        else:
            Debug.println("WARNING", "Ignoring commands from source '%s'" % (source))

    def is_source_enabled(self, source):
        if (source in self.sources.keys()
            and 'enabled' in self.sources[source]
            and self.sources[source]['enabled'] is True):
            return True
        return False

    def get_source_instance(self, source):
        return self.sources[source]['instance']
    
    def enable_source(self, source):
        Debug.println("INFO", "Enabling Source '%s'" % (source))
        if source in self.sources and self.sources[source]['instance'] is not None:
            self.sources[source]['enabled'] = True
        else:
            raise PianetteConfigError("Source '%s' is not loaded yet" % (source))

    def disable_source(self, source):
        Debug.println("INFO", "Disabling Source '%s'" % (source))
        if source in self.sources:
            self.sources[source]['enabled'] = False
        else:
            raise PianetteConfigError("Source '%s' is not loaded yet" % (source))

    def load_source(self, source):
        if source in self.sources and 'instance' in self.sources[source]:
            Debug.println("WARNING", "Source '%s' is already enabled" % (source))
            return

        try:
            source_module = importlib.import_module('pianette.sources.' + source)
        except ImportError:
            Debug.println("FAIL", "Unsupported source '%s'" % (source))
            return
        source_class = getattr(source_module, source)
        instance = source_class(configobj=self.configobj, pianette=self)

        Debug.println("INFO", "Loading Source '%s'" % (source))
        self.sources[source] = {
            'enabled': True,
            'instance': instance,
        }

    def unload_source(self, source):
        Debug.println("INFO", "Unloading Source '%s'" % (source))
        # Gives a chance for the source to disable itself
        if source in self.sources and 'instance' in self.sources[source]:
            try:
                self.sources[source]['instance'].disable()
            except AttributeError:
                pass
        self.sources[source] = {
            'enabled': False,
        }

    def poll_enabled_sources(self):
        for source in self.sources.keys():
            if self.is_source_enabled(source):
                instance = self.get_source_instance(source)
                try:
                    instance.poll()
                except AttributeError:
                    pass

    def select_game(self, game=None):
        if game is None:
            return self.unselect_game()
        Debug.println("INFO", "Selecting Game '%s'" % (game))
        module_name = "config.games.%s.game" % game

        # Let's import the game module, if not previously done
        if module_name not in sys.modules:
            try:
                self.selected_game_module = importlib.import_module(module_name)
            except ImportError:
                Debug.println("FAIL", "Game '%s' doesn't have a module in the games folder" % game)
                return
        else:
            self.selected_game_module = sys.modules[module_name]
        self.selected_game = game
        
        # We have to re-init with the game's mappings
        # instead of the general mappings :
        if not self.configobj.get("Game").get(game):
            raise PianetteConfigError("Undefined Game '%s' section in configobj" % game)
        if not self.selected_player:
            raise PianetteConfigError("You must select a player first")

        self.selected_game_config = self.configobj.get("Game").get(game)
        self.selected_player_config = self.selected_game_config.get("Player %s" % self.selected_player)

        # Retrieve the mappings
        game_mappings = self.selected_game_config.get("Mappings")
        player_mappings = self.selected_player_config.get("Mappings")

        # Merge the two dictionaries of keys
        if player_mappings is not None:
            full_mappings = dict(game_mappings, **player_mappings);
        else:
            full_mappings = game_mappings

        # Finally, override PIANETTE_CYCLE_PERIOD
        global PIANETTE_CYCLE_PERIOD
        if self.selected_game_config.get('cycle-period') is not None:
            PIANETTE_CYCLE_PERIOD = float(self.selected_game_config.get('cycle-period'))
            Debug.println("NOTICE", "The selected game overrides the cycle period : %f seconds" % PIANETTE_CYCLE_PERIOD)
        else:
            PIANETTE_CYCLE_PERIOD = float(self.configobj.get("Console").get('default-cycle-period'))
            Debug.println("NOTICE", "Resetting the default cycle period : %f seconds" % PIANETTE_CYCLE_PERIOD)

        # Re-init the mappings
        self.init_mappings(full_mappings)

    def unselect_game(self):
        Debug.println("INFO", "Unselecting Game")
        self.selected_game_module = None
        self.selected_game = None
        self.selected_game_config = None
        self.selected_player_config = None

    def get_selected_game_module(self):
        return self.selected_game_module

    def get_selected_game(self):
        return self.selected_game

    def get_selected_player(self):
        return self.selected_player

    def get_selected_game_config(self):
        return self.selected_game_config

    def get_selected_player_config(self):
        return self.selected_player_config

    def select_player(self, player=None):
        Debug.println("INFO", "Selecting Player %s" % (player))
        self.selected_player = player

    def get_buffered_states_mappings(self):
        return self.pianette_buffered_states_mappings

    def extract(self, controls_string, combo_controls, force_duration_cycles):
        if (force_duration_cycles is None):
            force_duration_cycles = PIANETTE_CONSOLE_PLAY_DURATION_CYCLES

        # Grammar:
        # `x|y` selects randomly one of the control. If used in a combo, it will not select 
        #     the same control twice, thus `x|y + x|z` will never return `x` for both disjunctions
        #     Nevertheless, `x|y + y` might return `x + y` or simply `y`, since extract cannot go
        #     backwards in a combo. `x + x|y` will always return `x + y`.
        # `x{100}` outputs `x` for 100 cycles
        #
        # Priority:
        # The combo operator is **always** evaluated last.
        # The `{}` operator has precedence and thus will be evaluated _after_ `|`.

        if '|' in controls_string:
            choices = list(set(controls_string.split('|')) - set(combo_controls))
            control = random.choice(choices)
        else:
            control = controls_string

        if '{' in control:
            [c, d_temp] = control.split('{')
            if (d_temp):
                [d, temp] = d_temp.split('}')
                return (c, int(d))

        return (control, force_duration_cycles)

    def get_buffered_states_for_controls_string(self, controls_string, force_duration_cycles = None):
        # Initial state and time
        controls_buffered_states = {}
        time_index = 0

        # Combo loop variables
        in_combo = False
        combo_controls = []
        previous_control = None

        # By default, no duration cycle is set to detect malformed controls_string starting with `+`
        duration_cycles = None

        for control in controls_string.split():
            # '+' should not be at the start of the string, fail gracefully
            if control == "+" and duration_cycles is None:
                Debug.println("FAIL", "Control string is not grammatically correct (starting with a +)")
                return controls_buffered_states
            elif control == "+":
                time_index -= duration_cycles
                in_combo = True
            elif control == ";" and in_combo == False: # During a combo, a semi-colon (;) is not grammatically correct.
                # We add a "0" cycle count for every possible state, to be sure 
                # that it will add an offset even for future added controls
                # that are not yet present in self.controls_buffered_states
                for c in self.psx_controller_buffered_states:
                    if c in controls_buffered_states:
                        controls_buffered_states[c].extend([0] * PIANETTE_CONSOLE_PLAY_DURATION_CYCLES)
                    else:
                        controls_buffered_states[c] = [0] * PIANETTE_CONSOLE_PLAY_DURATION_CYCLES
            else:
                if in_combo:
                    combo_controls.append(previous_control) # Next control will be in a combo
                else:
                    combo_controls = []
                control, duration_cycles = self.extract(control, combo_controls, force_duration_cycles)
                
                if control in controls_buffered_states:
                    buffer_duration = 0
                    for duration in controls_buffered_states[control]:
                        buffer_duration += abs(duration)

                    if time_index - buffer_duration > 0:
                        controls_buffered_states[control].append(-time_index + buffer_duration)
                        controls_buffered_states[control].append(duration_cycles)
                    elif not in_combo or time_index == buffer_duration:
                        controls_buffered_states[control].append(duration_cycles)

                # If we've got an unknown control, it will be ignored and the string will
                # be parsed as if the control was not there, still modifying the time index
                # if needed and not breaking combos, leading to generally correct and expected
                # results. No exception should be raised.
                elif control in self.psx_controller_buffered_states:
                    controls_buffered_states[control] = []

                    if time_index > 0:
                        controls_buffered_states[control].append(-time_index)

                    controls_buffered_states[control].append(duration_cycles)

                time_index += duration_cycles
                in_combo = False # Always assume that we're the last control in the combo

                previous_control = control

        return controls_buffered_states

    def push_console_controls(self, controls_string, duration_cycles = None):
        controls_buffered_states = self.get_buffered_states_for_controls_string(controls_string, duration_cycles)

        for control, buffered_states in controls_buffered_states.items():
            self.psx_controller_buffered_states[control] = buffered_states

    def push_piano_notes(self, notes_string):
        for note in notes_string.replace("+", " ").split():
            self.piano.switch_note_on(note)

    def hold_piano_pedals(self, pedals_string):
        for pedal in pedals_string.replace("+", " ").split():
            self.piano.switch_pedal_on(pedal)

    def release_piano_pedals(self, pedals_string):
        for pedal in pedals_string.replace("+", " ").split():
            self.piano.switch_pedal_off(pedal)

    # Timer Methods

    def get_cycle_period(self):
        return PIANETTE_CYCLE_PERIOD

    def _run_timer(self):
        self._timer_is_running = False
        self.start_timer()
        self.cycle_buffered_states()

    def start_timer(self):
        if not self._timer_is_running:
            self._timer = threading.Timer(self._timer_interval, self._run_timer)
            self._timer.start()
            self.is_running = True

    def stop_timer(self):
        self._timer.cancel()
        self._timer_is_running = False

    def cycle_buffered_states(self):
        self.poll_enabled_sources()

        # Input Piano Notes to Piano Buffered States
        for piano_note in self.piano.get_supported_notes():
            if self.piano.is_note_on(piano_note):
                Debug.println("INFO", "Buffering Piano Note %s" % (piano_note))
                self.piano_buffered_note_states[piano_note].append({ "cycles_remaining": PIANETTE_PROCESSING_CYCLES })
                self.piano.switch_note_off(piano_note)

        # Input Piano Pedals to Piano Buffered States
        for piano_pedal in self.piano.get_supported_pedals():
            if self.piano.is_pedal_on(piano_pedal):
                if not self.piano_buffered_pedal_states[piano_pedal]:
                    Debug.println("INFO", "Indefinitely buffering Piano Pedal %s" % (piano_pedal))
                self.piano_buffered_pedal_states[piano_pedal] = [{ "cycles_remaining": "∞" }]
            else:
                if self.piano_buffered_pedal_states[piano_pedal]:
                    Debug.println("INFO", "Indefinitely unbuffering Piano Pedal %s" % (piano_pedal))
                self.piano_buffered_pedal_states[piano_pedal] = []

        # Process Buffered States: Determine piano note or chord
        # Notes that have reached their last cycle "lead" the chord determination
        # Other notes may be used to "complement" lead notes.
        # If a winning chord is found, push corresponding combo to PSX Controller buffer
        # If complementary notes are actually used, they are discarded from buffer.
        lead_notes = []
        complementary_notes = []
        for piano_note in self.piano_buffered_note_states.keys():
            processed_buffered_states = []
            for buffered_state in self.piano_buffered_note_states[piano_note]:
                if buffered_state["cycles_remaining"] == 0:
                    lead_notes.append(piano_note)
                else:
                    complementary_notes.append(piano_note)
                    buffered_state["cycles_remaining"] -= 1
                    processed_buffered_states.append(buffered_state)
            self.piano_buffered_note_states[piano_note] = processed_buffered_states

        if lead_notes:
            Debug.println("INFO", "Processing Piano Notes: lead=%s, complementary=%s" % (lead_notes, complementary_notes))
            ranked_chord_bitids = self.get_ranked_chord_bitids_including_at_least_one_of_notes(lead_notes)

            all_notes_chord_bitid = self.get_notes_chord_bitid(lead_notes + complementary_notes)
            ranked_winning_chord_bitids = [chord_bitid for chord_bitid in ranked_chord_bitids if not ((all_notes_chord_bitid & chord_bitid) ^ chord_bitid)]

            if ranked_winning_chord_bitids:
                winning_chord_bitid = ranked_winning_chord_bitids[0]
                winning_states_mapping = deepcopy(self._buffered_states_mapping_for_chord_bitid[winning_chord_bitid])

                # Push piano command to PSX Controller buffer, clearing any pending combo
                for control in self.psx_controller_buffered_states.keys():
                    self.psx_controller_buffered_states[control] = winning_states_mapping["psx_controller"].get(control, [])

                # Clear winning chord notes from the piano buffer
                for piano_note in self.piano_buffered_note_states.keys():
                    if piano_note in self._note_bitids:
                        if self._note_bitids[piano_note] & winning_chord_bitid:
                            if self.piano_buffered_note_states[piano_note]:
                                self.piano_buffered_note_states[piano_note] = self.piano_buffered_note_states[piano_note][1:]

        # Pedals buffer their own PSX controls in parallel of chord resolution
        for piano_pedal in self.piano_buffered_pedal_states.keys():
            for buffered_state in self.piano_buffered_pedal_states[piano_pedal]:
                if buffered_state["cycles_remaining"] == "∞":
                    if piano_pedal in self._pedal_bitids:
                        # Unshift pedal command to PSX Controller buffer, merging with any pending combo
                        psx_controller_states_for_pedal = self._buffered_states_mapping_for_pedal_bitid[self._pedal_bitids[piano_pedal]]["psx_controller"]
                        for control, single_cycles_count in psx_controller_states_for_pedal.items():
                            cycles_count = single_cycles_count[0]
                            if not self.psx_controller_buffered_states[control]:
                                self.psx_controller_buffered_states[control] = [ cycles_count ]
                            elif self.psx_controller_buffered_states[control][0] < cycles_count:
                                self.psx_controller_buffered_states[control][0] = cycles_count

        # Output PSX Controller Buffered states to PSX Controller
        triggered_controls = ""
        cleared_controls = ""
        for psx_control, buffered_state in self.psx_controller_buffered_states.items():
            if buffered_state:
                cyclesCount = buffered_state.pop(0)
                if cyclesCount > 0:
                    triggered_controls += "(%s, %d) " % (psx_control, cyclesCount)
                    self.psx_controller_state.raiseFlag(psx_control)
                    cyclesCount-= 1
                    # If we're decrementing a cycle count, we don't
                    # want to insert 0 to avoid 'missing a step'.
                    if cyclesCount > 0:
                        buffered_state.insert(0, cyclesCount)
                elif cyclesCount < 0:
                    cleared_controls += "(%s, %d) " % (psx_control, -cyclesCount)
                    self.psx_controller_state.clearFlag(psx_control)
                    cyclesCount+= 1
                    # If we're incrementing a cycle count, we don't
                    # want to insert 0 to avoid 'missing a step'.
                    if cyclesCount < 0:
                        buffered_state.insert(0, cyclesCount)
                else:
                    cleared_controls += "(%s, %d) " % (psx_control, 1)
                    self.psx_controller_state.clearFlag(psx_control)
            else:
                self.psx_controller_state.clearFlag(psx_control)

        if len(triggered_controls) > 0:
            Debug.println("INFO", "Keeping PSX Controls %sTriggered" % triggered_controls)
        if len(cleared_controls) > 0 and len(triggered_controls) == 0:
            Debug.println("INFO", "General pause for 1 cycle")
        elif len(cleared_controls) > 0:
            Debug.println("DEBUG", "Keeping PSX Control %sCleared" % cleared_controls)

        self.console_controller.sendStateBytes()
