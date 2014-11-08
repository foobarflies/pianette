# coding: utf-8

class PianetteException(Exception):
    pass

class PianetteCmdError(PianetteException):
    pass

class PianetteConfigError(PianetteException):
    pass

class PianetteGPIOConfigError(PianetteConfigError):
    pass
