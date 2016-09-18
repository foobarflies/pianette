# coding: utf-8

import os.path

from configobj import ConfigObj
from pianette.utils import Debug

PIANETTE_CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), os.path.pardir, "config"))

def get_all_configobj():
    configobj = ConfigObj()

    for root, dirs, files in os.walk(PIANETTE_CONFIG_PATH):
        for file in files:
            if file.endswith(".ini"):
                Debug.println("INFO", "Reading configuration file %s/%s ..." % (os.path.basename(root), file))
                configobj.merge(ConfigObj(os.path.join(root, file)))

    return configobj