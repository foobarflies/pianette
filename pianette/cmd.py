# coding: utf-8

import cmd
import random
import time

class PianetteCmd(cmd.Cmd):
    prompt = 'pianette: '

    def __init__(self, piano_state, psx_controller_state):
        super().__init__()
        self.piano_state = piano_state
        self.psx_controller_state = psx_controller_state

    def do_play_note(self, note):
        self.piano_state.raise_note(note)

    def do_play_chord(self, notes_string):
        notes = notes_string.split(',')
        for note in notes:
            self.piano_state.raise_note(note)
            time.sleep(random.randint(0,10)/1000)

    def do_EOF(self, line):
        return True

    def postloop(self):
        print()
