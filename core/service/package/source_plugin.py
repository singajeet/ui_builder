"""
.. module:: source_plugin
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""

#imports ---------------------------------
import logging
from typing import Dict, Any
from tinydb import Query
from ui_builder.core import init_log
from ui_builder.core.service import sessions
from ui_builder.core.service.package import models

#init logs ----------------------------
init_log.config_logs()
LOGGER = logging.getLogger(__name__)

class DefaultPackageSource(models.PackageSource):
    """Represents an package source in package management system
    """

    def __init__(self):
        """DefaultPackageSource constructor
        """
        super(DefaultPackageSource, self).__init__()
        self.__index_table = None
        self.__index_list = None

    def prepare(self, name: str, db_connection: Any) -> None:
        super(DefaultPackageSource, self).prepare(name, db_connection)
        self.__index_table = self.__db_connection.table('PackageIndex')
        self.__index_list = {}
        if self.__index_table is not None:
            self.__index_list = self.\
                    __index_table.get(Query()['Name'] == name)

    async def get_package_index(self) -> Dict[str]:
        """Downloads package index from configured source uri
        Returns:
            package_index (json): Package index dict
        """
        async with sessions.Web()\
                .SESSION.get(self.__details['Uri'], \
                             params={'action': 'index'}) \
                as _response:
            self.__index_list = await _response.json()
            return self.__index_list

    async def get_validity_status(self):
        """Returns the validity of package index such that \
                if count of package index in source and \
                :attr:`__index_list` matches, it returns \
                True else False
        Returns:
            validity_status (bool): Returns True if count \
                    match else False
        """
        async with sessions.Web().SESSION\
                .get(self.__details['Uri'], \
                     params={'action':'count', \
                               'local_index':\
                               len(self.__index_list)}) \
                as _response:
            return await _response.json()

    def get_cached_package_index(self):
        """Returns the current package index which was \
                already downloaded
            in previous requests
        Returns:
            index (dict): Returns an dict of package names, \
                    version and dependencies
        """
        return self.__index_list
