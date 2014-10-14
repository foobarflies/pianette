import threading
import datetime
import time

class ControllerStateTimedBuffer(object):
    def __init__(self, controllerState, consoleController):
        self.controllerState = controllerState
        self.consoleController = consoleController

        self.stateBuffers = {
            "T" : [],
            "S" : [],
            "X" : [],
            "O" : [],
            "UP" : [],
            "DOWN" : [],
            "RIGHT" : [],
            "LEFT" : [],
            "SELECT" : [],
            "START" : [],
        }

        self._interval = 0.010 # 7 msecs < _interval < 26 msecs

    def popStateBuffers(self):
        while(True):
            lock = threading.Lock()
            lock.acquire()
            for control, controlBuffer in self.stateBuffers.items():
                if controlBuffer:
                    cyclesCount = controlBuffer.pop(0)
                    if cyclesCount > 0:
                        self.controllerState.raiseFlag(control)
                        cyclesCount-= 1
                        controlBuffer.insert(0, cyclesCount)
                    elif cyclesCount < 0:
                        self.controllerState.clearFlag(control)
                        cyclesCount+= 1
                        controlBuffer.insert(0, cyclesCount)
                    else:
                        self.controllerState.clearFlag(control)

            lock.release()
            time.sleep(self._interval)
