# coding: utf-8

import argparse

from pianette.utils import Debug

class PianetteArgumentParser(argparse.ArgumentParser):

  def __init__(self, *args, configobj=None, **kwargs):
      super(PianetteArgumentParser, self).__init__(*args, **kwargs)
      self.configobj = configobj

      supported_sources = self.configobj.get("Pianette").get("supported-sources")
      self.add_argument("-e", "--enable-source", type=str, choices=supported_sources,
                        action="append", help="enable source")

  def parse_args(self, *args, **kwargs):
      args = super(PianetteArgumentParser, self).parse_args(*args, **kwargs)

      # Remove duplicate entries in `enable_source` list
      if args.enable_source is not None:
          args.enable_source = list(set(args.enable_source))

      return args
