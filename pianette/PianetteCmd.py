# coding: utf-8

import cmd
import pianette.errors
import random
import re
import time
import json

from pianette.utils import Debug

class PianetteCmdUtil:

    # Namespaces
    supported_cmd_namespaces = [ "console", "game", "piano", "pianette", "time" ]

    @staticmethod
    def is_supported_cmd_namespace(cmd_namespace):
        return cmd_namespace in PianetteCmdUtil.supported_cmd_namespaces


class PianetteCmd(cmd.Cmd):
    prompt = 'pianette: '

    def __init__(self, configobj=None, pianette=None, **kwargs):
        super().__init__(**kwargs)
        self.configobj = configobj
        self.pianette = pianette

    def parseline(self, line):
        # Pianette-specific command parser
        command, arg, line = super().parseline(line)

        if command and command != "EOF":
            command = command.lower()

        # Rewrite namespaced commands for cmd to properly map them
        # The default parser would interpret "namespace.do-stuff arg1 arg2" as the "namespace" command with arguments ".do-stuff", "arg1", "arg2"
        # What we want instead, is the "namespace__do_stuff" command with arguments "arg1", "arg2"
        # .. Except for the game namespace, where commands are dynamic, so we want to keep the ".do-stuff" as the first argument
        namespace = None

        if command and PianetteCmdUtil.is_supported_cmd_namespace(command):
            if arg and command != "game":
                arg_list = arg.split()
                if arg_list and len(arg_list[0]) > 1 and arg_list[0][0] == ".":
                    namespace = command
                    command += "__"
                    command += arg_list[0][1:].replace("-", "_")
                    arg_list.pop(0)
                    arg = " ".join(arg_list)

        if command == "game":
            # Let's sanitize the command name and keep arg a list of arguments
            arg_list = arg.split()
            if arg_list and len(arg_list[0]) > 1 and arg_list[0][0] == ".":
                arg_list[0] = arg_list[0][1:].replace("-", "_")
                arg = arg_list

        if namespace == "piano":
            # Assume that some arguments in piano commands include aliases for harder-to type characters
            arg = arg.replace("b", "♭")
            arg = arg.replace("#", "♯")

        if namespace == "console":
            arg = arg.upper()

            # Assume that some arguments in console commands include aliases for harder-to type characters
            arg = arg.replace("UP", "↑")
            arg = arg.replace("RIGHT", "→")
            arg = arg.replace("DOWN", "↓")
            arg = arg.replace("LEFT", "←")

            arg = arg.replace("SQUARE", "□")
            arg = arg.replace("TRIANGLE", "△")
            arg = arg.replace("CROSS", "✕")
            arg = arg.replace("CIRCLE", "◯")

            # Assume that some arguments in console commands include aliases for longer-to type arguments
            arg = arg.replace("↖", "← + ↑")
            arg = arg.replace("↗", "↑ + →")
            arg = arg.replace("↘", "→ + ↓")
            arg = arg.replace("↙", "↓ + ←")

        # Insert safe spaces around "+" signs when arg is a string
        if (arg is not None and not isinstance(arg, list)):
            arg = re.sub('\s*\+\s*',' + ', arg)

        return command, arg, line

    def do_EOF(self, arg):
        return False

    # Overrides
    def emptyline(self):
        return

    # Commands

    def do_console__hit(self, args):
        Debug.println("INFO", "running command: console.hit" + " " + args)
        self.pianette.push_console_controls(args, duration_cycles=1)

    def do_console__play(self, args):
        Debug.println("INFO", "running command: console.play" + " " + args)
        self.pianette.push_console_controls(args)

    def do_console__reset(self, args):
        Debug.println("INFO", "running command: console.reset" + " " + args)
        self.onecmd("console.play START + SELECT")

    def do_game(self, args):
        module = self.pianette.get_selected_game_module()
        game = self.pianette.get_selected_game()
        config = self.pianette.get_selected_game_config()
        player_config = self.pianette.get_selected_player_config()
        try:
            method = args[0]
            # Call the relevant game method from the loaded module
            getattr(module, method)(args[1:], cmd=self, config=config, player_config=player_config)
        except IndexError:
            Debug.println("WARNING", "You must specify a command")
        except AttributeError:
            # Method does not exist, gracefully fail
            Debug.println("WARNING", "Command %s (%s) does not exist for the game '%s'" % (method, args[1:], game))

    def do_pianette__disable_source(self, args):
        Debug.println("INFO", "running command: pianette.disable_source" + " " + args)
        self.pianette.disable_source(args)

    def do_pianette__enable_source(self, args):
        Debug.println("INFO", "running command: pianette.enable_source" + " " + args)
        self.pianette.enable_source(args)

    def do_pianette__select_game(self, args):
        Debug.println("INFO", "running command: pianette.select_game" + " " + args)
        self.pianette.select_game(args)

    def do_pianette__dump_state(self, args):
        Debug.println("INFO", "running command: pianette.dump_state")

        # Dump general info on the pianette instance
        Debug.println("NOTICE", "Enabled sources: %s" % self.pianette.get_selected_player())

        # Dump general game configuration
        Debug.println("NOTICE", "Currently selected game: '%s'" % self.pianette.get_selected_game())
        Debug.println("NOTICE", "Current game config:")
        print(json.dumps(self.pianette.get_selected_game_config(), sort_keys=True, indent=4))
        
        # Dump player specific configuration for this game
        Debug.println("NOTICE", "Currently selected player: %s" % self.pianette.get_selected_player())
        Debug.println("NOTICE", "Current player config:")
        print(json.dumps(self.pianette.get_selected_player_config(), sort_keys=True, indent=4))

    def do_piano__play(self, args):
        Debug.println("INFO", "running command: piano.play" + " " + args)
        self.pianette.push_piano_notes(args)

    def do_piano__hold(self, args):
        Debug.println("INFO", "running command: piano.hold" + " " + args)
        self.pianette.hold_piano_pedals(args)

    def do_piano__release(self, args):
        Debug.println("INFO", "running command: piano.release" + " " + args)
        self.pianette.release_piano_pedals(args)

    def do_time__sleep(self, args):
        Debug.println("INFO", "running command: time.sleep" + " " + args)
        args_list = args.split()
        if args_list:
            time.sleep(float(args_list[0]))
        else:
            raise pianette.errors.PianetteCmdError("No argument provided for time.sleep")
