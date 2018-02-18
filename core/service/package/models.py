"""
.. module:: models
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""

#imports ---------------------------------
import abc
import os
import logging
import pathlib
from tinydb import TinyDB, Query, where
from ui_builder.core import utils, init_log, constants
from ui_builder.core.service import iplugins
from ui_builder.core.service.component import models
import six

#init logs ----------------------------
init_log.config_logs()
LOGGER = logging.getLogger(__name__)


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
        LOGGER.debug('Looking for package file in...%s', self.location)
        temp_pkg_files = os.listdir(self.location)
        conf_file = ''
        for _file in temp_pkg_files:
            if _file.endswith(constants.PACKAGE_FILE_EXTENSION):
                conf_file = _file
                LOGGER.debug('%s package file found', _file)
                break

        if conf_file == '':
            err = 'No config file found for this package'
            LOGGER.error(err)
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
            LOGGER.info('Package details loaded successfully...%s', self.name)
            LOGGER.debug('Registring child components now...')
            self.__load_component_install_config()

    def __load_component_install_config(self):
        """Load details about all components which exists in this package
        """
        if self.__comp_name_list is None:
            self.load_install_config()
        if self.__comp_name_list is not None:
            for comp_name in self.__comp_name_list:
                comp_path = os.path.join(self.location, comp_name.strip())
                comp = models.ComponentInfo(comp_name.strip(), comp_path)
                comp.parent_id = self.package_id
                comp.load_install_config()
                self.__components[comp_name] = comp
                self.__comp_name_id_map[comp.id] = comp_name
                LOGGER.debug('Component with Name:%s and Id:%s loaded successfully'\
                             , comp_name, comp.id)
        else:
            err = 'Can not load components of package...{0}'.format(self.name)
            LOGGER.error(err)
            raise Exception(err)

    def load_details(self, pkg_id, db_conn):
        """Load details of package from database after the package has been installed in the system
        Args:
            pkg_id (uuid): A unique id assigned to package
            db_conn (object): An open connection to the metadata database
        """
        self.__db_connection = db_conn
        self.package_id = pkg_id
        LOGGER.debug('Loading details for package...[%s] from db', pkg_id)
        if db_conn is not None:
            pkg_table = db_conn.table('Package')
            pkg = Query()
            pkg_record = pkg_table.get(pkg['Details']['id'] == pkg_id)
            if pkg_record is not None:
                self.__dict__ = pkg_record['Details']
                for comp_id, comp_name in self.__comp_name_id_map:
                    comp = models.ComponentInfo(comp_name, '')
                    comp.load_details(comp_id, db_conn)
                    self.__components[comp_name] = comp
                    LOGGER.debug('Component [%s] with id [%s] loaded and restored \
                                 under pkg [%s]', comp_name, comp_id, self.name)
            LOGGER.debug('Successfully loaded details for pkg [%s]', self.name)
        else:
            LOGGER.error('Database connection is invalid; Can''t load pkg [%s] details',\
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

@six.add_metaclass(abc.ABCMeta)
class PackageSource(iplugins.ISource):
    """Base class for package source"""

    def __init__(self):
        super(PackageSource, self).__init__()

    @abc.abstractmethod
    async def get_package_index(self):
        """Downloads package index from configured source uri
        Returns:
            package_index (json): Package index dict
        """
        pass

    @abc.abstractmethod
    async def get_validity_status(self):
        """Returns the validity of package index such that if count of \
                package index in source and :attr:`__index_list` matches, \
                it returns True else False
        Returns:
            validity_status (bool): Returns True if count match else False
        """
        pass

    @abc.abstractmethod
    def get_cached_package_index(self):
        """Returns the current package index which was already downloaded
            in previous requests

        Returns:
            index (dict): Returns an dict of package names, version and \
                    dependencies
        """
        pass
