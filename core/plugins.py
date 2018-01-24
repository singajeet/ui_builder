"""
Classes related to plugins
"""
from pluginbase import PluginBase

class PluginManager(object):

    """Docstring for PluginManager. """

    def __init__(self, plugin_source_path):
        """TODO: to be defined1. """
        self._plugin_source_path = plugin_source_path
        self._plugin_base = PluginBase(package='ui.controls.plugins')
        self._plugin_source = self._plugin_base.make_plugin_source(searchpath=self._plugin_source_path)

    def plugin_source_path():
        doc = "The plugin_source_path property."
        def fget(self):
            return self._plugin_source_path
        def fset(self, value):
            self._plugin_source_path = value
        def fdel(self):
            del self._plugin_source_path
        return locals()
    plugin_source_path = property(**plugin_source_path())

    def plugin_base():
        doc = "The plugin_base property."
        def fget(self):
            return self._plugin_base
        def fset(self, value):
            self._plugin_base = value
        def fdel(self):
            del self._plugin_base
        return locals()
    plugin_base = property(**plugin_base())

    def plugin_source():
        doc = "The plugin_source property."
        def fget(self):
            return self._plugin_source
        def fset(self, value):
            self._plugin_source = value
        def fdel(self):
            del self._plugin_source
        return locals()
    plugin_source = property(**plugin_source())

    def get_plugins(self):
        """TODO: Docstring for get_plugins.
        :returns: TODO

        """
        return self.plugin_source.list_plugins()

    def get_plugin(self, plugin_name):
        """TODO: Docstring for get_plugin.

        :plugin_name: TODO
        :returns: TODO

        """
        return self.plugin_source.load_plugin(plugin_name)

