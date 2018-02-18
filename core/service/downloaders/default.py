"""
.. module:: downloader
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""

#imports ---------------------------------
import logging
import pathlib
import aiohttp
from ui_builder.core import utils, init_log, constants
from ui_builder.core.service import iplugins
from ui_builder.core.service import sessions


#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)


class Downloader(iplugins.IDownloader):
    """Docstring for PackageDownloader. """

    __single_downloader = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single__downloader):
            cls.__single_downloader = object.__new__(cls, *args, **kwargs)
        return cls.__single_downloader

    def __init__(self):
        pass

    async def download(self, source, resource_name):
        """Downloads the package from source and returns the content to \
                caller of this coroutine
        Args:
            resource_name (str): Name of the package that needs to be downloaded
        """
        async with sessions.Web()\
                .SESSION.get(source.details['Uri'], \
                             params={'resource_name' : resource_name, \
                                     'action':'download'}) as _response:
            with open('{0}/{1}.pkg'\
                      .format(self.__download_location, resource_name), \
                      'wb') as fd:
                while True:
                    chunk = _response.content.read(self.__chunk_size)
                    if not chunk:
                        break
                    fd.write(chunk)
            return pathlib.Path('{0}/{1}.pkg'.format(self.__download_location, \
                                                     resource_name))
        return None
