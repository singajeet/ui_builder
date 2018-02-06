"""
.. module:: cmd_parser
   :platform: Unix, Windows
   :synopsis: Register commands and parse command arguments for validity and converting to various dict

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
from ui_builder.core import constants

class CommandTemplate(object):

    """Docstring for TemplateCommand. """

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

    def add_sub_cmd_template(self, sub_cmd):
        """TODO: Docstring for add_sub_cmd_template.

        :sub_cmd: TODO
        :returns: TODO

        """
        #if current cmd is an sub-cmd, don't allow addition of further sub cmds templates
        if self.is_sub_command == True:
            raise Exception('Nested sub-command templates are not allowed')
        #if the sub-cmd passed already have an sub-cmd, do not add template to prevent nested sub-cmd templates
        if sub_cmd is not None and sub_cmd.have_sub_commands == True:
            raise Exception('Nested sub-command templates are not allowed')
        if sub_cmd is not None:
            if isinstance(sub_cmd, CommandTemplate):
                self.sub_commands[sub_cmd.command_name] = sub_cmd
                sub_cmd.is_sub_command = True
                self.have_sub_commands = True
                return sub_cmd
            else:
                raise ValueError('Invalid template type {0}! Only CommandTemplate type are accepted'.format(sub_cmd))
        else:
            raise ValueError('Can''t add an empty template')

    def add_sub_cmd_templates_by_name(self, sub_cmd_dict={}):
        """TODO: Docstring for add_sub_cmd_templates_by_name.
        :returns: TODO

        """
        if len(sub_cmd_dict) > 0:
            for cmd_name in sub_cmd_dict:
                self.add_sub_cmd_template_by_name(cmd_name, None, sub_cmd_dict[cmd_name])
            return self

    def add_sub_cmd_template_by_name(self, sub_cmd_name, desc=None, cmd_valid_vals=['ANY']):
        """TODO: Docstring for add_sub_cmd_template_by_name
        :returns: TODO

        """
        if sub_cmd_name is not None:
            self.sub_commands[sub_cmd_name] = CommandTemplate(sub_cmd_name, desc, cmd_valid_vals)
            (self.sub_commands[sub_cmd_name]).is_sub_command = True
            self.have_sub_commands = True
            return self.sub_commands[sub_cmd_name]
        else:
            raise Exception('Invalid sub-command template name')

    def is_valid_kw_option(self, opt_name, opt_val):
        """TODO: Docstring for is_valid_kw_option.

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

    def error_missing_arguments(self, raise_not_found_err=False):
        """TODO: Docstring for error_missing_arguments.
        :returns: TODO

        """
        err = 'Missing required arguments.\n'\
                'Valid arguments list: {0}'.format(self.command_valid_values)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def error_invalid_arguments(self, raise_not_found_err=False):
        """TODO: Docstring for error_invalid_arguments.
        :returns: TODO

        """
        err = 'Invalid arguments value provided.\n'\
                'Valid arguments list: {0}'.format(self.command_valid_values)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def error_missing_options(self, raise_not_found_err=False):
        """TODO: Docstring for error_missing_arguments.
        :returns: TODO

        """
        err = 'Missing required options.\n'\
                'Valid options list: {0}'.format(self.options)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def error_invalid_options(self, raise_not_found_err=False):
        """TODO: Docstring for error_invalid_options.

        :e: TODO
        :returns: TODO

        """ 
        err = 'Invalid options value provided.\n'\
                'Valid options list: {0}'.format(self.options)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def error_missing_kw_options(self, raise_not_found_err=False):
        """TODO: Docstring for error_missing_kw_options.

        :raise_not_found_err: TODO
        :returns: TODO

        """ 
        err = 'Missing keyword arguments.\n'\
                'Valid keyword arguments list: {0}'.format(self.keyword_options)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def error_invalid_kw_options(self, raise_not_found_err=False):
        """TODO: Docstring for error_invalid_kw_options.

        :raise_not_found_err: TODO
        :returns: TODO

        """ 
        err = 'Invalid keyword arguments provided.\n'\
                'Valid arguments list: {0}'.format(self.keyword_options)
        if raise_not_found_err:
            raise Exception(err)
        else:
            return err

    def get_help(self):
        """TODO: Docstring for get_help.
        :returns: TODO

        """
        help_msg = '{0}\n\n'.format(self.description)
        help_msg += '{0} <{1}>'.format(self.command_name, self.command_valid_values)
        if len(self.options) > 0:
            help_msg += ' [{0}]'.format(self.options)
        if len(self.keyword_options) > 0:
            help_msg += ' [{0}]'.format(self.keyword_options)
        help_msg += '\n\n'
        if self.is_sub_command == False and len(self.sub_commands) > 0:
            help_msg += 'Sub Commands: '
            for sub_cmd in self.sub_commands.keys():
                help_msg += '{0}, '.format(sub_cmd)
            help_msg += '\n\n'
            help_msg += 'For more information on sub-commands, use:\n{0} <Sub-Command> --help'.format(self.command_name)
        return help_msg

    def print_help(self):
        """TODO: Docstring for print_help.
        :returns: TODO

        """
        print(self.get_help())

class ParsedResult(object):
    """Docstring for ParsedResult. """

    def __init__(self, cmd_name, cmd):
        """TODO: to be defined1. """
        self.parsed_cmd_name = cmd_name
        self.parsed_cmd = cmd
        self.is_help_requested = True if len(cmd[CommandParser.PARSED_OPTIONS]) > 0 and cmd[CommandParser.PARSED_OPTIONS].__contains__('--help') else False
        self.help_message = cmd.get_help()
        self.parsed_values = cmd[CommandParser.PARSED_CMD_VALUES]
        self.parsed_options = cmd[CommandParser.PARSED_OPTIONS]
        self.parsed_kw_options = cmd[CommandParser.PARSED_KW_OPTIONS]

class CommandParser(object):

    """Docstring for CommandParser. """

    def __init__(self, raise_not_found_err = False):
        """TODO: to be defined1. """
        self.commands = {}
        self.raise_not_found_error = raise_not_found_err

    def add_cmd_template(self, command_name, desc=None, sub_command=None, sub_desc=None, *opts, **kwopts):
        """TODO: Docstring for add_cmd_template.
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
                        next_val = None
                        if len(opts) > 0:
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
                cmd = CommandTemplate(command_name, desc, values, options, keyword_options)
                cmd_dict = {}
                cmd_dict[INSTANCE] = cmd
                cmd_dict[PARSED_CMD_VALUES] = []
                cmd_dict[PARSED_OPTIONS] = {}
                cmd_dict[PARSED_KW_OPTIONS] = {}
                self.commands[command_name] = cmd_dict
                return cmd
            else:
                cmd = CommandTemplate(command_name, desc)
                cmd_dict = {}
                cmd_sub_dict = {}
                cmd_dict[INSTANCE] = cmd
                cmd_dict[sub_command] = cmd_sub_dict
                sub_cmd = CommandTemplate(sub_command, sub_desc, values, options, keyword_options)
                cmd_sub_dict[INSTANCE] = sub_cmd
                cmd_sub_dict[PARSED_CMD_VALUES] = []
                cmd_sub_dict[PARSED_OPTIONS] = {}
                cmd_sub_dict[PARSED_KW_OPTIONS] = {}
                cmd.add_sub_cmd_template(sub_cmd)
                self.commands[command_name] = cmd_dict
                return cmd

    def parse(self, command, sub_command=None, *args, **kwargs):
        """TODO: Docstring for parse.

        :arg1: TODO
        :returns: TODO

        """
        if command is not None:
            if self.commands.__contains__(command):
                cmd_dict = self.commands[command]
                cmd = cmd_dict[INSTANCE]
                if sub_command is not None and cmd.sub_commands.__contains__(sub_command):
                    cmd = cmd.sub_commands[sub_command]
                    cmd_dict = cmd_dict[sub_command]
                cmd_dict[PARSED_OPTIONS]={}
                cmd_dict[PARSED_KW_OPTIONS] = {}
                cmd_dict[PARSED_CMD_VALUES] = []
                if len(args) > 0:
                    args = list(args)
                    while(len(args) > 0):
                        arg = args.pop(0)
                        if arg.startswith('--'):
                            next_val = None
                            if len(args) > 0:
                                next_val = args[0] if args[0] is not None else None
                            if next_val is None:
                                if cmd.is_valid_option(arg, True):
                                    cmd_dict[PARSED_OPTIONS][arg] = True
                                    continue
                                else:
                                    return cmd.error_invalid_options()
                            if next_val.startswith('--') == False:
                                opt_val = args.pop(0)
                                if cmd.is_valid_option(arg, opt_val):
                                    cmd_dict[PARSED_OPTIONS][arg] = opt_val
                                else:
                                    return cmd.error_invalid_options()
                            else:
                                if cmd.is_valid_option(arg, True):
                                    cmd_dict[PARSED_OPTIONS][arg] = True
                                else:
                                    return cmd.error_invalid_option()
                        else:
                            if cmd.is_valid_value(arg):
                                cmd_dict[PARSED_CMD_VALUES].append(arg)
                            else:
                                return cmd.error_invalid_arguments()
                if len(kwargs) > 0:
                    for kwarg in kwargs:
                        val = kwargs[kwarg]
                        if cmd.is_valid_kw_option(kwarg, val):
                            cmd_dict[PARSED_KW_OPTIONS][kwarg] = val
                        else:
                            return cmd.error_invalid_kw_options()
            else:
                raise Exception('Command not found...{0}'.format(cmd.command_name))
        else:
            raise Exception('Really??.... An empty command!')
        if sub_command is None:
            result = ParsedResult(command, self.commands[command])
            return result
        else:
            result = ParsedResult(sub_command, self.commands[command][sub_command])
            return result

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
            return cmd_dict[PARSED_CMD_VALUES]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            return cmd_dict[PARSED_CMD_VALUES]

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
            cmd_opts = cmd_dict[PARSED_OPTIONS]
            return cmd_opts[opt_name]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            cmd_opts = cmd_dict[PARSED_OPTIONS]
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
            cmd_opts = cmd_dict[PARSED_KW_OPTIONS]
            return cmd_opts[opt_name]
        else:
            cmd_dict = self.commands[cmd]
            cmd_dict = cmd_dict[sub_cmd]
            cmd_opts = cmd_dict[PARSED_KW_OPTIONS]
            return cmd_opts[opt_name]

    def get_current_cmd_keyword_option(self, opt_name):
        """TODO: Docstring for get_current_cmd_option.
        :returns: TODO

        """
        return self.get_keyword_option(self.parsed_cmd, self.parsed_sub_cmd, opt_name)
