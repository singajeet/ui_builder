"""
.. module:: package
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""

#imports ---------------------------------
import configparser
import os
import logging
import shutil
import glob
import pathlib
from tinydb import TinyDB, Query, where
from ui_builder.core import utils, init_log, constants
from ui_builder.core.service import sessions

#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)


class PackageInfo(object):
    """:class:`PackageInfo` class contains information about a package in the \
            Package Managment System. A package consist of one or more components \
            grouped logically together. If there is an dependency between components \
            and other packages, same will be defined in this class
    """

    def __init__(self, config_file_path=None):
        """:class:`PackageInfo` class have one required parameter

        Args:
            config_file_path (str): Location of the package on the local file system \
                    where package is installed
        """
        if config_file_path is not None:
            config_file_path = pathlib.Path(config_file_path).absolute() \
                    if config_file_path.find('~') < 0 \
                    else pathlib.Path(config_file_path).expanduser()
        else:
            raise Exception('Path to config file can''t be none')
        self.package_id = None
        self._location = config_file_path.parent
        self._config_file = config_file_path
        self.name = None
        self.description = None
        self.type = None
        self.author = None
        self.url = None
        self.company = None
        self.version = None
        self._is_enabled = True
        self._is_installed = False
        self.__comp_name_list = []
        self.__comp_name_id_map = {}
        self.__components = {}
        self.package_dependencies = {}
        self.__db_connection = None

    @property
    def config_file(self):
        """Location and name of config file which will be used during installation \
                of the package
        """
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        self._config_file = value

    @property
    def location(self):
        """The location on file system where this package is installed \
                or will be installed
        """
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def is_enabled(self):
        """Flag which denotes whether package is in use or not
        """
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value

    @property
    def is_installed(self):
        """As name suggest, this flag tells whether package is installed or not
        """
        return self._is_installed

    @is_installed.setter
    def is_installed(self, value):
        self._is_installed = value

    def load_install_config(self):
        """Loads package details from config file during installation of this package
        """
        logger.debug('Looking for package file in...%s', self.location)
        temp_pkg_files = os.listdir(self.location)
        conf_file = ''
        for _file in temp_pkg_files:
            if _file.endswith(constants.PACKAGE_FILE_EXTENSION):
                conf_file = _file
                logger.debug('%s package file found', _file)
                break

        if conf_file == '':
            err = 'No config file found for this package'
            logger.error(err)
            raise NameError(err)
        else:
            self.config_file = utils.CheckedConfigParser()
            self.config_file.read(os.path.join(self.location, conf_file))
            self.package_id = self.config_file.get_or_none('Details', 'Id')
            self.name = self.config_file.get_or_none('Details', 'Name')
            self.description = self.config_file.get_or_none('Details', 'Description')
            self.type = self.config_file.get_or_none('Details', 'Type')
            self.author = self.config_file.get_or_none('Details', 'Author')
            self.url = self.config_file.get_or_none('Details', 'Url')
            self.version = self.config_file.get_or_none('Details', 'Version')
            self.company = self.config_file.get_or_none('Details', 'Company')
            self.__comp_name_list = self.config_file.get_or_none('Details', \
                                                                 'Components').split(',')
            self.package_dependencies = self.config_file.items('PackageDependencies')\
            if self.config_file.has_section('PackageDependencies') else {}
            logger.info('Package details loaded successfully...%s', self.name)
            logger.debug('Registring child components now...')
            self.__load_component_install_config()

    def __load_component_install_config(self):
        """Load details about all components which exists in this package
        """
        if self.__comp_name_list is None:
            self.load_install_config()
        if self.__comp_name_list is not None:
            for comp_name in self.__comp_name_list:
                comp_path = os.path.join(self.location, comp_name.strip())
                comp = components.ComponentInfo(comp_name.strip(), comp_path)
                comp.parent_id = self.package_id
                comp.load_install_config()
                self.__components[comp_name] = comp
                self.__comp_name_id_map[comp.id] = comp_name
                logger.debug('Component with Name:%s and Id:%s loaded successfully'\
                             , comp_name, comp.id)
        else:
            err = 'Can not load components of package...{0}'.format(self.name)
            logger.error(err)
            raise Exception(err)

    def load_details(self, pkg_id, db_conn):
        """Load details of package from database after the package has been installed in the system

        Args:
            pkg_id (uuid): A unique id assigned to package
            db_conn (object): An open connection to the metadata database
        """
        self.__db_connection = db_conn
        self.package_id = pkg_id
        logger.debug('Loading details for package...[%s] from db', pkg_id)
        if db_conn is not None:
            pkg_table = db_conn.table('Package')
            pkg = Query()
            pkg_record = pkg_table.get(pkg['Details']['id'] == pkg_id)
            if pkg_record is not None:
                self.__dict__ = pkg_record['Details']
                for comp_id, comp_name in self.__comp_name_id_map:
                    comp = components.ComponentInfo(comp_name, '')
                    comp.load_details(comp_id, db_conn)
                    self.__components[comp_name] = comp
                    logger.debug('Component [%s] with id [%s] loaded and restored \
                                 under pkg [%s]', comp_name, comp_id, self.name)
            logger.debug('Successfully loaded details for pkg [%s]', self.name)
        else:
            logger.error('Database connection is invalid; Can''t load pkg [%s] details',\
                         pkg_id)
            raise Exception('Database connection is invalid while loading pkg \
                            details...[%s]', pkg_id)

    def get_comp_name_list(self):
        """Returns a list containing name of all components available in this package

        Returns:
            comp_name_list ([str]): List of component names available in this package
        """
        if self.__comp_name_list is not None:
            return self.__comp_name_list
        self.load_details(self.package_id, self.__db_connection)
        return self.__comp_name_list

    def get_components(self):
        """Returns instances of all components which are part of this package

        Returns:
            components ([object]): Returns list of components instances
        """
        if self.__components is not None:
            return self.__components
        return None

    def get_component(self, comp_name):
        """Load component based on the name passed as args and return sane

        Args:
            comp_name (str): Name of the component which needs to be loaded

        Returns:
            An instance of component if found else None
        """
        if self.__comp_name_list is not None:
            return self.__components[comp_name]

        return None

    def get_component_by_id(self, comp_id):
        """Same as :meth:`get_component` but loads the component based on id

        Args:
            comp_id (uuid): The unique id assigned to an component

        Returns:
            An instance of component or None
        """
        if self.__components is not None and self.__comp_name_id_map is not None:
            if self.__comp_name_id_map[comp_id] is not None:
                return self.__comp_name_id_map[comp_id]
        else:
            return None

class PackageSource(object):
    """Base class for package source"""

    SESSION = sessions.Web().SESSION

    def __init__(self, download_location, db_connection, name):
        """Base constructor for package source
        Args:
            download_location (str): Folder location where package will be downloaded
            db_connection (object): An open cinnection to database
            name (str): Name of the package source
        """
        self.__download_location = download_location
        self.__db_connection = db_connection
        self.name = name
        self.details = {}

    def save(self):
        """Saves details of package source to database
        """
        pass

    def update(self, attribute_name, value):
        """Update current sources attribute with new value
        Args:
            attribute_name (str): Name of the attribute that needs to be updated
            value (str): New value that needs to be updated
        Returns:
            status (bool): True or False
            message (str): Failure reasons
        """
        pass

    async def get_package_index(self):
        """Downloads package index from configured source uri
        Returns:
            package_index (json): Package index dict
        """
        pass

    async def get_validity_status(self):
        """Returns the validity of package index such that if count of package index in source and :attr:`__index_list` matches, it returns True else False
        Returns:
            validity_status (bool): Returns True if count match else False
        """
        pass

    def get_cached_package_index(self):
        """Returns the current package index which was already downloaded
            in previous requests

        Returns:
            index (dict): Returns an dict of package names, version and dependencies
        """
        pass

class DefaultPackageSource(PackageSource):
    """Represents an package source in package management system
    """

    def __init__(self, download_location, db_connection, name, uri=None, username=None, password=None, src_type=None, modified_on=None, modified_by=None, security_id=None, class_type=None, class_in_module=None):
        """Creates new source or load existing source
        Args:
            download_location (str): Local folder where downloaded packages will be stored
            db_connection (object): An open connection to metadata db
            name (str): Name of package source
            uri (str): A web path or file system path to the source index
            username (str): Username to access source
            password (str): Password for accessing source
            src_type (str): Web or Filesystem
            modified_on: Modified on date time
            modified_by: Name of user who havemodified it
            security_id (uuid): Id of security principle
            class_type (PackageSource): derived class of the package source (should be derived from :class:`PackageSource`
            class_in_module (str): Name of the module which have above mentioned class_type
        """
        self.name = name
        self.__download_location = download_location
        self.__details = {
            'Name' : name,
            'Uri' : uri,
            'Username' : username,
            'Password' : password,
            'Src_type' : src_type,
            'Modified_On' : modified_on,
            'Modified_By' : modified_by,
            'Security_Id' : security_id,
            'ClassType': 'DefaultPackageSource',
            'ClassInModule': 'package'
        }
        self.__db_connection = db_connection
        self.__source_table = self.__db_connection.table('PackageSource')
        _details_in_db={}
        if self.__source_table is not None:
            _details_in_db = self.__source_table.get(Query()['Name'] == name)
            if len(_details_in_db) > 0:
                self.__details = _details_in_db
        self.__index_table = self.__db_connection.table('PackageIndex')
        self.__index_list = {}
        if self.__index_table is not None:
            self.__index_list = self.__index_table.get(Query()['Name'] == name)

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

    def uri():
        doc = "The uri property."
        def fget(self):
            return self.__details['Uri']
        return locals()
    uri = property(**uri())

    def username():
        doc = "The username property."
        def fget(self):
            return self.__details['Username']
        return locals()
    username = property(**username())

    def src_type():
        doc = "The src_type property."
        def fget(self):
            return self.__details['Src_type']
        return locals()
    src_type = property(**src_type())

    def security_id():
        doc = "The security_id property."
        def fget(self):
            return self.__details['Security_Id']
        return locals()
    security_id = property(**security_id())

    def details():
        doc = "The details property."
        def fget(self):
            return self.__details
        return locals()
    details = property(**details())

    def save(self):
        """Creates a new package source record and saves it in database
        """
        src_count = self.__source_table.count(Query()['Name'] == self.name)
        if src_count <= 0:
            _result = self.__source_table.insert(self.__details)
        else:
            return (False, 'A source with same name already exists - {0}'.format(self.name))
        if len(_result) > 0:
            return (True, _result)
        else:
            return (False, 'Unable to save package source')

    def update(self, attribute_name, value):
        """Update current sources attribute with new value
        Args:
            attribute_name (str): Name of the attribute that needs to be updated
            value (str): New value that needs to be updated

        Returns:
            status (bool): True or False
            message (str): Failure reasons
        """
        self.__details[attribute_name] = value
        _result = self.__source_table.update(self.__details, Query()['Name'] == self.name)
        if len(_result) > 0:
            return (True, _result)
        else:
            return (False, 'Unable to update attribute {0} with new value {1}'.format(attribute_name, value))

    async def get_package_index(self):
        """Downloads package index from configured source uri

        Returns:
            package_index (json): Package index dict
        """
        async with PackageSource.SESSION.get(self.__details['Uri'], params={'action': 'index'}) as _response:
            self.__index_list = await _response.json()
            return self.__index_list

    async def get_validity_status(self):
        """Returns the validity of package index such that if count of package index in source and :attr:`__index_list` matches, it returns True else False
        Returns:
            validity_status (bool): Returns True if count match else False
        """
        async with PackageSource.SESSION.get(self.__details['Uri'], params = {'action': 'count', 'local_index':len(self.__index_list)}) as _response:
            return await _response.json()

    def get_cached_package_index(self):
        """Returns the current package index which was already downloaded
            in previous requests

        Returns:
            index (dict): Returns an dict of package names, version and dependencies
        """
        return self.__index_list
