

class Command(object):

    """Docstring for Command. """

    def __init__(self, cmd_name, desc=None, cmd_valid_vals=['ANY'], opts={}, keyword_opts={}):
        """TODO: to be defined1. """
        self.command_name = cmd_name
        self.description = desc
        self.sub_commands = {}
        self.options = {}
        self.keyword_options = {}
        self.is_sub_command = False
        self.have_sub_commands = False
        if len(cmd_valid_vals) > 0:
            self._command_valid_values = cmd_valid_vals
        else:
            self._command_valid_values = ['ANY']
        if len(opts) > 0:
            for opt_name in opts:
                self.add_option(opt_name, opts[opt_name])
        if len(keyword_opts) > 0:
            for key_opt_name in keyword_opts:
                self.add_keyword_option(key_opt_name, keyword_opts[key_opt_name])


    def command_valid_values():
        doc = "The command_valid_values property."
        def fget(self):
            return self._command_valid_values
        def fset(self, value):
            self._command_valid_values = value
        def fdel(self):
            del self._command_valid_values
        return locals()
    command_valid_values = property(**command_valid_values())

    def add_sub_command(self, sub_cmd):
        """TODO: Docstring for add_sub_command.

        :sub_cmd: TODO
        :returns: TODO

        """
        #if current cmd is an sub-cmd, don't allow addition further sub cmds
        if self.is_sub_command == True:
            raise Exception('Nested sub-commands are not allowed')
        #if the sub-cmd passed already have an sub-cmd, do not add to prevent nested sub-cmds
        if sub_cmd is not None and sub_cmd.have_sub_commands == True:
            raise Exception('Nested sub-commands are not allowed')
        if sub_cmd is not None:
            if isinstance(sub_cmd, Command):
                self.sub_commands[sub_cmd.command_name] = sub_cmd
                sub_cmd.is_sub_command = True
                self.have_sub_commands = True
                return sub_cmd
            else:
                raise ValueError('Invalid command type {0}! Only Command type are accepted'.format(sub_cmd))
        else:
            raise ValueError('Can''t add an empty command')

    def add_sub_commands_by_name(self, sub_cmd_dict={}):
        """TODO: Docstring for add_sub_commands_by_name.
        :returns: TODO

        """
        if len(sub_cmd_dict) > 0:
            for cmd_name in sub_cmd_dict:
                self.add_sub_command_by_name(cmd_name, None, sub_cmd_dict[cmd_name])
            return self

    def add_sub_command_by_name(self, sub_cmd_name, desc=None, cmd_valid_vals=['ANY']):
        """TODO: Docstring for add_sub_command.
        :returns: TODO

        """
        if sub_cmd_name is not None:
            self.sub_commands[sub_cmd_name] = Command(sub_cmd_name, desc, cmd_valid_vals)
            (self.sub_commands[sub_cmd_name]).is_sub_command = True
            self.have_sub_commands = True
            return self.sub_commands[sub_cmd_name]
        else:
            raise Exception('Invalid sub-command name')

    def is_valid_kw_option(self, opt_name, opt_val):
        """TODO: Docstring for is_valid_.

        :arg1: TODO
        :returns: TODO

        """
        if opt_name is None:
            return False
        if len(self.keyword_options) == 0:
            return False
        if self.keyword_options.__contains__(opt_name):
            valid_vals = self.keyword_options[opt_name]
            if valid_vals.__contains__(opt_val):
                return True
            else:
                return False
        else:
            return False

    def is_valid_option(self, opt_name, opt_val):
        """TODO: Docstring for is_valid_option.

        :arg1: TODO
        :returns: TODO

        """
        if opt_name is None:
            return False
        if len(self.options) == 0:
            return False
        if self.options.__contains__(opt_name):
            if opt_val == True or opt_val == False:
                return True
            valid_opts = self.options[opt_name]
            if valid_opts.__contains__(opt_val):
                return True
            else:
                return False
        else:
            return False

    def is_valid_value(self, arg):
        """TODO: Docstring for is_valid_value.

        :arg: TODO
        :returns: TODO

        """
        if arg is None:
            return False
        #if no valid value list is maintained
        if len(self.command_valid_values) == 0:
            #treat all values as valid
            return True
        elif len(self.command_valid_values) == 1 and self.command_valid_values[0] == 'ANY':
            return True
        elif self.command_valid_values.__contains__(arg):
            return True
        else:
            return False

    def add_option(self, option_name, opt_valid_vals=['ANY']):
        """TODO: Docstring for add_options.

        :arg1: TODO
        :returns: TODO

        """
        if option_name is not None:
            if option_name.startswith('--'):
                if isinstance(opt_valid_vals, bool):
                    self.options[option_name] = opt_valid_vals
                else:
                    self.options[option_name] = opt_valid_vals if len(opt_valid_vals) > 0 else ['ANY']
                return self
            else:
                raise Exception('Option should start with "--" characters')
        else:
            raise Exception('Invalid option name')

    def add_keyword_option(self, keyword_opt_name, valid_vals=['ANY']):
        """TODO: Docstring for add_keyword_option.

        :keyword_opt_name: TODO
        :returns: TODO

        """
        if keyword_opt_name is not None:
            self.keyword_options[keyword_opt_name] = valid_vals if len(valid_vals) > 0 else ['ANY']

class CommandParser(object):

    """Docstring for CommandParser. """

    INSTANCE = 'instance'
    PARSED_CMD_VALUES = 'parsed_cmd_values'
    PARSED_OPTIONS = 'parsed_options'
    PARSED_KW_OPTIONS = 'parsed_kw_options'

    def __init__(self, raise_not_found_err = False):
        """TODO: to be defined1. """
        self.commands = {}
        self.parsed_cmd = None
        self.parsed_sub_cmd = None
        self.raise_not_found_error = raise_not_found_err

    def add_command(self, command_name, desc=None, sub_command=None, sub_desc=None, *opts, **kwopts):
        """TODO: Docstring for add_command.
        :returns: TODO

        """
        if command_name is not None:
            options = {}
            keyword_options = {}
            values = []
            if len(opts) > 0:
                opts = list(opts)
                while(len(opts) > 0):
                    #get the first option
                    opt = opts.pop(0)
                    #if it starts with "--"
                    if opt.startswith('--'):
                        #check whether next arg is an option or val for current opt
                        next_val = opts[0] if opts[0] is not None else None
                        if next_val is None:
                            options[opt] = True
                            continue
                        if next_val.startswith('--') == False:
                            options[opt] = opts.pop(0)
                        else:
                            options[opt] = True
                    else:
                        values.append(opt)
            if len(kwopts) > 0:
                for arg in kwopts:
                    keyword_options[arg] = kwopts[arg]
            if sub_command is None:
                cmd = Command(command_name, desc, values, options, keyword_options)
                cmd_dict = {}
                cmd_dict[CommandParser.INSTANCE] = cmd
                cmd_dict[CommandParser.PARSED_CMD_VALUES] = []
                cmd_dict[CommandParser.PARSED_OPTIONS] = {}
                cmd_dict[CommandParser.PARSED_KW_OPTIONS] = {}
                self.commands[command_name] = cmd_dict
                return cmd
            else:
                cmd = Command(command_name, desc)
                cmd_dict = {}
                cmd_sub_dict = {}
                cmd_dict[CommandParser.INSTANCE] = cmd
                cmd_dict[sub_command] = cmd_sub_dict
                sub_cmd = Command(sub_command, sub_desc, values, options, keyword_options)
                cmd_sub_dict[CommandParser.INSTANCE] = sub_cmd
                cmd_sub_dict[CommandParser.PARSED_CMD_VALUES] = []
                cmd_sub_dict[CommandParser.PARSED_OPTIONS] = {}
                cmd_sub_dict[CommandParser.PARSED_KW_OPTIONS] = {}
                cmd.add_sub_command(sub_cmd)
                self.commands[command_name] = cmd_dict
                return cmd

    def parse(self, command, sub_command=None, *args, **kwargs):
        """TODO: Docstring for parse.

        :arg1: TODO
        :returns: TODO

        """
        if command is not None:
            self.parsed_cmd = command
            self.parsed_sub_cmd = sub_command
            if self.commands.__contains__(command):
                cmd_dict = self.commands[command]
                cmd = cmd_dict[CommandParser.INSTANCE]
                if sub_command is not None and cmd.sub_commands.__contains__(sub_command):
                    cmd = cmd.sub_commands[sub_command]
                    cmd_dict = cmd_dict[sub_command]
                if len(args) > 0:
                    args = list(args)
                    while(len(args) > 0):
                        arg = args.pop(0)
                        if arg.startswith('--'):
                            next_val = args[0] if args[0] is not None else None
                            if next_val is None:
                                if cmd.is_valid_option(arg, True):
                                    cmd_dict[CommandParser.PARSED_OPTIONS][arg] = True
                                    continue
                                else:
                                    return self.return_or_raise(arg=arg)
                            if next_val.startswith('--') == False:
                                opt_val = args.pop(0)
                                if cmd.is_valid_option(arg, opt_val):
                                    cmd_dict[CommandParser.PARSED_OPTIONS][arg] = opt_val
                                else:
                                    return self.return_or_raise(msg='Invalid value provided for option {0}'.format(arg), arg=opt_val)
                            else:
                                if cmd.is_valid_option(arg, True):
                                    cmd_dict[CommandParser.PARSED_OPTIONS][arg] = True
                                else:
                                    return self.return_or_raise(arg=arg)
                        else:
                            if cmd.is_valid_value(arg):
                                cmd_dict[CommandParser.PARSED_CMD_VALUES].append(arg)
                            else:
                                return self.return_or_raise(arg=arg)
                if len(kwargs) > 0:
                    for kwarg in kwargs:
                        val = kwargs[kwarg]
                        if cmd.is_valid_kw_option(kwarg, val):
                            cmd_dict[CommandParser.PARSED_KW_OPTIONS][kwarg] = val
                        else:
                            return self.return_or_raise(msg='Either key is invalid or value for key [{0}] is not valid'.format(kwarg), arg=val)
            else:
                return self.return_or_raise(msg='Command not found', arg=command)
        else:
            return self.return_or_raise(msg='Command can''t be empty')

    def return_or_raise(self, valid=False, msg='Invalid argument provided', arg=None):
        """TODO: Docstring for return_or_raise.
        :returns: TODO

        """
        if self.raise_not_found_error:
            arg_name = arg if arg is not None else ''
            raise Exception('{0}...{1}'.format(msg, arg_name))
        else:
            return valid

    def get_cmd_values(self, cmd, sub_cmd):
        """TODO: Docstring for get_cmd_values.
        :returns: TODO

        """
        if sub_cmd is None:
            cmd_dict = self.commands[cmd]
            return cmd_dict[CommandParser.PARSED_CMD_VALUES]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            return cmd_dict[CommandParser.PARSED_CMD_VALUES]

    def get_current_cmd_values(self):
        """TODO: Docstring for get_cmd_va.

        :arg1: TODO
        :returns: TODO

        """
        return self.get_cmd_values(self.parsed_cmd, self.parsed_sub_cmd)

    def get_option(self, cmd, sub_cmd, opt_name):
        """TODO: Docstring for get_option.
        :returns: TODO

        """
        if sub_cmd is None:
            cmd_dict = self.commands[cmd]
            cmd_opts = cmd_dict[CommandParser.PARSED_OPTIONS]
            return cmd_opts[opt_name]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            cmd_opts = cmd_dict[CommandParser.PARSED_OPTIONS]
            return cmd_opts[opt_name]

    def get_current_cmd_option(self, opt_name):
        """TODO: Docstring for get_current_cmd_option.
        :returns: TODO

        """
        return self.get_option(self.parsed_cmd, self.parsed_sub_cmd, opt_name)

    def get_keyword_option(self, cmd, sub_cmd, opt_name):
        """TODO: Docstring for get_option.
        :returns: TODO

        """
        if sub_cmd is None:
            cmd_dict = self.commands[cmd]
            cmd_opts = cmd_dict[CommandParser.PARSED_KW_OPTIONS]
            return cmd_opts[opt_name]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            cmd_opts = cmd_dict[CommandParser.PARSED_KW_OPTIONS]
            return cmd_opts[opt_name]

    def get_current_cmd_keyword_option(self, opt_name):
        """TODO: Docstring for get_current_cmd_option.
        :returns: TODO

        """
        return self.get_keyword_option(self.parsed_cmd, self.parsed_sub_cmd, opt_name)
