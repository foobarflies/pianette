# coding: utf-8

from utils import *

class PianoState:

    def __init__(self):
        self.notes_state = {
            "C3": False,
            "D3": False,
            "E3": False,
            "F3": False,
            "G3": False,
            "A4": False,
            "B♭4": False,
            "B4": False,
            "C": False,
            "C5": False,
            "D5": False,
            "E♭5": False,
            "E5": False,
            "F5": False,
            "G♭5": False,
            "G5": False,
            "A6": False,
            "B♭6": False,
            "B6": False,
        }

    def __str__(self):
        state_string = ""

        for note, cycles in self.notes_state.items():
            if (cycles > 0):
                state_string += note + " "

        return state_string

    def raise_note(self, note):
        self.notes_state[note] = True

    def clear_note(self, note):
        self.notes_state[note] = False
