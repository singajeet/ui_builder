"""
.. module:: iplugins
   :platform: Unix, Windows
   :synopsis: Contains interfaces to all plugins

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
from typing import Type, Any
from pathlib import Path
import yapsy
from tinydb import Query
from ui_builder.core import constants

class ISource(yapsy.IPlugin):
    """Interface for an source system"""

    def __init__(self):
        """Constructor of ISource should not have any arguments
        """
        self.__name = None
        self.__details = {}
        self.__db_connection = None
        self.__source_table = None

    @property
    def name(self):
        """Name property of source
        """
        return self._name

    @property
    def details(self):
        """Details property of source
        """
        return self._details

    def prepare(self, name: str, db_connection:Any) -> None:
        """Prepare the source object to perform further actions
        Args:
            name (str): Unique name of source system
            db_connection (object): An open connection to database
        """
        if name is None or db_connection is None:
            raise ValueError('Both name and db connection args are mandatory')
        self.__name = name
        self.__db_connection = db_connection
        self.__source_table = db_connection.table('Source')
        self.__details = self.__source_table.get(Query()['name'] == name)
        self.__is_new = False
        if len(self.__details) <= 0:
            self.__is_new = True
        elif len(self.__details) > 1:
            raise LookupError('Inconsistent source table. There should be only one record for a given source. Number of records found: %s' % len(self.__details))

    def update_details(self, uri:str=None, username:str=None, password:str=None, source_type:str=None, modified_on:str=None, modified_by:str=None, security_id:str=None) -> (bool, str):
        """Update current sources attribute with new value
        Args:
            uri (str): A web path or file system path to the source index
            username (str): Username to access source
            password (str): Password for accessing source
            src_type (str): Web or Filesystem
            modified_on: Modified on date time
            modified_by: Name of user who havemodified it
            security_id (uuid): Id of security principle
        Returns:
            status (bool): True or False
            message (str): Failure reasons
        """
        if uri is not None:
            self.__details['Uri'] = uri
        if username is not None:
            self.__details['Username'] = username
        if password is not None:
            self.__details['Password'] = password
        if source_type is not None:
            self.__details['Source_Type'] = source_type
        if modified_on is not None:
            self.__details['Modified_On'] = modified_on
        if modified_by is not None:
            self.__details['Modified_By'] = modified_by
        if security_id is not None:
            self.__details['Security_Id'] = security_id
        record_count = 0
        if not self.__is_new:
            record_count = self.__source_table.update(self.__details, Query()['name'] == self.name)
        if record_count > 0:
            return (True, '%d record(s) updated' % record_count)
        return (False, 'Unable to update details in db. If it is a new record, please save it first')

    def save(self) -> (bool, str):
        """Creates a new source record and saves it in database
        """
        src_count = self.__source_table.count(Query()['Name'] == self.name)
        if src_count <= 0:
            _result = self.__source_table.insert(self.__details)
        else:
            return (False, 'A source with same name already exists - %s' % self.name)
        if len(_result) > 0:
            return (True, _result)
        else:
            return (False, 'Unable to create new source record')

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
