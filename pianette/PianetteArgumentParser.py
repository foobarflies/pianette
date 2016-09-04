# coding: utf-8

import argparse

from pianette.utils import Debug

class PianetteArgumentParser(argparse.ArgumentParser):

  def __init__(self, *args, configobj=None, **kwargs):
      super(PianetteArgumentParser, self).__init__(*args, **kwargs)
      self.configobj = configobj

      supported_sources = self.configobj.get("Pianette").get("supported-sources")
      self.add_argument("-s", "--enable-source", type=str, choices=supported_sources,
                        action="append", dest="enabled_sources", help="enable source")

  def parse_args(self, *args, **kwargs):
      args = super(PianetteArgumentParser, self).parse_args(*args, **kwargs)

      # Remove duplicate entries in `enabled_sources` list
      if args.enabled_sources is not None:
          args.enabled_sources = list(set(args.enabled_sources))

      return args
