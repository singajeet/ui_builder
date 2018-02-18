"""
.. module:: generic_manager
   :platform: Unix, Windows
   :synopsis: Resource downloader

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import configparser
from yapsy.PluginManager import PluginManager
from ui_builder.core.service import iplugins
from ui_builder.core import constants

class DownloadManager(object):
    """DownloadManager will be used to download any kind of resource from a \
            source system. DownloadManager will locate all plugins of\
            type :class:`IDownloader` and will provide it back to the\
            requesting object
    """
    __single_download_manager = None

    def __new__(cls, *args, **kwargs):
        """Singleton class constructor
        """
        if cls != type(cls.__single_download_manager):
            cls.__single_download_manager = object.__new__(cls, *args, **kwargs)
        return cls.__single_download_manager

    def __init__(self):
        """Constructor for DownloadManager
        """
        self.plugins_path = constants.DOWNLOADER_PLUGINS_PATH
        self.save_downloads_to = constants.SAVE_DOWNLOADS_TO_PATH
        self.plugin_manager = PluginManager(categories_filter={constants.DOWNLOAD_PLUGIN_FILTER: iplugins.IDownloader})
        self.plugin_manager.setPluginPlaces([self.plugins_path])
        self.plugin_manager.locatePlugins()
        self.plugin_manager.loadPlugins()

    def downloaders_list(self):
        """Provides a list of all downloader plugins available
        """
        return self.plugin_manager.getPluginsOfCategory(constants.DOWNLOAD_PLUGIN_FILTER)

    def get_downloader(self, downloader_name=None):
        """Returns a downloader plugin instance by finding through name
        """
        return self.plugin_manager.getPluginByName(downloader_name, constants.DOWNLOAD_PLUGIN_FILTER)
