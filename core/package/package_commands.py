"""
package_commands.py
Contains commands for performing package related tasks
"""
from ui_builder.core.provider import commands
from ui_builder.core.parser import cmd_parser
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
    DOWNLOAD = 'download'
    FIND = 'find'

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
        self.register_command(PackageCommands.DEACTIVATE, 'Dectivate all (or specified) package if installed',self.deactivate_packages_command, '--all')
        self.register_command(PackageCommands.SHOW, 'Show details about the package passed as argument', self.show_package_command)
        self.register_command(PackageCommands.DOWNLOAD, 'Download package from the configured sources(or a source provided as option with --source) and make it ready for installation', self.download_package_command, '--source')
        self.register_command(PackageCommands.LIST, 'Show list of all packages in all configured sources. List will be displayed as grouped by source', self.list_packages_command)
        self.register_command(PackageCommands.FIND, 'Search the specified package in all configured sources', self.find_package_command)

    def register_command(self, name, desc, action, *args, **kwargs):
        """TODO: Docstring for register_commands.
        :returns: TODO

        """
        cmd = commands.Command(name)
        act = commands.Action(action)
        cmd._actions.append(act)
        commands.CommandManager.register_command('Packages', name, cmd)
        self.pkg_mgr_commands_map[name] = cmd
        self.cmd_parser.add_cmd_template('Package', 'Command for managing packages', name, desc, *args, **kwargs)

    def load_packages_command(self, *args, **kwargs):
        """TODO: Docstring for load_packages_command.
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.LOAD, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        #Case1: when --all option passed to the cmd
        if len(cmd.parsed_options) > 0:
            if cmd.parsed_options.__contains__('--all'):
                self.package_manager.load_packages()
                return 'SUCCESS'
            else:
                return cmd.parsed_cmd.error_invalid_options()
        else:
            cmd.parsed_cmd.error_missing_options()
        #Case2: when no opt passed,only pkg-names passed
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                self.package_manager.load_package(pkg)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def install_packages_command(self, *args, **kwargs):
        """TODO: Docstring for install_packages_command.
        :arg1: TODO
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.INSTALL, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        #Case1: when --all option passed to the cmd
        if len(cmd.parsed_options) > 0:
            if cmd.parsed_options.__contains__('--all'):
                self.package_manager.install_packages()
                return 'SUCCESS'
            else:
                return cmd.parsed_cmd.error_invalid_options()
        else:
            cmd.parsed_cmd.error_missing_options()
        #Case2: when no opt passed,only pkg-names passed
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                self.package_manager.install_package(pkg)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def uninstall_packages_command(self, *args, **kwargs):
        """TODO: Docstring for install_packages_command.
        :arg1: TODO
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.UNINSTALL, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        #Case1: when no opt passed,only pkg-names passed
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                self.package_manager.uninstall_package(pkg)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()
    def activate_packages_command(self, *args, **kwargs):
        """TODO: Docstring for activate_packages_command
        :*arg: TODO
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.ACTIVATE, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        #Case1: when --all option passed to the cmd
        if len(cmd.parsed_options) > 0:
            if cmd.parsed_options.__contains__('--all'):
                self.package_manager.activate_packages()
                return 'SUCCESS'
            else:
                return cmd.parsed_cmd.error_invalid_options()
        else:
            return cmd.parsed_cmd.error_missing_options()
        #Case2: when no opt passed,only pkg-names passed
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                self.package_manager.activate_package(pkg)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def deactivate_packages_command(self, *args, **kwargs):
        """TODO: Docstring for deactivate_packages_command
        :*arg: TODO
        :returns: TODO
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.DEACTIVATE, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        #Case1: when --all option passed to the cmd
        if len(cmd.parsed_options) > 0:
            if cmd.parsed_options.__contains__('--all'):
                self.package_manager.deactivate_packages()
                return 'SUCCESS'
            else:
                return cmd.parsed_cmd.error_invalid_options()
        else:
            return cmd.parsed_cmd.error_missing_options()
        #Case2: when no opt passed,only pkg-names passed
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                self.package_manager.deactivate_package(pkg)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def list_packages_command(self, *args, **kwargs):
        """TODO: Docstring for list_packages_command.

        :*arg: TODO
        :returns: TODO

        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.LIST, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        return self.package_manager.list_packages()

    def show_package_command(self, *args, **kwargs):
        """TODO: Docstring for show_package_command.

        :*arg: TODO
        :returns: TODO

        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.SHOW, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        if len(cmd.parsed_values) > 0:
            if len(cmd.parsed_values) == 1:
                pkg = cmd.parsed_values[0]
                return self.package_manager.show_package(pkg)
            else:
                return cmd.parsed_cmd.error_invalid_arguments()
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def download_package_command(self, *args, **kwargs):
        """TODO: Docstring for download_package_command.

        :*arg: TODO''
        :returns: TODO

        """
        source = None
        cmd = self.cmd_parser.parse('Package', PackageCommands.DOWNLOAD, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        if len(cmd.parsed_option) > 0:
            if cmd.parsed_options.__contains__('--source'):
                source = cmd.parsed_options['--source']
            else:
                cmd.parsed_cmd.error_invalid_options()
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                if source is None:
                    self.package_manager.download_package(pkg)
                else:
                    self.package_manager.download_package(pkg, source)
            return 'SUCCESS'
        else:
            return cmd.parsed_cmd.error_missing_arguments()

    def find_package_command(self, *args, **kwargs):
        """TODO: Docstring for find_package_command.
        :returns: TODO

        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.FIND, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        if len(cmd.parsed_values) > 0:
            for pkg in cmd.parsed_values:
                result = self.package_manager.find_package(pkg)
                if result is not None:
                    return result
            return 'NOT_FOUND'
        else:
            return cmd.parsed_cmd.error_missing_arguments()
