"""
.. module:: iplugins
   :platform: Unix, Windows
   :synopsis: Contains interfaces to all plugins

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
from typing import Type
from pathlib import Path
import yapsy

class ISource(yapsy.IPlugin):
    """Interface for an source system"""

    def __init__(self):
        """Constructor of ISource should not have any arguments
        """
        self._name = None
        self._details = {}

    @property
    def name(self):
        """Name property of source
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def details(self):
        """Details property of source
        """
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

class IDownloader(yapsy.IPlugin):
    """Interface for all downloaders
    """

    def __init__(self):
        """Constructor definition of an plugin. 
        Note:: A plugin should not have an argument in its constructor
        """
        self._source = None
        self._config = None
        self._resource_drop_in_path = None

    @property
    def source(self):
        """source property of downloader
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def resource_drop_in_path(self):
        """Path to the location where downloaded resources should be saved
        """
        return self._resource_drop_in_path

    @resource_drop_in_path.setter
    def resource_drop_in_path(self, value):
        self._resource_drop_in_path = value

    @property
    def config(self):
        """Configuration for the downloader
        """
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    async def download(self, source: Type[ISource], resource_name: str) -> Type[Path]:
        """Download method downloads the resource from the source \
                passed as argument
        Args:
            source (ISource): should be an instance of :class:`ISource' \
                    containing details about source system
            resource_name: name of resource that needs to be downloaded
        Returns:
            downloaded_file (Path): an instance of :class:`Path` having \
                    details of downloaded file''s path
        """
        pass
