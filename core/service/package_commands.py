"""
.. module:: package_commands
   :platform: Unix, Windows
   :synopsis: Contains commands for performing package related tasks

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""


from ui_builder.core.provider import commands
from ui_builder.core.parser import cmd_parser

class PackageCommands(object):
    """PackageCommands extends the functionality of the Commands available. It supports the various functions of package system through :class:`Commands` interface. These commands can be invoked from Command Line, Gui, etc with help of :class:`CommandManager` """
    """
    .. attribute: Command types
    """

    INSTALL = 'install' #:attr:`Install`
    UNINSTALL = 'uninstall'
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    LIST = 'list'
    SHOW = 'show'
    LOAD = 'load'
    DOWNLOAD = 'download'
    FIND = 'find'

    def __init__(self, pkg_manager):
        """PackageCommands class needs an instance of :class:`PackageManager` to further work with packages in the system
        Args:
            package_manager (PackageManager): An instance of :class:`PackageManager`
        """
        self.package_manager = pkg_manager
        self.pkg_mgr_commands_map = {}
        self.cmd_parser = cmd_parser.CommandParser()

    def register_commands(self):
        """registers all the packages related commands with :class:`PackageManager` and :class:`CommandParser`
        Args:
            None
        Returns:
            None
        """
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
        """Register command with the :class:`CommandManager` and :class:`CommandParser`

        Args:
            name (str): Name of the command to register
            desc (str): Description about the xommand
            action (Action): Instance of :class:`Action` class or any callable object which will be called back by this command
            args (object): Arguments that needs to be passed to commands callback method

        Kwargs:
            kwargs (object):Keyword arguments that will be passed to callback object

        Returns:
            None

        Examples:


        """
        cmd = commands.Command(name)
        act = commands.Action(action)
        cmd._actions.append(act)
        commands.CommandManager.register_command('Packages', name, cmd)
        self.pkg_mgr_commands_map[name] = cmd
        self.cmd_parser.add_cmd_template('Package', 'Command for managing packages', name, desc, *args, **kwargs)

    def load_packages_command(self, *args, **kwargs):
        """TODO: Docstring for load_packages_command.
        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
        """
        cmd = self.cmd_parser.parse('Package', PackageCommands.LIST, *args, **kwargs)
        #if help is requested
        if cmd.is_help_requested:
            return cmd.help_message
        return self.package_manager.list_packages()

    def show_package_command(self, *args, **kwargs):
        """TODO: Docstring for show_package_command

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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

        Args:
            args (objects): callback parameters

        Kwargs:
            kwars (object): callback keyword parameters

        Returns:
            None
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
