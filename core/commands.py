##
##
##
from configparser import ConfigParser

class Action(object):

    """Docstring for Action. """

    def __init__(self, func, name=None, owner=None):
        """TODO: to be defined1. """
        self.id = None
        self.name = None
        self.owner = None
        self._callback = func

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

    def execute(self, *args, **kwargs):
        """TODO: Docstring for execute.
        :returns: TODO

        """
        if self.callback is None or not callable(self.callback):
            raise ReferenceError('The function reference is not callable')
        else:
            self.callback(args, kwargs)

class Event(object):

    """Docstring for Event. """

    def __init__(self, name=None):
        """TODO: to be defined1. """
        self.id = None
        self.name = name
        self.event_args = None
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

    def fire(self, source, *args, **kwargs):
        """TODO: Docstring for fire.

        :arg1: TODO
        :returns: TODO

        """
        for subscriber in self.subscribers:
            if isinstance(subscriber, Action):
                subscriber.execute(source, args, kwargs)
            else:
                if callable(subscriber):
                    subscriber(source, args, kwargs)
                else:
                    raise ReferenceError('Not a callable object...{0}'.format(subscriber))

class EventArgs(object):

    """Docstring for EventArgs. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

class Command(object):

    """Docstring for Command. """

    def __init__(self, name=None):
        """TODO: to be defined1. """
        self.id = None
        self.name = name #Command name
        self._actions = [] #Actions to be executed
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

        def actions():
            doc = "The action property."
            def fget(self):
                return self._actions
            def fset(self, value):
                self._actions = value
            def fdel(self):
                del self._actions
            return locals()
        actions = property(**actions())

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

        def add_action(self, action_obj):
            """TODO: Docstring for add_action.
            :returns: TODO

            """
            if action_obj is not None and (isinstance(action_obj, Action) or callable(action_obj)):
                self.actions.append(action_obj)
            else:
                raise ValueError('Provided argument is not an callable or Action type')

        def remove_action(self, action_obj):
            """TODO: Docstring for remove_action.
            :returns: TODO

            """
            if action_obj is not None and self.actions.__contains__(action_obj):
                self.actions.remove(action_obj)

        def do(self, *args, **kwargs):
            """TODO: Docstring for do.

            :arg: TODO
            :returns: TODO

            """
            if self.pre_callback is not None:
                self.pre_callback()
            if self.actions is not None:
                for act in self.actions:
                    if isinstance(act, Action):
                        act.execute(args, kwargs)
                    elif callable(act):
                        act(args, kwargs)
                    else:
                        raise ReferenceError('The reference procided in Action is not callable')
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
        self.namespace_commands = {}
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

    def post_callback():
        doc = "The post_callback property."
        def fget(self):
            return self._post_callback
        def fset(self, value):
            self._post_callback = value
        def fdel(self):
            del self._post_callback
        return locals()
    post_callback = property(**post_callback())

    def register_namespace(self, namespace):
        """TODO: Docstring for register_namespace.

        :namespace: TODO
        :returns: TODO

        """
        if namespace is not None:
            if self.namespace_commands.__contains__(namespace):
                raise Exception('Command namespace is already registered...{0}'.format(namespace))
            else:
                self.namespace_commands[namespace]={}
        else:
            raise ValueError('Namespace argument value can''t be empty')

    def unregister_namespace(self, namespace):
        """TODO: Docstring for unregister_namespace.
        :returns: TODO

        """
        if namespace is not None:
            if self.namespace_commands.__contains__(namespace):
                self.namespace_commands.pop(namespace)

    def register_command(self, namespace, name, command):
        """TODO: Docstring for register_command.

        :name: TODO
        :returns: TODO

        """
        if namespace is not None and name is not None and command is not None:
            if self.namespace_commands.__contains__(namespace) == False:
                raise Exception('Provided namespace is not registered yet...{0}'.format(namespace))
            if callable(command) or isinstance(command, Action):
                overwrite_mode = self._config.get(CONFIG_SECTION, OVERWRITE_COMMAND_MODE)
                commands = self.namespace_commands[namespace]
                if commands[name] is not None and overwrite_mode == 'on':
                    commands[name] = command
                elif commands[name] is not None and overwrite_mode != 'on':
                    raise Exception('An command is already registered with same name')
                else:
                    commands[name] = command
            else:
                raise Exception('Invalid command provided, only callable type or Action types are allowed')
        else:
            raise ValueError('Both name and command parameters are required')

    def unregister_command(self, namespace, name):
        """TODO: Docstring for unregister_command.

        :name: TODO
        :returns: TODO

        """
        if name is not None and nameapace is not None:
            if self.namespace_commands.__contains__(namespace):
                commands = self.namespace_commands[namespace]
                if commands[name] is not None:
                    commands.pop(name)

    def call(self, namespace, name, *args, **kwargs):
        """TODO: Docstring for call.

        :nam: TODO
        :returns: TODO

        """
        if name is not None and namespace is not None:
            if self.namespace_commands.__contains__(namespace):
                commands = self.namespace_commands[namespace]
                if commands[name] is not None:
                    command = self.commands[name]
                    if isinstance(command, Command):
                        command.do(args, kwargs)
                    elif callable(command):
                        command(args, kwargs)
                    else:
                        raise Exception('The command object for Command is not callable or is not of type Command...{0}'.format(name))
                else:
                    raise Exception('Command [{0}] not found in namespace... [{1}]'.format(name, namespace))
            else:
                raise Exception('Namespace [{0}] is not registered yet'.format(namespace))
        else:
            raise ValueError('Either name parameter is empty or command is not yet registered')

    def get_command(self, namespace, name):
        """TODO: Docstring for get_command.

        :name: TODO
        :returns: TODO

        """
        commands = self.namespace_commands[namespace]
        return commands[name] if commands[name] is not None else None

class Commands(object):

    """Docstring for Commands. """

    SUCCESS = 0
    FAILED = 1
    SUCCESS_WARNING = 2
    WARNING = 4
    INVALID_COMMAND_OPTION = 8
    INVALID_COMMAND = 16
    INVALID_SUB_COMMAND_OPTION = 32
    INVALID_SUB_COMMAND = 64

    def __init__(self):
        """TODO: to be defined1. """
        pass

