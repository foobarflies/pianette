# coding: utf-8

class PianoState:

    notes_state = None

    def __init__(self, notes_state):
        self.notes_state = notes_state

    def __str__(self):
        state_string = ""

        for note, cycles in self.notes_state.items():
            if (cycles > 0):
                state_string += note + " "

        return state_string

    def get_notes_keys(self):
        return self.notes_state.keys()

    def raise_note(self, note):
        self.notes_state[note] = True

    def is_note_raised(self, note):
        return (self.notes_state[note] is True)

    def clear_note(self, note):
        self.notes_state[note] = False

    def is_note_cleared(self, note):
        return (self.notes_state[note] is False)
