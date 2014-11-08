# coding=utf-8

from copy import deepcopy
from pianette.ConsoleController import ConsoleController
from pianette.ControllerState import ControllerState
from pianette.PianetteCmd import PianetteCmd
from pianette.PianoState import PianoState
from pianette.utils import Debug

import threading

# Pianette Configuration

# Period of I/O cycle, in seconds
PIANETTE_CYCLE_PERIOD = 10/1000 # Seems to properly operate between 7 msecs and 26 msecs (PSX observation)

# Number of cycles before Inputs are processed and sent to Output
PIANETTE_PROCESSING_CYCLES = 2

# Number of cycles for the duration of a single console.play
PIANETTE_CONSOLE_PLAY_DURATION_CYCLES = 3

# Mapping: Piano Notes (input) => PSX Controller Combo (output)
PIANETTE_BUFFERED_STATES_MAPPINGS = [
    # Single Notes (left hand): Moves
    {
        "piano": [ "C1" ],
        "psx_controller": { "LEFT": [ 9 ] },
    },
    {
        "piano": [ "G1" ],
        "psx_controller": { "DOWN": [ 9 ] },
    },
    {
        "piano": [ "C2" ],
        "psx_controller": { "RIGHT": [ 9 ] },
    },

    # Single Notes (right hand): Simple Strikes
    # SQUARE
    {
        "piano": [ "C3" ],
        "psx_controller": { "S": [ 3 ] },
    },
    {
        "piano": [ "D♭3" ],
        "psx_controller": { "S": [ 3 ] },
    },
    {
        "piano": [ "D3" ],
        "psx_controller": { "S": [ 3 ] },
    },
    {
        "piano": [ "E♭3" ],
        "psx_controller": { "S": [ 3 ] },
    },
    # TRIANGLE
    {
        "piano": [ "E3" ],
        "psx_controller": { "T": [ 3 ] },
    },
    {
        "piano": [ "F3" ],
        "psx_controller": { "T": [ 3 ] },
    },
    {
        "piano": [ "G♭3" ],
        "psx_controller": { "T": [ 3 ] },
    },
    # O
    {
        "piano": [ "G3" ],
        "psx_controller": { "O": [ 3 ] },
    },
    {
        "piano": [ "A♭3" ],
        "psx_controller": { "O": [ 3 ] },
    },
    {
        "piano": [ "A3" ],
        "psx_controller": { "O": [ 3 ] },
    },
    # X
    {
        "piano": [ "B♭3" ],
        "psx_controller": { "X": [ 3 ] },
    },
    {
        "piano": [ "B3" ],
        "psx_controller": { "X": [ 3 ] },
    },
    {
        "piano": [ "C4" ],
        "psx_controller": { "X": [ 3 ] },
    },
  
    # Chords (left hand): Combo Moves!
    {
        "piano": [ "C1", "G1", "C2" ],
        "psx_controller": { "UP" : [ 3 ] },
    },
    {
        "piano": [ "C1", "G1" ],
        "psx_controller": { "UP" : [ 3 ], "LEFT": [ 3 ] },
    },
    {
        "piano": [ "G1", "C2" ],
        "psx_controller": { "UP" : [ 3 ], "RIGHT": [ 3 ] },
    },

    # Chords (right hand): Combo Strikes!

# FIX ME
    {
        # S1 + X1 + O1 (Do majeur) => Tatsukami
        "piano": [ "C5", "E5", "D5" ],
        "psx_controller": { "DOWN" : [ 1, 3 ],  "RIGHT" : [ -1, 3, 3 ], "X" : [ -1, -3, -3, 10] },
    },
    {
        # S1 + X1 + O1 + CR3 (Do 7e) => Hadouken
        "piano": [ "C5", "E5", "D5", "B♭6" ],
        "psx_controller": { "DOWN" : [ 1, 3 ],  "LEFT" : [ -1, 3, 3 ], "S" : [ -1, -3, -3, 10] },
    },
    {
        # S1 + S2 + T1 (Do 6) => ?
        "piano": [ "C5", "F5", "A6" ],
        "psx_controller": {},
    },
    {
        # S1 + CR1 + O1 (Do min) => ?
        "piano": [ "C5", "E♭5", "D5" ],
        "psx_controller": {},
    },
    {
        # S1 + CR1 + O1 + CR3 (Do min 7e) => ?
        "piano": [ "C5", "E♭5", "D5", "B♭6" ],
        "psx_controller": {},
    },
    {
        # S1 + CR1 + CR2 + CR3 (Dim 3) => ?
        "piano": [ "C5", "E5", "G♭5", "B♭6" ],
        "psx_controller": {},
    },
# FIX ME 
]

# Assign a unique, combinable bitid to configured notes
_NOTE_BITIDS = {}

_current_note_bitid = 0b1
for buffered_state_mapping in PIANETTE_BUFFERED_STATES_MAPPINGS:
    for note in buffered_state_mapping["piano"]:
        if not note in _NOTE_BITIDS:
            _NOTE_BITIDS[note] = _current_note_bitid
            _current_note_bitid <<= 1
del _current_note_bitid

# Structure Buffered States Mapping using Piano "Chords" bitids (combination of Note bitids)
# Rank chords as follows:
#   1- chords with more notes have a higher priority
#   2- for an equal number of notes, chords declared first in config have a higher priority
_ranked_chord_bitids_for_note_count = {}

_BUFFERED_STATES_MAPPING_FOR_CHORD_BITID = {}
for buffered_state_mapping in PIANETTE_BUFFERED_STATES_MAPPINGS:
    chord_bitid = 0b0
    note_count = len(buffered_state_mapping["piano"])

    for note in buffered_state_mapping["piano"]:
        chord_bitid |= _NOTE_BITIDS[note]

    _BUFFERED_STATES_MAPPING_FOR_CHORD_BITID[chord_bitid] = buffered_state_mapping
    chord_bitids = _ranked_chord_bitids_for_note_count.get(note_count, [])
    chord_bitids.append(chord_bitid)
    _ranked_chord_bitids_for_note_count[note_count] = chord_bitids

_RANKED_CHORD_BITIDS = []
for note_count in sorted(list(_ranked_chord_bitids_for_note_count.keys()), reverse = True):
    _RANKED_CHORD_BITIDS.extend(_ranked_chord_bitids_for_note_count[note_count])
del _ranked_chord_bitids_for_note_count

def get_notes_chord_bitid(notes):
    notes_bitids = [ _NOTE_BITIDS[note] for note in notes ]
    notes_chord_bitid = 0b0
    for bitid in notes_bitids:
        notes_chord_bitid |= bitid
    return notes_chord_bitid

def get_ranked_chord_bitids_including_at_least_one_of_notes(notes, from_chord_bitids_pool = _RANKED_CHORD_BITIDS):
    notes_chord_bitid = get_notes_chord_bitid(notes)

    ranked_notes_chord_bitids = []
    for chord_bitid in from_chord_bitids_pool:
        if (chord_bitid & notes_chord_bitid):
            ranked_notes_chord_bitids.append(chord_bitid)

    return ranked_notes_chord_bitids

class Pianette:
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

        self.pianette_buffered_states_mappings = []

        for notes_string, controls_string in pianette_mappings_configobj.items():
            if not isinstance(controls_string, str):
                # Not a string, probably a configuration sub-section
                pass
            else:
                # Assume that some arguments in console commands include aliases for longer-to type arguments
                controls_string = controls_string.replace("↖", "← + ↑")
                controls_string = controls_string.replace("↗", "↑ + →")
                controls_string = controls_string.replace("↘", "→ + ↓")
                controls_string = controls_string.replace("↙", "↓ + ←")

                self.pianette_buffered_states_mappings .append({
                    "piano": notes_string.replace("+", " ").split(),
                    "psx_controller": Pianette.get_buffered_states_for_controls_string(controls_string)
                })

    def __init__(self, configobj=None):
        self.__init_using_configobj(configobj=configobj)

        self.piano_state = PianoState(configobj=self.configobj)
        self.psx_controller_state = ControllerState(configobj=self.configobj)

        # Instantiate the console controller that is responsible for sendint out the psx constroller state to the console
        self.console_controller = ConsoleController(self.psx_controller_state, configobj=self.configobj)

        # Upcoming state cycles for the Piano Notes (input)
        self.piano_buffered_states = {}
        try:
            self.piano_buffered_states = { k: [] for k in self.configobj['Piano']['supported-notes'] }
        except KeyError:
            pass

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

    @staticmethod
    def get_buffered_states_for_controls_string(controls_string):
        controls_buffered_states = {}
        time_index = 0

        for control in controls_string.split():
            if control == "+":
                time_index -= PIANETTE_CONSOLE_PLAY_DURATION_CYCLES
            else:
                if control in controls_buffered_states:
                    buffer_duration = 0
                    for duration in controls_buffered_states[control]:
                        buffer_duration += abs(duration)

                    if time_index - buffer_duration > 0:
                        controls_buffered_states[control].append(-time_index + buffer_duration)
                        controls_buffered_states[control].append(PIANETTE_CONSOLE_PLAY_DURATION_CYCLES)
                    else:
                        controls_buffered_states[control][-1] += PIANETTE_CONSOLE_PLAY_DURATION_CYCLES

                else:
                    controls_buffered_states[control] = []

                    if time_index > 0:
                        controls_buffered_states[control].append(-time_index)

                    controls_buffered_states[control].append(PIANETTE_CONSOLE_PLAY_DURATION_CYCLES)

                time_index += PIANETTE_CONSOLE_PLAY_DURATION_CYCLES

        return controls_buffered_states

    def push_console_controls(self, controls_string):
        controls_buffered_states = Pianette.get_buffered_states_for_controls_string(controls_string)

        for control, buffered_states in controls_buffered_states.items():
            self.psx_controller_buffered_states[control] = buffered_states

    def push_piano_notes(self, notes_string):
        for note in notes_string.split():
            self.piano_state.raise_note(note)

    # Timer Methods

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
        # Input Piano Notes to Piano Buffered States
        for piano_note in self.piano_state.get_notes_keys():
            if self.piano_state.is_note_raised(piano_note):
                Debug.println("INFO", "Processing Piano Note %s" % (piano_note))
                self.piano_buffered_states[piano_note].append({ "cycles_remaining": PIANETTE_PROCESSING_CYCLES })
                self.piano_state.clear_note(piano_note)

        # Process Buffered States: Determine piano note or chord
        # Notes that have reached their last cycle "lead" the chord determination
        # Other notes may be used to "complement" lead notes.
        # If a winning chord is found, push corresponding combo to PSX Controller buffer
        # If complementary notes are actually used, they are discarded from buffer.
        lead_notes = []
        complementary_notes = []
        for piano_note in self.piano_buffered_states.keys():
            processed_buffered_states = []
            for buffered_state in self.piano_buffered_states[piano_note]:
                if buffered_state["cycles_remaining"] == 0:
                    lead_notes.append(piano_note)
                else:
                    complementary_notes.append(piano_note)
                    buffered_state["cycles_remaining"] -= 1
                    processed_buffered_states.append(buffered_state)
            self.piano_buffered_states[piano_note] = processed_buffered_states

        if lead_notes:
            Debug.println("INFO", "Processing Piano Notes: lead=%s, complementary=%s" % (lead_notes, complementary_notes))
            ranked_chord_bitids = get_ranked_chord_bitids_including_at_least_one_of_notes(lead_notes)

            all_notes_chord_bitid = get_notes_chord_bitid(lead_notes + complementary_notes)
            ranked_winning_chord_bitids = [chord_bitid for chord_bitid in ranked_chord_bitids if not ((all_notes_chord_bitid & chord_bitid) ^ chord_bitid)]

            if ranked_winning_chord_bitids:
                winning_chord_bitid = ranked_winning_chord_bitids[0]
                winning_states_mapping = deepcopy(_BUFFERED_STATES_MAPPING_FOR_CHORD_BITID[winning_chord_bitid])

                # Push piano command to PSX Controller buffer, clearing any pending combo
                for control in self.psx_controller_buffered_states.keys():
                    self.psx_controller_buffered_states[control] = winning_states_mapping["psx_controller"].get(control, [])

                # Clear winning chord notes from the piano buffer
                for piano_note in self.piano_buffered_states.keys():
                    if _NOTE_BITIDS[piano_note] & winning_chord_bitid:
                        if self.piano_buffered_states[piano_note]:
                            self.piano_buffered_states[piano_note] = self.piano_buffered_states[piano_note][1:]

        # Output PSX Controller Buffered states to PSX Controller
        for psx_control, buffered_state in self.psx_controller_buffered_states.items():
            if buffered_state:
                cyclesCount = buffered_state.pop(0)
                if cyclesCount > 0:
                    Debug.println("INFO", "Keeping PSX Control %s Triggered for %d cycles" % (psx_control, cyclesCount))
                    self.psx_controller_state.raiseFlag(psx_control)
                    cyclesCount-= 1
                    buffered_state.insert(0, cyclesCount)
                elif cyclesCount < 0:
                    Debug.println("INFO", "Keeping PSX Control %s Cleared for %d cycles" % (psx_control, -cyclesCount))
                    self.psx_controller_state.clearFlag(psx_control)
                    cyclesCount+= 1
                    buffered_state.insert(0, cyclesCount)
                else:
                    Debug.println("INFO", "Clearing PSX Control %s" % psx_control)
                    self.psx_controller_state.clearFlag(psx_control)
            else:
                self.psx_controller_state.clearFlag(psx_control)

        self.console_controller.sendStateBytes()
