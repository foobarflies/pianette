# coding=utf-8

from utils import *

import threading
import time

class Pianette(object):
    def __init__(self, piano_state, psx_controller_state):
        self.piano_state = piano_state
        self.psx_controller_state = psx_controller_state

        self.stateBuffers = {
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

        self._interval = 10/1000 # 7 msecs < _interval < 26 msecs
        popStateBuffersThread = threading.Thread(target=self.popStateBuffersWorker)
        popStateBuffersThread.daemon = True
        popStateBuffersThread.start()
        Debug.println("INFO", "Pianette popStateBuffersWorker initialized at %f secs interval" % self._interval)

    def popStateBuffersWorker(self):
        while(True):
            for control, controlBuffer in self.stateBuffers.items():
                if controlBuffer:
                    cyclesCount = controlBuffer.pop(0)
                    if cyclesCount > 0:
                        self.psx_controller_state.raiseFlag(control)
                        cyclesCount-= 1
                        controlBuffer.insert(0, cyclesCount)
                    elif cyclesCount < 0:
                        self.psx_controller_state.clearFlag(control)
                        cyclesCount+= 1
                        controlBuffer.insert(0, cyclesCount)
                    else:
                        self.psx_controller_state.clearFlag(control)

            time.sleep(self._interval)
