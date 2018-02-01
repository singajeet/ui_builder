"""
package_commands.py
Contains commands for performing package related tasks
"""
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

    def register_commands(self):
        self.register_command(INSTALL, self.install_packages_command)
        self.register_command(UNINSTALL, self.uninstall_packages_command)
        self.register_command(LOAD, self.load_packages_command)

    def register_command(self, name, action):
        """TODO: Docstring for register_commands.
        :returns: TODO

        """
        cmd = commands.Command(name)
        act = commands.Action(action)
        cmd._actions.append(act)
        commands.CommandManager.register_command('Packages', name, cmd)
        self.pkg_mgr_commands_map[name] = cmd

    def load_packages_command(self, *args, **kwargs):
        """TODO: Docstring for load_packages_command.
        :returns: TODO
        """
        if len(args) >= 2:
            cmd = args.pop(0)
            if cmd.upper() == 'LOAD':
                param = args.pop(0)
                if param.upper() == '--ALL':
                    self._load_packages()
                elif param.upper() == 'PACKAGE':
                    pkg_name = args.pop(0)
                    if pkg_name is not None:
                        self._load_package(pkg_name)
                        return (commands.Commands.SUCCESS, 'Package loaded', None)
                    else:
                        return (commands.Commands.SUCCESS_WARNING, 'Package not found!', None)
                else:
                    return (commands.Commands.INVALID_SUB_COMMAND_OPTION, 'Invalid option provided - {0}'.format(param), 'Valid options are --all, package <package_name>')
            else:
                return (commands.Commands.INVALID_SUB_COMMAND, 'Invalid sub-command provided', None)

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
