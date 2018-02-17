"""
.. module:: package
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

class PackageIndexManager(object):
    """Provides indexing functionality of packages in all of the package sources.

    Note:
        This is an singleton class and will be
        shared between objects
    """

    __single_package_index_manager = None

    def __new__(cls, *args, **kwargs):
        """Singleton object creator
        """
        if cls != type(cls.__single_package_index_manager):
            cls.__single_package_index_manager = object.__new__(cls, *args, **kwargs)
        return cls.__single_package_index_manager

    def __init__(self, db_connection, download_location):
        """Initialize :class:`PackageIndexManager` class

        Args:
            db_connection (object): An open connection to metadata database
            download_location (str): location where packages will be downloaded
        """
        self.__db_connection = db_connection
        self._sources_table = db_connection.table('PackageSource')
        self.__package_sources = self.get_all_sources()
        self.__package_index_registry = {}
        self.__source_validity_status = {}
        self.__download_location = download_location
        self.__get_index_thread = tasks.HybridThread(name='PackageIndexCoroThread',\
                                                     notify_on_all_done=self.__common_callback)
        if len(self.__package_sources) <= 0:
            warnings.warn('No package source are configured. :class:`PackageManager`\
                          will not be able to download any packages')
        else:
            self.__update_package_list()

    def __common_callback(self, results, owner, _type):
        """The common coroutine callback, which will be called on completion \
                of all coroutines with owner as one of the parameters
        """
        if owner == 'ValidityStatusCheck':
            self.__validity_status_callback(results, _type)
        elif owner == 'FetchIndex':
            self.__update_index_callback(results, _type)

    async def __get_index(self, source):
        """Coroutine to get the index from source using async request

        Args:
            source (str): Name of the package source from where index needs to be fetched
        """
        return await source.get_package_index()

    def __update_index_callback(self, results, _type):
        """This function will be called once all coroutines :func:`__get_index` are done.
            This callback will receive a list of results in random order as a \
                    tuple of two elements (source-name, source-index-list)

        Args:
            results (list): A 2 element tuple list
            _type (int): function or coroutine
        """
        for result in results:
            _name = result[0]
            _source_index = result[1]
            self.__package_index_registry[_name] = _source_index
        if self.__get_index_thread is not None:
            self.__get_index_thread = None

    def get_all_sources(self):
        """Returns an list of :class:`PackageSource` configured in current system

        Returns:
            sources (PackageSource): list of all sources configured
        """
        _sources = {}
        if self._sources_table is not None:
            if self._sources_table.count() > 0:
                for source in self._sources_table.all():
                    class_type = source.details['class_type']
                    class_in_module = source.details['class_in_module']
                    source_object = object()
                    if class_type is not None and class_in_module is not None:
                        source_object = plugins.load(class_type, class_in_module)
                        if source_object is not None and callable(source_object):
                            _sources[source.name] = source_object(source.name)
                        else:
                            _sources[source.name] = DefaultPackageSource\
                                    (self.__download_location, \
                                    self.__db_connection, source.name)
        return _sources

    def add_source(self, download_loc, name, uri=None, username=None, password=None, \
                   src_type='Web', modified_on=None, modified_by=None, security_id=None, \
                   class_type=None, class_in_module=None):
        """Add an new source system
        Args:
            name (str): Name of the source
            uri (str): Uri of the new source i.e., url or folder path
            username (str): Username to access source uri (optional)
            password (str): Password to access source uri (optional)
            src_type (str): Type of the source - Web, FileSystem, etc
            modified_on (date): Datetime when new source is added
            modified_by (str): Name of the user who added the source
            security_id (uuid): The security rules applied to this source
            class_type (str): Class type of the source \
                    (should be derived from :class:`PackageSource`)
            class_in_module (str): Name of the module where the above \
                    'class_type' can be found
        Returns:
            status (bool): True or False
            message (str): Failure reason
        """
        new_source = DefaultPackageSource(download_loc, self.__db_connection, name, \
                                          uri=uri, username=username, password=password, \
                                   src_type=src_type, modified_on=modified_on, \
                                   modified_by=modified_by, security_id=security_id, \
                                   class_type=class_type, class_in_module=class_in_module)
        status = new_source.save()
        if status is not None and status[0] is True:
            self.__package_sources[name] = new_source
        return status

    def update_source(self, name, attribute_name, value=None):
        """Update an source system
        Args:
            name (str): Name of the source
            attribute_name (str): Name of the attribute that needs to be updated
            value (str): New value of the attribute to be updated
        Returns:
            status (bool): True or False
            message (str): Failure reason
        """
        if self._sources_table is not None and len(self.__package_sources) > 0:
            src_record = self.__package_sources[name]
            _result = src_record.update(attribute_name, value)
            return _result
            
        return (False, 'No package source are yet configured')

    def remove_source(self, source_name):
        """Removes source from system

        Args:
            source_name (str): Name of source that needs to be removed

        Returns:
            status (bool): True or False
            message (str): Reason for failurer
        """
        if source_name is not None:
            result = self._sources_table.remove(Query()['Name'] == source_name)
        if result is None or len(result) <= 0:
            return (False, 'Can''t delete source from the system')
            
        return (True, 'Source has been deleted - {0}'.format(result))

    async def __get_validity_status(self, source):
        """docstring for get_validity_status"""
        return await source.get_validity_status()

    def __validity_status_callback(self, results, _type):
        """Will be called once all :func:`__get_validity_status` coroutines are done

        Args:
            results (list): A list of two elements tuple
                                -[0] (str): source name
                                -[1] (bool): valid or not valid
        """
        for result in results:
            _src_name = result[0]
            _is_src_valid = result[1]
            self.__source_validity_status[_src_name] = _is_src_valid
        if self.__get_index_thread is not None:
            self.__get_index_thread = None

    def refresh_index(self, percentage_completed_callback=None):
        """Refresh the local index from the backend index source

        Args:
            percentage_completed_callback (callable): A callable which be called \
                    back to percentage completed status (optional)
        """
        self.__update_package_list(percentage_completed_callback)
        self.__get_index_thread.wait_for_all_coroutines()

    def __update_package_list(self, percentage_completed_callback=None):
        """This function will fetch a list of all packages under an source

        Args:
            percentage_completed_callback (func): Callback will be called on updation \
                    of each package and percentage completion will be passed to callback
        """
        if len(self.__package_sources) > 0:
            #Step1 - Get validity status of all current sources configured
            self.__get_index_thread.set_owner('ValidityStatusCheck')
            for source_name, source in self.__package_sources.items():
                self.__get_index_thread.add_coroutine(self.__get_validity_status, source)
                if percentage_completed_callback is not None:
                    #return the percentage completion
                    self.__get_index_thread.register_coroutine_completed_percentage\
                            (percentage_completed_callback)
            self.__get_index_thread.start_forever()
            #Will wait for coroutines to finish as we need it for next step
            self.__get_index_thread.wait_for_all_coroutines()
            #Step2 - Get cached package index for sources having valid indexes
            for source_name, is_valid in self.__source_validity_status.items():
                if is_valid:
                    self.__package_index_registry[source_name] = \
                            self.__package_sources[source_name].get_cached_package_index()
            #Step3 - Refresh cached index from source for those which are not valid
            self.__get_index_thread.set_owner('FetchIndex')
            for source_name, is_valid in self.__source_validity_status.items():
                if not is_valid:
                    self.__get_index_thread\
                            .add_coroutine(self.__get_index, \
                                           self.__package_sources[source_name])
                    if percentage_completed_callback is not None:
                        #return the percentage completion
                        self.__get_index_thread\
                                .register_coroutine_completed_percentage(percentage_completed_callback)
                self.__get_index_thread.reschedule()
                #No need to wait here as calling thread will handle it

    def get_package_list(self, refresh=False, percentage_completed_callback=None):
        """Returns an list of all packages either from cache or downloading it from source

        Args:
            refresh (bool): Whether to have package indexes refreshed before \
                    returning the index list (default=False)
        """
        if percentage_completed_callback is not None and callable(percentage_completed_callback):
            percentage_completed_callback(0)
        if refresh:
            self.__update_package_list(percentage_completed_callback)
            if self.__get_index_thread is not None:
                #wait for coroutines to finish
                self.__get_index_thread.wait_for_all_coroutines()
        if percentage_completed_callback is not None and callable(percentage_completed_callback):
            percentage_completed_callback(100)
        return self.__package_index_registry

    def find_package(self, package_name):
        """Finds an package in the index repository

        Args:
            package_name (str): Name of the package that needs to be searched

        Returns:
            result (tuple of 4 elements): Returns an tuple having below mentioned 4 elements
                - status (bool): True if package found else False
                - source_name (str): source name where package was found
                - package_index (dict): dict of package index
                - message (str): Error message if not able to find the package
        """
        if package_name is not None:
            for source_name, source in self.__package_sources.items():
                if self.__package_index_registry[source_name].__contains__(package_name):
                    return (True, source, \
                            self.__package_index_registry[source.name][package_name], '')
            return (False, None, None, 'No such package found...{0}'.format(package_name))
        return (False, None, None, 'Can''t accept blank value for package name')

class PackageManager(object):
    """This class is core in package management system. This manages all other services of 
        package management system. All sub-components should coordinate with help of this
        class
    """
    __single_package_manager = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_package_manager):
            cls.__single_package_manager = object.__new__(cls, *args, **kwargs)
        return cls.__single_package_manager

    def __init__(self, conf_path):
        """:class:`PackageManager` is an interface to the package management system and
            provide functionality (to find, install, load, etc) to manage various kinds of
            packages in the whole system. This class is a backbone of the whole system and
            should always have high priority in whole system.

            PackageManager have following core components:

                * :class:`PackageInstaller` - Install the package in system by updating its \
                        info in DB
                * :class:`PackageDownloader` - Downloads the package from relevant source
                * :class:`ArchiveManager` - Expands the package on local file system during \
                        installation
                        & keeps copy of uninstalled archived package in its local cache
                * :class:`PackageSource` - The source of an package
                * :class:`PackageIndexManager` - Maintains the index list of all packages \
                        (installed & uninstalled both)

        Notes: :class:`PackageManager` will work as a service and should have a dedicated thread
            for smooth functionality. The thread will be among other threads of high priority
        """
        logger.info('Starting PackageManager...')
        self._packages_map = {}
        self._packages_name_id_map = {}
        self.key_binding_config = configparser.ConfigParser()
        self.key_binding_config.read(os.path\
                                     .join(conf_path, \
                                           '{0}.cfg'.format(constants.COMMAND_BINDINGS)))
        self.__load_key_command_bindings()
        logger.debug('Loading PackageManager Configuration...%s', conf_path)
        self.package_id = None
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(conf_path, 'ui_builder.cfg'))
        self.pkg_install_location = os.path\
                .abspath(self.__config.get(constants.PACKAGE_INSTALLER, \
                                           constants.PKG_INSTALL_LOC))
        ###Setup commands
        self.__key_to_command_mapping = {}
        self.__db_connection = TinyDB(UI_BUILDER_DB_PATH)
        self.installer = PackageInstaller(conf_path)
        self.commands = package_commands.PackageCommands(self)
        self.commands.register_commands()
        self.downloader = PackageDownloader(conf_path)
        self.archive_manager = ArchiveManager(conf_path)
        self.component_manager = components.ComponentManager(self.__db_connection)
        self.package_index_manager = PackageIndexManager(self.__db_connection)

    @property
    def packages_name_id_map(self):
        """This property provides the mapping of package id to its name for fast lookup
        """
        return self._packages_name_id_map

    @property
    def packages_map(self):
        """Provides the mapping of package id and its in memory instance for \
                faster loading of packages
        """
        return self._packages_map

    def __load_key_command_bindings(self):
        """Loads the binding details between package manager's commands and associated keys
            These binding details will be used by the :class:`CommandManager`
        """
        for key, value in self.key_binding_config.items(constants.PACKAGE_MANAGER):
            self.__key_to_command_mapping[key] = value

    def load_package(self, pkg_name):
        """Load package details from the database, create instance of :class:`PackageInfo`
            and returns the imstance back. It also maintains the instance in in-memory
            mapping property :attr:`packages_map` for faster lookup

        Args:
            pkg_name (str): Name of the package to be loaded

        Returns:
            Instance of :class:`PackageInfo` class or None if not found
        """
        _pkg_table = self.__db_connection.table('Package_Index')
        _pkg = _pkg_table.get(Query()['name'] == pkg_name)
        if _pkg is not None:
            pkg = PackageInfo('')
            pkg.load_details(_pkg.id, self.__db_connection)
            self.packages_name_id_map[_pkg.name] = _pkg.id
            self.packages_map[_pkg.id] = pkg
            return pkg
        
        return None

    def load_packages(self):
        """Load all packages in the in-memory mapping property :attr:`packages_map`
        """
        _package_table = self.__db_connection.table('Package_Index')
        _all_packages = _package_table.all()
        for  pkg_record in _all_packages:
            pkg = PackageInfo('')
            pkg.load_details(pkg_record.id, self.__db_connection)
            self.packages_name_id_map[pkg_record.name] = pkg_record.id
            self.packages_map[pkg_record.id] = pkg
        logger.debug('Packages map has been initialized successfully!')

    def __get_package_file(self, package_name):
        """Gets the physical package file from drop-in location, archive cache, \
                index manager or download from source.
            Following workflow will be used to get the package file

            1. Request package from :class:`ArchiveManager`-
                1.1. If available in archive cache, ArchiveManager will return it for \
                        installation
                1.2. :class:`PackageManager` will forward the package to \
                        :class:`PackageInstaller` for further installation
            2. If not found in cache, the request will be forwarded to \
                    :class:`PackageIndexManager` to find the source of package
                2.1. If found in index, an instance of :class:`PackageSource` and \
                        request will be forwarded to :class:`PackageDownloader`\
                        to download package from respective source
                2.2. Once downloaded, request will goto :class:`PackageInstaller` \
                        for installation after package unarchived
                     by :class:`ArchiveManager`
                2.3. After installation, :class:`ArchiveManager` and :class:`PackageManager` \
                        will update its respective cache
            3. If not found in local index, an 'index refresh' request will be generated and \
                    process will start again from step '2' (once the index is refreshed)

        Args:
            package_name (str): Package name for which file needs to be returned

        Returns:
            package_file (PackageFile): An instance of :class:`PackageFile` \
                    having package content
        """
        #Step 1 - find package in archive manager and install
        _package_file = None
        if self.archive_manager.is_package_available(package_name):
            _package_file = self.archive_manager.get_package(package_name)
        elif self.archive_manager.is_package_available_in_cache(package_name):
            #Step 1.1
            _package_file = self.archive_manager.get_package_from_cache(package_name)
            #Step 2 - Get source of package from :class:`PackageIndexManager`. \
                    #The result will have following format (Status:[True/False], \
                    #SourceName, Source Instance, Error Message)
        if _package_file is not None:
            return (True, _package_file, '')
        else:
            package_source = self.package_index_manager.find_package(package_name)
        #Step 2.1 - Package found in index, ask :class:`PackageDownloader` to \
                #download package in :attr:`pkg_drop_location`
        if package_source[0]:
            self.downloader.download(package_source[1], package_source[2])
        #Step 2.2 - Get the downloaded physical package file :class:`PackageFile` \
                #from :class:`ArchiveManager`
        if self.archive_manager.is_package_available(package_name):
            return (True, self.archive_manager.get_package(package_name), '')
            
        return (False, None, 'Package not available in local and source index')

    def install_package(self, package_name, percentage_completed_callback=None):
        """Install package on local file system. This class will use \
                :meth:`__get_package_file` to get the package file

        Args:
            package_name (str): Name of the package that needs to be installed

        Returns:
            status (bool): True or False
            message (str): Failure details

        Note:
            Please refer to :class:`PackageIndexManager` for more information on 'PackageIndex' refresh request
        """
        if package_name is None:
            raise Exception('Can''t accept blank package name')

        _package_file = self.__get_package_file(package_name)
        if _package_file is not None:
            #Step 1.2 & 2.2 - Install package
            _status = self.installer.install_package(package_name, _package_file)
            #Step 2.3 - Update caches
            self.archive_manager.move_package_to_cache(package_name)
            self.load_package(package_name)
            return _status
        else:
            #Step 3 - Get local index refreshed from :class:`PackageIndexManager`
            self.package_index_manager.refresh_index(percentage_completed_callback)
            #Step 3.2 - Start process again from step 2
            _package_file = self.__get_package_file(package_name)
            self.packages_map
            #Install the package if found
            if _package_file is not None:
                _status = self.installer.install_package(package_name, _package_file)
                return _status
                
            return (False, 'Package not found...{0}'.format(file_name))

    def install_packages(self, package_list=[], percentage_completed_callback=None):
        """Install packages provided as list
        Args:
            package_list (list): Name of packages to be installed
        Returns:
            results (list): Returns a list of results for all packages passed to this function
        """
        _results = {}
        for package in package_list:
            _status = self.install_package(package, percentage_completed_callback)
            _results[package] = _status
        return _results

    def uninstall_package(self, package_name):
        """Uninstall the package from system. This call will be forwarded to installer for performing the operation

        Args:
            package_name (str): Name of the package that needs to be uninstalled

        Returns:
            status (bool): Returns True or False
            message (str): Reason in case of failure
        """
        return self.installer.uninstall_package(package_name)

    def __update_packages_enabled_status(self, status, package_list):
        """Changes the :attr:`is_enabled` property of a package

        Args:
            status (bool): The new value of is_enabled property
            package_list (list): A list of package names that needs to be updated

        Returns:
            status (bool): Returns True or False
            message (str): Reason for failure
        """
        _results = {}
        for package_name in package_list:
            if self.packages_name_id_map.__contains__(package_name):
                _package_id = self.packages_name_id_map[package_name]
                if self.packages_map.__contains__(_package_id):
                    _package = self.packages_map[_package_id]
                    _package.is_enabled = status
                    self.packages_map[_package_id] = _package
                    _package_table = self.__db_connection.table('Packages')
                    _package_record = _package_table.get(Query['Details']['id'] == _package_id)
                    _package_record['Details']['is_enabled'] = status
                    _package_table.update({'Details': _package_record}, Query()['Details']['id'] == _package_id)
                    _status = (True, '')
                    _results[package_name] = _status
                else:
                    _status = (False, 'No such package exists in package_id->package map')
                    _results[package_name] = _status
            else:
                _status = (False, 'No such package exists in package_name->package_id map')
                _results[package_name] = _status
        return _results

    def activate_packages(self, package_list):
        """Same as :meth:`update_packages_enabled_status` but call this function with status=True
            to activate all packages in list

        Args:
            package_list (list): A list of package names that needs to be updated

        Returns:
            status (bool): Returns True or False
            message (str): Reason for failure
        """
        return self.__update_packages_enabled_status(True, package_list)

    def activate_package(self, package_name):
        """Same as activate packages function but accepts only one package at a time

        Args:
            package_name (str): Packages's name that needs to be activated

        Returns:
            status (bool): True or False
            message (str): Reason for failure
        """
        _package_list = []
        _package_list.append(package_name)
        return self.activate_packages(_package_list)

    def deactivate_packages(self, package_list):
        """Same as :meth:`activate_packages` but passes value False to deactivate packages

        Args:
            package_list (list): List of packages that needs to be deactivated

        Returns:
            status (bool): True or False
            message (str): Reason for failure
        """
        return self.__update_packages_enabled_status(False, package_list)

    def deactivate_package(self, package_name):
        """Same as :meth:`deactivate_packages` but works for only one package at a time

        Returns:
            status (bool): True or False
            message (str): Reason for failure
        """
        package_list=[]
        package_list.append(package_name)
        return self.deactivate_packages(package_list)

    def list_packages(self):
        """
         Provides an list of all installed packages
        """
        return self.package_index_manager.get_package_list()

    def show_package(self, pkg_name):
        """TODO: Docstring for show_package.
        :returns: TODO
        """
        if self.packages_name_id_map is None or len(self.packages_name_id_map) <= 0:
            self.load_packages()
        if pkg_name is not None and pkg_name != '':
            pkg_id = self.packages_name_id_map[pkg_name]
            if pkg_id is not None:
                pkg = self.packages_map[pkg_id]
                _details = utils.FormattedStr()
                _details.format('Name', pkg.name)
                _details.format('Description', pkg.description)
                _details.format('Location', pkg.location)
                _details.format('Type', pkg.type)
                _details.format('Author', pkg.author)
                _details.format('Url', pkg.url)
                _details.format('Company', pkg.company)
                _details.format('Version', pkg.version)
                _details.format('Is Enabled', pkg.is_enabled)
                _details.format('Is Installed', pkg.is_installed)
                for comp in pkg.get_comp_name_list():
                    _details.format('Component', comp)
                return _details.get_str()
            else:
                return 'Unable to get details as package [{0}] is not availabel locally\n'\
                        'Kindly refresh the packages index'
        else:
                raise Exception('Package not found...{0}'.format(pkg_name))

    def list_sources(self):
        """TODO: Docstring for list_sources.
        :returns: TODO

        """
        return self.package_index_manager.get_all_sources()

    def find_package(self, package_name):
        """Finds an package by name in all available sources
        """
        if package_name is not None:
            return self.package_index_manager.find_package(package_name)
        else:
            raise Exception('No such package found...{0}'.format(package_name))

class PackageSource(object):
    """Base class for package source"""

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
    SESSION = aiohttp.ClientSession()

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

class Downloader(object):
    """Base class for downloader. All downloaders should inherit from this class """

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

class PackageInstaller(object):
    """Installs the package on local system. This class interacts with :class:`PackageDownloader`
        or :class:`ArchiveManager` to complete its operation
    """

    __single_package_installer = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_package_installer):
            cls.__single_package_installer = object.__new__(cls, *args, **kwargs)
        return cls.__single_package_installer

    def __init__(self, package_manager, conf_path):
        """TODO: to be defined1. """
        logger.debug('Loading PackageInstaller Configuration...{0}'.format(conf_path))
        self.id = None
        self._config = configparser.ConfigParser()
        self._config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = os.path.abspath(self._config.get(PACKAGE_INSTALLER, PKG_INSTALL_LOC))
        logger.debug('Packages will be installed in following location...{0}'.format(self.pkg_install_location))
        self.package_manager = package_manager

        global UI_BUILDER_DB_PATH
        UI_BUILDER_DB_PATH = self._config.get(PACKAGE_INSTALLER, UI_BUILDER_DB)

    def pkg_install_location():
        doc = "The pkg_install_location property."
        def fget(self):
            return self._pkg_install_location
        def fset(self, value):
            self._pkg_install_location = value
        def fdel(self):
            del self._pkg_install_location
        return locals()
    pkg_install_location = property(**pkg_install_location())

    def uninstall_package(self, package_name):
        """Uninstall a package from the system.
        Note:
            Though the package will be uninstalled from the system, but an copy of archived package will be available in archive cache

        Args:
            package_name (str): Name of package that needs to be uninstalled

        Returns:
            None
        """
        db = TinyDB(UI_BUILDER_DB_PATH)
        q = Query()
        pkg_idx = db.table('Package_Index')
        pkg = pkg_idx.get(q['name'] == package_name)
        if len(pkg) > 0:
            if len(pkg) == 1:
                pkg_tbl = db.table('Package')
                pkg_record = pkg_tbl.get(Query()['Details']['id'] == pkg.id)
                if len(pkg_record) > 0:
                    if len(pkg_record) == 1:
                        location = pkg_record['Location']
                        #WARNING-This section physically removes the package and its components from file system and unregisters it from index and registry. PackageManager should take care of unregistering the components once this ops gets completed successfully
                        if location is not None and os.path.exists(location):
                            shutil.rmtree(location, ignore_errors=True)
                            pkg_tbl.remove(Query['Details']['id'] == pkg.id)
                            pkg_idx.remove(Query['id'] == pkg.id)
                            del pkg
                        elif location is not None and os.path.exists(location) == False:
                            logger.warn('No folder exists at location [{0}], deleting entry for pkg from index'.format(location))
                            pkg_tbl.remove(Query['Details']['id'] == pkg.id)
                            pkg_idx.remove(Query['id'] == pkg.id)
                            del pkg
                        else:
                            logger.warn('Package is in inconsistent state, removing package details from system...{0}'.format(pkg.name))
                            pkg_tbl.remove(Query['Details']['id'] == pkg.id)
                            pkg_idx.remove(Query['id'] == pkg.id)
                            del pkg
                    else:
                        logger.warn('More than 1 package found with same name, package uninstall is skipped...{0}'.format(package_name))
                else:
                    logger.warn('No such pakage exist...{0}'.format(package_name))
            else:
                logger.warn('More than 1 package found, skipping uninstall process...{0}'.format(package_name))
        else:
            logger.warn('No such package exists...{0}'.format(package_name))

    def install_package(self, package_name, package_file):
        """Install package on the local file system
        Args:
            package_name (str): Name of the package that needs to be installed
            package_file (PackageFile): An instance of :mod:`ui_builder.core.io.filesystem`.:class:`PackageFile`
        """
        package_overwrite_mode = True if self._config.get(PACKAGE_INSTALLER, PKG_OVERWRITE_MODE).upper() == 'ON' else False
        package_path = package_file.extract_to(self.pkg_install_location, overwrite=package_overwrite_mode)
        package_info = self.__validate_package(package_path)
        registered = self.__register_package(package_info)
        if registered == False:
            logger.warn('Unable to register package, check logs for more info...{0}'.format(package_name))
            return False
        else:
            logger.info('Package has been installed successfully...{0}'.format(package_name))
            return True

    def __validate_package(self, package_path):
        """Validates the content of extracted package on file system and returns an instance :class:`PackageInfo` if validated successfully

        Args:
            package_path (Path): An instance of :mod:`pathlib`.:class:`Path` pointing to physical package file

        Returns:
            package (PackageInfo): Returns an instace of :class:`PackageInfo`
        """
        logger.debug('Validating package at location...{0}'.format(package_path))
        #find .pkg files
        package_config_file = glob.glob(os.path.join(package_path, '*.pkg'))
        if len(package_config_file) == 1:
            package_info = PackageInfo(package_config_file)
            logger.debug('Package definition found...{0}'.format(package_config_file[0]))
            return package_info
        elif len(package_config_file) > 1:
            logger.warn('Multiple .pkg files found. A valid package should have only one .pkg file')
            return None
        else:
            logger.warn('No .pkg file found. A package should have exactly one .pkg file')
        return None

    def __register_package(self, package_info):
        """Registers the package with :class:`PackageManager` and its components with :class:`ComponentManager`

        Args:
            package_info (PackageInfo): An instance of :class:`PackageInfo`that needs to be registered
        """
        logger.debug('Loading package details stored at...{0}'.format(package_info.location))
        package_info._load_install_config()
        logger.debug('Open connection to database: {0}'.format(UI_BUILDER_DB_PATH))
        #global UI_BUILDER_DB_PATH
        db = TinyDB(UI_BUILDER_DB_PATH)
        q = Query()
        package_table = db.table('Packages')
        package_info.is_enabled = True
        package_info.is_installed = True
        package_details = package_info.__dict__.copy()
        #we will not save config and component objects
        package_details['_config_file'] = None
        package_details['_components'] = None
        package_entry = package_table.upsert({'Location':package_info.location, 'Details':package_details}, q['Details']['id'] == package_info.id)
        logger.debug('Package with name [{0}] and id [{1}] has been registered'.format(package_info.name, package_info.id))
        package_index_table = db.table('Package_Index')
        index_q = Query()
        package_index = package_index_table.upsert({'Id':package_info.id, 'Name':package_info.name}, index_q['Id'] == package_info.id)
        logger.debug('Processing child components now...')
        for name, component in package_info.components.items():
            self.component_manager.register(component.id, component, package_info)
        return True

class ArchiveManager(object):
    """ArchiveManager maintains all the packages which are available on local system in compressed/zip state

    Note: This is an singleton class and is shared among other objects
    """
    __single_archive_manager = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_archive_manager):
            cls.__single_archive_manager = object.__new__(cls, *args, **kwargs)
        return cls.__single_archive_manager

    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = configparser.ConfigParser()
        self._config.read(os.path.join(conf_path, 'ui_builder.cfg'))
        self.archive_drop_location = os.path.abspath(self._config.get(constants.PACKAGE_INSTALLER, constants.PKG_DROP_IN_LOC))
        self.archive_cache_location = os.path.abspath(self._config.get(constants.PACKAGE_INSTALLER, constants.PKG_DROP_IN_LOC))
        self.archive_file_list  = None

    def archive_drop_location():
        doc = "The archive_drop_location property."
        def fget(self):
            return self._archive_drop_location
        def fset(self, value):
            self._archive_drop_location = value
        def fdel(self):
            del self._archive_drop_location
        return locals()
    archive_drop_location = property(**archive_drop_location())

    def archive_file_list():
        doc = "The archive_file_list property."
        def fget(self):
            return self._archive_file_list
        def fset(self, value):
            self._archive_file_list = value
        def fdel(self):
            del self._archive_file_list
        return locals()
    archive_file_list = property(**archive_file_list())

    def archive_cache_location():
        doc = "The archive_cache_location contains all the downloaded packes for future installation"
        def fget(self):
            return self._archive_cache_location
        def fset(self, value):
            self._archive_cache_location = value
        def fdel(self):
            del self._archive_cache_location
        return locals()
    archive_cache_location = property(**archive_cache_location())

    def move_package_to_cache(self, package_name):
        """Moves the processed package to cache location for future references

        Args:
            package_name (str): Name of the package that needs to be moved

        Returns:
            status (bool): Returns True or False depending upon move ops result
        """
        if package_name is not None:
            package_path = self.get_validated_package_path(package_name)
            if package_path is not None:
                package_file = filesystem.PackageFile(package_path)
                status = package_file.move(self.archive_cache_location)
                if status is not None:
                    return True
        return False

    def restore_package_from_cache(self, package_name):
        """Restore package from cache back to drop-in location for installation

        Args:
            package_name (str): Name of the package that needs to be restored

        Returns:
            status (bool): Returns true or false
        """
        if package_name is not None:
            package_path = self.get_validated_package_cache_path(package_name)
            if package_path is not None:
                package_file = filesystem.PackageFile(package_path)
                package = package_file.move(self.archive_drop_location)
                if package is not None:
                    return None
        return False

    def get_validated_package_path(self, package_name):
        """Looks for a package file on local file system, check if it is a valid zip file
            and return back the path to package file

        Args:
            package_name (str): This should be the package name and not a package "file" name

        Returns:
            file_path (str): Absolute path to package file on file system
        """
        for file_name in os.listdir(self.archive_drop_location):
            package_name = validFileName('{0}.{1}'.format(package_name, constants.PACKAGE_FILE_EXTENSION))
            if file_name.upper() == package_name.upper():
                file_path = os.path.join(self.archive_drop_location, file_name)
                if os.path.isfile(file_path):
                    try:
                        utils.validate_file(file_path)
                        if zipfile.is_zipfile(file_path):
                            return file_path
                        else:
                            return None
                    except Exception as msg:
                        return None

    def get_validated_package_path_list(self):
        """Same as :meth:`get_validated_package_path` but returns a list of packages available in :attr:`package_drop_in_location`

        None:
            file_paths (list): Returns a list of valid package paths from drop in location
        """
        self.archive_file_list = []
        for file_name in os.listdir(self.archive_drop_location):
            file_path = os.path.join(self.archive_drop_location, file)
            if os.path.isfile(file_path):
                try:
                    utils.validate_file(file_path)
                    if zipfile.is_zipfile(file_path):
                        self.archive_file_list.append(file_path)
                    else:
                        logger.debug('File is not zipped and is skipped...{0}'.format(file))
                except Exception as msg:
                    logger.warn('Invalid file and is skipped...{0}'.format(file))
            else:
                logger.debug('Not a file and is skipped...{0}'.format(file))
        return self.archive_file_list


    def is_package_available(self, package_name):
        """Checks whether package exists in package drop location or not
        """
        if package_name is not None:
            package_name = '{0}.pkg'.format(validFileName(package_name))
            package_file = os.path.join(self.archive_drop_location, package_name)
            if os.path.exists(package_file):
                return True
        else:
            return False

    def get_package(self, package_name):
        """Find a package in drop-in location and return back file object

        Args:
            package_name (str): Package name that needs to be returned from drop-in location

        Returns:
            zipped_file (ZipFile): An instance of :class:`ZipFile` available in module :mod:`ui_builder.core.io.filesystem`
        """
        if self.is_package_available(package_name):
            file_path = self.get_validated_package_path(package_name)
            zipped_file = filesystem.PackageFile(file_path)
            return zipped_file

    def is_package_available_in_cache(self, package_name):
        """Checks whether package exists in the archive cache or not
        """
        if package_name is not None:
            package_name = '{0}.pkg'.format(validFileName(package_name))
            package_file = os.path.join(self.archive_cache_location, package_name)
            if os.path.exists(package_file):
                return True
        else:
            return False

    def get_validated_package_cache_path(self, package_name):
        """Looks for a package file on local archive cache, check if it is a valid zip file
            and return back the path to package file

        Args:
            package_name (str): This should be the package name and not a package "file" name

        Returns:
            file_path (str): Absolute path to package file on file system or None
        """
        for file_name in os.listdir(self.archive_cache_location):
            package_name = validFileName('{0}.{1}'.format(package_name, constants.PACKAGE_FILE_EXTENSION), initCap=False)
            if file_name.upper() == package_name.upper():
                file_path = os.path.join(self.archive_cache_location, file_name)
                if os.path.isfile(file_path):
                    try:
                        utils.validate_file(file_path)
                        if zipfile.is_zipfile(file_path):
                            return file_path
                        else:
                            return None
                    except Exception as msg:
                        return None

    def get_package_from_cache(self, package_name):
        """Find a package in local archive location and return back file object

        Args:
            package_name (str): Package name that needs to be returned from cache

        Returns:
            zipped_file (ZipFile): An instance of :class:`ZipFile` available in module :mod:`ui_builder.core.io.filesystem`
        """
        if self.is_package_available_in_cache(package_name):
            file_path = self.get_validated_package_cache_path(package_name)
            zipped_file = filesystem.PackageFile(file_path)
            return zipped_file

class DummyDownloader(Downloader):

    """Docstring for DummyDownloader. """

    def __init__(self):
        """TODO: to be defined1. """

        
