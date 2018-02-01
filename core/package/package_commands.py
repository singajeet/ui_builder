"""
package_commands.py
Contains commands for performing package related tasks
"""
from ui_builder.core.provider import commands, cmd_parser
import service

class PackageCommands(object):

    """Docstring for PackageCommand. """
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    LIST = 'list'
    SHOW = 'show'
    LOAD = 'load'

    def __init__(self, pkg_manager):
        """TODO: to be defined1. """
        self.package_manager = pkg_manager
        self.pkg_mgr_commands_map = {}
        self.cmd_parser = cmd_parser.CommandParser()

    def register_commands(self):
        self.register_command(PackageCommands.INSTALL, 'Install all packages (or specific one) available in package drop location', self.install_packages_command, '--all')
        self.register_command(PackageCommands.UNINSTALL, 'Uninstall specified package from the system', self.uninstall_packages_command)
        self.register_command(PackageCommands.LOAD, 'Load all packages (or specified one) available in the system', self.load_packages_command, '--all')
        self.register_command(PackageCommands.ACTIVATE, 'Activate all (or specified) package if installed',self.activate_packages_command, '--all')

    def register_command(self, name, desc, action, *args, **kwargs):
        """TODO: Docstring for register_commands.
        :returns: TODO

        """
        cmd = commands.Command(name)
        act = commands.Action(action)
        cmd._actions.append(act)
        commands.CommandManager.register_command('Packages', name, cmd)
        self.pkg_mgr_commands_map[name] = cmd
        self.cmd_parser.add_command('Package', 'Command for managing packages', name, desc, *args, **kwargs)

    def load_packages_command(self, *args, **kwargs):
        """TODO: Docstring for load_packages_command.
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.LOAD, *args, **kwargs)


    def install_packages_command(self, *args, **kwargs):
        """TODO: Docstring for install_packages_command.
        :arg1: TODO
        :returns: TODO
        """
        if len(args) >= 2:
            cmd = args.pop(0)

    def uninstall_packages_command(self, *args, **kwargs):
        """TODO: Docstring for install_packages_command.
        :arg1: TODO
        :returns: TODO
        """
        if len(args) >= 2:
            cmd = args.pop(0)

    def activate_packages_command(self, *args, **kwargs):
        """TODO: Docstring for activate_packages_command
        :*arg: TODO
        :returns: TODO
        """
        pass
