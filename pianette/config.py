# coding: utf-8

import os.path

from configobj import ConfigObj
from pianette.utils import Debug

PIANETTE_CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir, "config"))

def get_configobj(*config_files):
    configobj = ConfigObj()

    for config_file in config_files:
        Debug.println("INFO", "Reading configuration file %s ..." % (config_file))
        configobj.merge(ConfigObj(os.path.join(PIANETTE_CONFIG_PATH, config_file + ".ini")))

    return configobj
