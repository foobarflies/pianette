# coding=utf-8

from utils import *

import threading

# Pianette Mappings: Piano Notes => PSX Controller Combo
# Ranked by descending order of priority
PIANETTE_BUFFERED_STATES_MAPPINGS = [
    # Single Notes (left hand): Moves
    {
        "piano": [ "C3" ],
        "psx_controller": { "LEFT": [ 3 ] },
    },
    {
        "piano": [ "D3" ],
        "psx_controller": { "LEFT": [ 3 ] },
    },
    {
        "piano": [ "F3" ],
        "psx_controller": { "DOWN": [ 3 ] },
    },
    {
        "piano": [ "A4" ],
        "psx_controller": { "RIGHT": [ 3 ] },
    },
    {
        "piano": [ "B4" ],
        "psx_controller": { "RIGHT": [ 3 ] },
    },

    # Single Notes (right hand): Simple Strikes
    {
        "piano": [ "C5" ],
        "psx_controller": { "S": [ 3 ] },
    },
    {
        "piano": [ "D5" ],
        "psx_controller": { "O": [ 3 ] },
    },
    {
        "piano": [ "E5" ],
        "psx_controller": { "X": [ 3 ] },
    },
    {
        "piano": [ "F5" ],
        "psx_controller": { "S": [ 3 ] },
    },
    {
        "piano": [ "G5" ],
        "psx_controller": { "O": [ 3 ] },
    },
    {
        "piano": [ "A6" ],
        "psx_controller": { "T": [ 3 ] },
    },
    {
        "piano": [ "B6" ],
        "psx_controller": { "T": [ 3 ] },
    },

    # Chords (left hand): Combo Moves!
    {
        # LEFT1 + CL1 + CL2 (Do majeur) => UP
        "piano": [ "C3", "E3", "G3" ],
        "psx_controller": { "UP" : [ 3 ] },
    },
    {
        # LEFT1 + CL4 (Do octave) => UP
        "piano": [ "C3", "E3", "G3" ],
        "psx_controller": { "UP" : [ 3 ] },
    },
    {
        # LEFT1 + CL1 + CL2 + CL3 (Do majeur 7e) => UP + Kick droit (ou gauche suivant player)
        "piano": [ "C3", "E3", "G3", "B♭4" ],
        "psx_controller": { "UP" : [ 3 ], "X": [ -1, 3 ] },
    },
    {
        # CL1 + CL2 + CL4 (Do Majeur premier renversement) => UP+RIGHT
        "piano": [ "E3", "G3", "C4" ],
        "psx_controller": { "RIGHT" : [ 3 ], "UP": [ -1, 3 ] },
    },
    {
        # LEFT1 + DOWN (Do Dim 4) => DOWN+LEFT
        "piano": [ "C3", "F3" ],
        "psx_controller": { "DOWN" : [ 3 ], "LEFT": [ 3 ] },
    },
    {
        # LEFT2 + DOWN (Ré Min) => DOWN+LEFT
        "piano": [ "D3", "F3" ],
        "psx_controller": { "DOWN" : [ 3 ], "LEFT": [ 3 ] },
    },
    {
        # RIGHT1 + DOWN (Ré min) => RIGHT+DOWN
        "piano": [ "A4", "F3" ],
        "psx_controller": { "DOWN" : [ 3 ], "RIGHT": [ 3 ] },
    },
    {
        # RIGHT2 + DOWN (Si) => RIGHT+DOWN
        "piano": [ "B4", "F3" ],
        "psx_controller": { "DOWN" : [ 3 ], "RIGHT": [ 3 ] },
    },

    # Chords (right hand): Combo Strikes!

    {
        # S1 + X1 + O1 (Do majeur) => Tatsukami
        "piano": [ "C5", "E5", "D5" ],
        "psx_controller": { "DOWN" : [ 1, 3 ],  "LEFT" : [ -1, 3, 3 ], "X" : [ -1, -3, -3, 10] },
    },
    {
        # S1 + X1 + O1 + CR3 (Do 7e) => Hadouken
        "piano": [ "C5", "E5", "D5", "B♭6" ],
        "psx_controller": { "DOWN" : [ 1, 3 ],  "LEFT" : [ -1, 3, 3 ], "X" : [ -1, -3, -3, 10] },
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

    # "Combo Enabler" keys, no direct mapping
    # "E3" (AKA "CL1")
    # "G3" (AKA "CL2")
    # "B♭4" (AKA "CL3")
    # "C4" (AKA "CL4")
    # "E♭5" (AKA "CR1")
    # "G♭5" (AKA "CR2")
    # "B♭6" (AKA "CR3")
]

class Pianette(object):
    def __init__(self, piano_state, psx_controller_state):
        self.piano_state = piano_state
        self.psx_controller_state = psx_controller_state

        # Upcoming state cycles for the Piano Notes (input)
        self.piano_buffered_states = {
            "C3": [],
            "D3": [],
            "E3": [],
            "F3": [],
            "G3": [],
            "A4": [],
            "B♭4": [],
            "B4": [],
            "C": [],
            "C5": [],
            "D5": [],
            "E♭5": [],
            "E5": [],
            "F5": [],
            "G♭5": [],
            "G5": [],
            "A6": [],
            "B♭6": [],
            "B6": [],
        }

        # Upcoming state cycles for the PSX Controller (output)
        self.psx_controller_buffered_states = {
            "T" : [],
            "S" : [],
            "X" : [],
            "O" : [],
            "UP" : [],
            "DOWN" : [],
            "LEFT" : [],
            "RIGHT" : [],
            "SELECT" : [],
            "START" : [],
        }

        self._timer = None
        self._timer_interval = 10/1000 # 7 msecs < _interval < 26 msecs for proper PSX controller operation
        self._timer_is_running = False

        # Start the timer thread that will cycle buffered states at each interval
        self.start_timer()
        Debug.println("INFO", "Pianette buffered states timer thread started at %f secs interval" % self._timer_interval)

    def __del__(self):
        if _timer in self:
            self.stop_timer()

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

        # Output PSX Controller Buffered states to PSX Controller
        for psx_control, buffered_state in self.psx_controller_buffered_states.items():
            if buffered_state:
                cyclesCount = buffered_state.pop(0)
                if cyclesCount > 0:
                    self.psx_controller_state.raiseFlag(psx_control)
                    cyclesCount-= 1
                    buffered_state.insert(0, cyclesCount)
                elif cyclesCount < 0:
                    self.psx_controller_state.clearFlag(psx_control)
                    cyclesCount+= 1
                    buffered_state.insert(0, cyclesCount)
                else:
                    self.psx_controller_state.clearFlag(psx_control)
