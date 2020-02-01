import argparse
import sys
import england.commands
import england.util
from inspect import getmembers, isclass


class Cli(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='amari',
                                         usage='amari <command> [<args>]')
        parser.add_argument('command', choices=self._get_command_list(),
                            help='Subcommand to run.')
        # @TODO Version
        parser.add_argument('-v', '--version', action='version',
                            version='Foo bar baz')
        args = parser.parse_args(sys.argv[1:2])

        if args.command == 'help':
            parser.print_help()
            exit(0)

        for cmd_module in getmembers(england.commands, isclass):
            if isclass(cmd_module[1]):
                if args.command == cmd_module[1].__name__.lower():
                    barbados_cmd = getattr(england.commands, cmd_module[1].__name__)()
                    barbados_cmd.run()
                    exit(0)

        england.util.die("Unrecognized command (%s)" % args.command)

    @staticmethod
    def _get_command_list():
        commands = []
        for cmd_module in getmembers(england.commands, isclass):
            if isclass(cmd_module[1]):
                commands.append(cmd_module[1].__name__.lower())

        commands.append('help')
        return commands
