"""
Classes related to features
"""
from pluginbase import PluginBase

class FeaturesManager(object):

    """Docstring for FeaturesManager. """

    def __init__(self, features_source_path):
        """TODO: to be defined1. """
        self._feature_source_path = feature_source_path
        self._plugin_base = PluginBase(package='ui.controls.plugins')
        self._feature_source = self._plugin_base.make_plugin_source(searchpath=self._feature_source_path)

    def feature_source_path():
        doc = "The feature_source_path property."
        def fget(self):
            return self._feature_source_path
        def fset(self, value):
            self._feature_source_path = value
        def fdel(self):
            del self._feature_source_path
        return locals()
    feature_source_path = property(**feature_source_path())

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

    def feature_source():
        doc = "The feature_source property."
        def fget(self):
            return self._feature_source
        def fset(self, value):
            self._feature_source = value
        def fdel(self):
            del self._feature_source
        return locals()
    feature_source = property(**feature_source())

    def get_features(self):
        """TODO: Docstring for get_features.
        :returns: TODO

        """
        return self.plugin_source.list_plugins()

    def get_feature(self, feature_name):
        """TODO: Docstring for get_feature.

        :feature_name: TODO
        :returns: TODO

        """
        return self.plugin_source.load_plugin(feature_name)

