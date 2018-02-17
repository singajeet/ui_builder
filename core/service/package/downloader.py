"""
.. module:: downloader
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""

#imports ---------------------------------
import configparser
import uuid
import os
import zipfile
import logging
import shutil
import glob
import pathlib
import warnings
import aiohttp
from goldfinch import validFileName
from tinydb import TinyDB, Query, where
from ui_builder.core.service import package_commands, components, plugins
from ui_builder.core.io import filesystem
from ui_builder.core.provider import tasks
from ui_builder.core import utils, init_log, constants

#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)


class Downloader(object):
    """Base class for downloader. \
            All downloaders should inherit from this class 
    """

    def __init__(self):
        """Default constructor for an downloader
        """
        pass

    async def download_package(self, source, package_name):
        """docstring for download_package"""
        pass

class PackageDownloader(object):
    """Docstring for PackageDownloader. """

    __single_package_downloader = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_package_downloader):
            cls.__single_package_downloader = object.__new__(cls, *args, **kwargs)
        return cls.__single_package_downloader

    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(conf_path, constants.CONF_FILE_NAME))
        self.download_src_modules_paths = self.config.get(constants.PACKAGE_DOWNLOADER, constants.DOWNLOAD_SOURCE_HANDLERS)
        self.pkg_drop_in_loc = os.path.abspath(self.config.get(constants.PACKAGE_INSTALLER, constants.PKG_DROP_IN_LOC))
        self.download_src = plugins.load(Downloader, self.download_src_modules_paths)

    async def download(self, source, package_name):
        """docstring for download"""
        if self.download_src is None or len(self.download_src) == 0 or not self.download_src.__contains__(source.name):
            return await self.download_package(source, package_name)
        else:
            _downloader_type = self.download_src[source.name]
            _downloader = _downloader_type()
            return await _downloader.download_package(source, package_name)

    async def download_package(self, source, package_name):
        """Downloads the package from source and returns the content to caller of this coroutine
        Args:
            package_name (str): Name of the package that needs to be downloaded
        """
        async with PackageSource.SESSION.get(source.details['Uri'], params={'package_name' : package_name, 'action':'download'}) as _response:
            with open('{0}/{1}.pkg'.format(self.__download_location, package_name), 'wb') as fd:
                while True:
                    chunk = _response.content.read(self.__chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)
            return pathlib.Path('{0}/{1}.pkg'.format(self.__download_location, package_name))
        return None
