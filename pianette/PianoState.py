# coding: utf-8

class PianoState:

    def __init__(self, configobj=None):
        self.configobj = configobj

        self.note_states = {}
        try:
            self.note_states = { k: False for k in self.configobj['Piano']['supported-notes'] }
        except KeyError:
            pass

    def __str__(self):
        state_string = ""

        for note, cycles in self.note_states.items():
            if (cycles > 0):
                state_string += note + " "

        return state_string

    def get_notes_keys(self):
        return self.note_states.keys()

    def raise_note(self, note):
        self.note_states[note] = True

    def is_note_raised(self, note):
        return (self.note_states[note] is True)

    def clear_note(self, note):
        self.note_states[note] = False

    def is_note_cleared(self, note):
        return (self.note_states[note] is False)
