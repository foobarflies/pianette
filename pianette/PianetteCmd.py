# coding: utf-8

import cmd
import pianette.errors
import time

from pianette.utils import Debug

class PianetteCmdUtil:

    # Namespaces

    supported_cmd_namespaces = [ "console", "game", "piano", "time" ]

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
        namespace = None

        if command and PianetteCmdUtil.is_supported_cmd_namespace(command):
            if arg:
                arg_list = arg.split()
                if arg_list and len(arg_list[0]) > 1 and arg_list[0][0] == ".":
                    namespace = command
                    command += "__"
                    command += arg_list[0][1:].replace("-", "_")
                    arg_list.pop(0)
                    arg = " ".join(arg_list)


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

        return command, arg, line

    def do_EOF(self, arg):
        return False

    # Commands

    def do_console__play(self, args):
        Debug.println("INFO", "running command: console.play" + " " + args)
        self.pianette.psx_controller_state.raiseFlag(args)

    def do_console__reset(self, args):
        Debug.println("INFO", "running command: console.reset" + " " + args)
        self.pianette.psx_controller_state.raiseFlag("START")
        self.pianette.psx_controller_state.raiseFlag("SELECT")
        time.sleep(0.2)
        self.pianette.psx_controller_state.clearFlag("START")
        self.pianette.psx_controller_state.clearFlag("SELECT")

    def do_game__select(self, args):
        self.onecmd("console.play ✕")

    def do_game__select_character(self, args):
        self.onecmd("console.play ✕")

    def do_game__select_fighting_style(self, args):
        self.onecmd("console.play ✕")

    def do_game__select_location(self, args):
        self.onecmd("console.play ✕")

    def do_game__select_mode(self, args):
        self.onecmd("console.play ✕")

    def do_piano__play(self, args):
        Debug.println("INFO", "running command: piano.play" + " " + args)
        self.pianette.piano_state.raise_note(args)

    def do_time__sleep(self, args):
        Debug.println("INFO", "running command: time.sleep" + " " + args)
        args_list = args.split()
        if args_list:
            time.sleep(float(args_list[0]))
        else:
            raise pianette.errors.PianetteCmdError("No argument provided for time.sleep")
