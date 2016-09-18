# coding: utf-8

import argparse

from pianette.utils import Debug

class Single(argparse.Action):
    # Thank you http://stackoverflow.com/a/14916104/162086
    def __call__(self, parser, namespace, values, option_string = None):
        if getattr(namespace, self.dest) is not None:
            msg = '{o} can only be specified once'.format(o = option_string)
            raise argparse.ArgumentError(None, msg)
        setattr(namespace, self.dest, values)

class PianetteArgumentParser(argparse.ArgumentParser):

  def __init__(self, *args, configobj=None, **kwargs):
      super(PianetteArgumentParser, self).__init__(*args, **kwargs)
      self.configobj = configobj

      supported_sources = self.configobj.get("Pianette").get("supported-sources")
      self.add_argument("-s", "--enable-source", type=str, choices=supported_sources,
                        action="append", dest="enabled_sources", help="Enable a source to be used as an input for Pianette")

      self.add_argument("-p", "--select-player", type=int, choices=[1,2],
                        action=Single, dest="selected_player", help="Select the actual player, i.e. the port of the console in which this instance is plugged")

      available_games = self.configobj.get("Game").keys()
      self.add_argument("-g", "--select-game", type=str, choices=available_games,
                        action=Single, dest="selected_game", help="Select the game — games are defined as Python modules and must reside in config/games")

  def parse_args(self, *args, **kwargs):
      args = super(PianetteArgumentParser, self).parse_args(*args, **kwargs)

      # Remove duplicate entries in `enabled_sources` list
      if args.enabled_sources is not None:
          args.enabled_sources = list(set(args.enabled_sources))

      return args
