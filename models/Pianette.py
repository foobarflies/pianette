# coding=utf-8

from utils import *

import threading

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
        self._timer_interval = 10/1000 # 7 msecs < _interval < 26 msecs
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
