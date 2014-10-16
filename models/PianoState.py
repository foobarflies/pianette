# coding: utf-8

import threading
from utils import *

class PianoState:

    def __init__(self):
        self.notes_state = {
            "C3": 0,
            "D3": 0,
            "E3": 0,
            "F3": 0,
            "G3": 0,
            "A4": 0,
            "B♭4": 0,
            "B4": 0,
            "C": 0,
            "C5": 0,
            "D5": 0,
            "E♭5": 0,
            "E5": 0,
            "F5": 0,
            "G♭5": 0,
            "G5": 0,
            "A6": 0,
            "B♭6": 10,
            "B6": 0,
        }

        self._timer = None
        self._timer_interval = 5/1000 # 5ms
        self._timer_is_running = False

        # Start the timer thread that will decrease notes cycles at each interval
        self.start_timer()

    def __del__(self):
        if _timer in self:
            self.stop_timer()

    def _run_timer(self):
        self._timer_is_running = False
        self.start_timer()
        self.decrement_notes_cycles()

    def start_timer(self):
        if not self._timer_is_running:
            self._timer = threading.Timer(self._timer_interval, self._run_timer)
            self._timer.start()
            self.is_running = True

    def stop_timer(self):
        self._timer.cancel()
        self._timer_is_running = False

    def decrement_notes_cycles(self):
        for note in self.notes_state.keys():
            cycles = self.notes_state[note]
            if (cycles > 0):
                self.notes_state[note] -= 1

    def __str__(self):
        state_string = ""

        for note, cycles in self.notes_state.items():
            if (cycles > 0):
                state_string += ("%s (%d) " % (note, cycles))

        return state_string

    """
    note is a string
    duration is expressed in seconds
    """
    def play_note(self, note, duration = 1/10):
        cycles_for_duration = int(duration / self._timer_interval)
        self.notes_state[note] = max(cycles_for_duration, self.notes_state[note])
