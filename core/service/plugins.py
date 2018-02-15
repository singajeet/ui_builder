import os
from ui_builder.core import constants

def load(plugin_type, plugins_path=None):
    """Function to load plugins of given type
    Args:
        plugin_type (type): The base type of plugin that needs to be loaded
        plugin_path (str): Path from where plugin should be loaded (optional)
    """
    plugin_path = plugin_path
    plugins = {}
    for _path in plugin_path:
        if os.path.exists(_path):
            _plugin_files = os.listdir(_path)
            if _plugin_files is not None:
                for _plugin_file in _plugin_files:
                    if os.path.isfile(os.path.join(_path, _plugin_file)):
                        if _plugin_file.endswith(constants.MODULE_FILE_POST_FIX):
                            plugin_name = _plugin_file.rstrip(constants.MODULE_FILE_POST_FIX)
                            plugin = importlib.import_module(plugin_name)
                            for member in dir(plugin):
                                obj = getattr(plugin, member)
                                if inspect.isclass(obj) and issubclass(obj, type(plugin_type)) and obj is not type(plugin_type):
                                    plugins[plugin_name] = obj
    return plugins
