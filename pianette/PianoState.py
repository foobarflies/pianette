# coding: utf-8

from pianette.errors import PianetteConfigError
from pianette.utils import Debug

class PianoState:

    # Private methods: Config

    def __init_using_configobj(self, configobj=None):
        if not configobj.__class__.__name__ == 'ConfigObj':
            raise PianetteConfigError('Unsupported Piano config')

        if not 'Piano' in configobj.dict().keys():
            raise PianetteConfigError('Piano config not found')

        self.configobj = configobj

        self.__init_note_states()
        self.__init_pedal_states()

    # Private methods: Notes

    def __init_note_states(self):
        try:
            supported_notes = self.configobj['Piano']['supported-notes']
        except KeyError:
            raise PianetteConfigError('Piano config must define supported-notes')

        self.note_states = {}
        for note in supported_notes:
            self.__set_note_state(note, False)

        Debug.println('SUCCESS', 'Piano note states initialized')

    def __assert_supported_note(self, note):
        if not note in self.note_states:
            raise KeyError('Piano does not support note "%s"' % note)

    def __get_note_state(self, note):
        return self.note_states[note]

    def __set_note_state(self, note, state):
        self.note_states[note] = state

    # Private methods: Pedals

    def __init_pedal_states(self):
        try:
            supported_pedals = self.configobj['Piano']['supported-pedals']
        except KeyError:
            raise PianetteConfigError('Piano config must define supported-pedals')

        self.pedal_states = {}
        for pedal in supported_pedals:
            self.__set_pedal_state(pedal, False)

        Debug.println('SUCCESS', 'Piano pedal states initialized')

    def __assert_supported_pedal(self, pedal):
        if not pedal in self.pedal_states:
            raise KeyError('Piano does not support pedal "%s"' % pedal)

    def __get_pedal_state(self, pedal):
        return self.pedal_states[pedal]

    def __set_pedal_state(self, pedal, state):
        self.pedal_states[pedal] = state

    # Constructor

    def __init__(self, configobj=None):
        self.__init_using_configobj(configobj)
        Debug.println('SUCCESS', 'Piano initialized')

    # Public methods: Config

    def set_configobj(self, configobj=None):
        self.__init_using_configobj(configobj)
        Debug.println('SUCCESS', 'Piano config changed')

    # Public methods: Notes

    def switch_note_off(self, note):
        self.__assert_supported_note(note)
        self.__set_note_state(note, False)

    def switch_note_on(self, note):
        self.__assert_supported_note(note)
        self.__set_note_state(note, True)

    def is_note_off(self, note):
        self.__assert_supported_note(note)
        return self.__get_note_state(note) is False

    def is_note_on(self, note):
        self.__assert_supported_note(note)
        return self.__get_note_state(note) is True

    def get_supported_notes(self):
        return self.note_states.keys()

    # Public methods: Pedals

    def switch_pedal_off(self, pedal):
        self.__assert_supported_pedal(pedal)
        self.__set_pedal_state(pedal, False)

    def switch_pedal_on(self, pedal):
        self.__assert_supported_pedal(pedal)
        self.__set_pedal_state(pedal, True)

    def is_pedal_off(self, pedal):
        self.__assert_supported_pedal(pedal)
        return self.__get_pedal_state(pedal) is False

    def is_pedal_on(self, pedal):
        self.__assert_supported_pedal(pedal)
        return self.__get_pedal_state(pedal) is True

    def get_supported_pedals(self):
        return self.pedal_states.keys()
