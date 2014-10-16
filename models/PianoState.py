from utils import *

class PianoState:
    notes_state = {
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
        "B♭6": 0,
        "B6": 0,
    }

    def __init__(self):
        pass

    def __str__(self):
        state_string = ""
        for note, cycles in self.notes_state.items():
            if (cycles > 0):
                state_string += ("%s (%d) " % (note, cycles))

        return state_string

    def play_note(self, note, duration = 1):
        self.notes_state[note] = max(duration, self.notes_state[note])
