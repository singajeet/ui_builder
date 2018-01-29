##
##
##
from configparser import ConfigParser

class Action(object):

    """Docstring for Action. """

    def __init__(self, func, name=None, owner=None, *args, **kwargs) :
        """TODO: to be defined1. """
        self.id = None
        self.name = None
        self.owner = None
        self._callback = func
        self.args = args
        self.kwargs = kwargs

    def callback():
        doc = "The callback property."
        def fget(self):
            return self._callback
        def fset(self, value):
            if callable(value):
                self._callback = value
            else:
                raise ValueError('Only callable types are allowed')
        def fdel(self):
            del self._callback
        return locals()
    callback = property(**callback())

    def execute(self, args=None):
        """TODO: Docstring for execute.
        :returns: TODO

        """
        if args is not None:
            self.args = args

        if self.callback is None or not callable(self.callback):
            raise ReferenceError('The function reference is not callable')
        else:
            self.callback(self, args, kwargs)

class Event(object):

    """Docstring for Event. """

    def __init__(self, name=None, event_args=None):
        """TODO: to be defined1. """
        self.id = None
        self.name = name
        self.event_args = event_args
        self.subscribers = []

    def add_subscriber(self, subscriber):
        """TODO: Docstring for add_subscriber.
        :returns: TODO

        """
        if subscriber is not None and callable(subscriber):
            self.subscribers.append(subscriber)
        else:
            raise Exception('Invalid subscriber provided')

    def remove_subscriber(self, subscriber):
        """TODO: Docstring for remove_subscriber.
        :returns: TODO

        """
        if subscriber is not None and self.subscribers.__contains__(subscriber):
            self.subscribers.remove(subscriber)

    def fire(self, event_args=None):
        """TODO: Docstring for fire.

        :arg1: TODO
        :returns: TODO

        """
        if event_args is not None:
            self.event_args = event_args

        for subscriber in self.subscribers:
            if isinstance(subscriber, Action):
                subscriber.execute(self.event_args)
            else:
                if callable(subscriber):
                    subscriber(self.event_args)
                else:
                    raise ReferenceError('Not a callable object...{0}'.format(subscriber))

class EventArgs(object):

    """Docstring for EventArgs. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

class Command(object):

    """Docstring for Command. """

    def __init__(self, name=None, args=None, action=None):
        """TODO: to be defined1. """
        self.id = None
        self.name = name #Command name
        self._action = action #Action to be executed
        self._post_callback = None #Will be called after cmd execution
        self._pre_callback = None
        self.args = args #imstance of CommandArgs

        def name():
            doc = "The name property."
            def fget(self):
                return self._name
            def fset(self, value):
                self._name = value
            def fdel(self):
                del self._name
            return locals()
        name = property(**name())

        def action():
            doc = "The action property."
            def fget(self):
                return self._action
            def fset(self, value):
                if callable(value):
                    self._action = value
                else:
                    raise ValueError('Only callable types are allowed')
            def fdel(self):
                del self._action
            return locals()
        action = property(**action())

        def post_callback():
            doc = "The post_callback property."
            def fget(self):
                return self._post_callback
            def fset(self, value):
                if callable(value):
                    self._post_callback = value
                else:
                    raise ValueError('Only callable types are allowed')
            def fdel(self):
                del self._post_callback
            return locals()
        post_callback = property(**post_callback())

        def pre_callback():
            doc = "The pre_callback property."
            def fget(self):
                return self._pre_callback
            def fset(self, value):
                if callable(value):
                    self._pre_callback = value
                else:
                    raise ValueError('Only callable typea are allowed')
            def fdel(self):
                del self._pre_callback
            return locals()
        pre_callback = property(**pre_callback())

        def args():
            doc = "The args property."
            def fget(self):
                return self._args
            def fset(self, value):
                self._args = value
            def fdel(self):
                del self._args
            return locals()
        args = property(**args())

        def do(self, args):
            """TODO: Docstring for do.

            :arg: TODO
            :returns: TODO

            """
            if args is not None:
                self.args = args

            if self.pre_callback is not None:
                self.pre_callback()
            if self.action is not None and isinstance(self.callback, Action):
                self.callback.execute(self.args)
            elif callable(self.callback):
                self.callback(self.args)
            else:
                raise ReferenceError('The reference procided in callback is not callable')

            if self.post_callback is not None:
                self.post_callback()

class CommandManager(object):

    CONFIG_SECTION = 'CommandManager'
    OVERWRITE_COMMAND_MODE = 'overwrite_command_mode'
    """Docstring for CommandManager. """

    def __init__(self, config_path, name=None):
        """TODO: to be defined1. """
        self.id = None
        self._config_path = config_path
        self.name = name
        self.commands = {}
        self._pre_callback = None
        self._post_callback = None
        self._config = ConfigParser()
        self._config.read(config_path)

    def config_path():
        doc = "The config_path property."
        def fget(self):
            return self._config_path
        def fset(self, value):
            if value is not None:
                self._config_path = value
            else:
                    raise ValueError('Value for config path can''t be None')
        def fdel(self):
            del self._config_path
        return locals()
    config_path = property(**config_path())

    def pre_callback():
        doc = "The pre_callback property."
        def fget(self):
            return self._pre_callback
        def fset(self, value):
            self._pre_callback = value
        def fdel(self):
            del self._pre_callback
        return locals()
    pre_callback = property(**pre_callback())

    def register_command(self, name, command):
        """TODO: Docstring for register_command.

        :name: TODO
        :returns: TODO

        """
        if name is not None and command is not None:
            if callable(command) or isinstance(command, Action):
                overwrite_mode = self._config.get(CONFIG_SECTION, OVERWRITE_COMMAND_MODE)
                if self.commands[name] is not None and overwrite_mode == 'on':
                    self.commands[name] = command
                elif self.commands[name] is not None and overwrite_mode != 'on':
                    raise Exception('An command is already registered with same name')
                else:
                    self.commands[name] = command
            else:
                raise Exception('Invalid command provided, only callable type or Action types are allowed')
        else:
            raise ValueError('Both name and command parameters are required')

    def unregister_command(self, name):
        """TODO: Docstring for unregister_command.

        :name: TODO
        :returns: TODO

        """
        if name is not None and self.commands[name] is not None:
            self.commands.pop(name)

    def call(self, name):
        """TODO: Docstring for call.

        :nam: TODO
        :returns: TODO

        """
        if name is not None and self.commands[name] is not None:
            command = self.commands[name]
            if isinstance(command, Command):
                args = command.args
                command.do(args)
            elif callable(command):
                command()
            else:
                raise Exception('The command object for Command is not callable or is not of type Command...{0}'.format(name))
        else:
            raise ValueError('Either name parameter is empty or command is not yet registered')

    def get_command(self, name):
        """TODO: Docstring for get_command.

        :name: TODO
        :returns: TODO

        """
        return self.commands[name] if self.commands[name] is not None else None
