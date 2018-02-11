"""
.. module:: package_commands
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""


#imports ---------------------------------
from ui_builder.core import utils, init_log, constants
import configparser
import uuid
import os
import zipfile
import logging
import shutil
import glob
import pathlib
import importlib
import inspect
import asyncio
from goldfinch import validFileName
from tinydb import TinyDB, Query, where
from ui_builder.core.package import package_commands, components
from ui_builder.core.io import filesystem

#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)


class PackageInfo(object):
    """:class:`PackageInfo` class contains information about a package in the Package Managment System
        A package consist of one or more components grouped logically together. If there is an dependency
        between components and other packages, same will be defined in this class
    """

    def __init__(self, config_file_path=None):
        """:class:`PackageInfo` class have one required parameter

        Args:
            config_file_path (str): Location of the package on the local file system where package is installed
        """
        if config_file_path is not None:
            config_file_path = pathlib.Path(config_file_path).absolute() if config_file_path.find('~') < 0 else pathlib.Path(config_file_path).expanduser()
        else:
            raise Exception('Path to config file can''t be none')
        self.id = None
        self.location = config_file_path.parent
        self.config_file = config_file_path
        self.name = None
        self.description = None
        self.type = None
        self.author = None
        self.url = None
        self.company = None
        self.version = None
        self.is_enabled = True
        self.is_installed = False
        self._comp_name_list = []
        self._comp_name_id_map = {}
        self._components = {}
        self.package_dependencies = {}

    def config_file():
        doc = "Location and name of config file which will be used during installation of the package"
        def fget(self):
            return self._config_file
        def fset(self, value):
            self._config_file = value
        def fdel(self):
            del self._config_file
        return locals()
    config_file = property(**config_file())

    def location():
        doc = "The location on file system where this package is installed or will be installed"
        def fget(self):
            return self._location
        def fset(self, value):
            self._location = value
        def fdel(self):
            del self._location
        return locals()
    location = property(**location())

    def is_enabled():
        doc = "Flag which denotes whether package is in use or not"
        def fget(self):
            return self._is_enabled
        def fset(self, value):
            self._is_enabled = value
        def fdel(self):
            del self._is_enabled
        return locals()
    is_enabled = property(**is_enabled())

    def is_installed():
        doc = "As name suggest, this flag tells whether package is installed or not"
        def fget(self):
            return self._is_installed
        def fset(self, value):
            self._is_installed = value
        def fdel(self):
            del self._is_installed
        return locals()
    is_installed = property(**is_installed())

    def _load_install_config(self):
        """Loads package details from config file during installation of this package
        """
        logger.debug('Looking for pkg file in...{0}'.format(self.location))
        temp_pkg_files = os.listdir(self.location)
        conf_file = ''
        for f in temp_pkg_files:
            if f.endswith('.pkg'):
                conf_file = f
                logger.debug('{0} pkg file found'.format(f))
                break

        if conf_file == '':
            err = 'No config file found for this package'
            logger.error(err)
            raise NameError(err)
        else:
            self.config_file = utils.CheckedConfigParser()
            self.config_file.read(os.path.join(self.location, conf_file))
            self.id = self.config_file.get_or_none('Details', 'Id')
            self.name = self.config_file.get_or_none('Details', 'Name')
            self.description = self.config_file.get_or_none('Details', 'Description')
            self.type = self.config_file.get_or_none('Details', 'Type')
            self.author = self.config_file.get_or_none('Details', 'Author')
            self.url = self.config_file.get_or_none('Details', 'Url')
            self.version = self.config_file.get_or_none('Details', 'Version')
            self.company = self.config_file.get_or_none('Details', 'Company')
            self._comp_name_list = self.config_file.get_or_none('Details', 'Components').split(',')
            self.package_dependencies = self.conf_file.items('PackageDependencies') if self.conf_file.has_section('PackageDependencies') else {}
            logger.info('Package details loaded successfully...{0}'.format(self.name))
            logger.debug('Registring child components now...')
            self._load_child_comp_config()

    def _load_child_comp_config(self):
        """Load details about all components which exists in this package
        """
        if self._comp_name_list is None:
            self._load_pkg_config()

        if self._comp_name_list is not None:
            for comp_name in self._comp_name_list:
                comp_path = os.path.join(self.location, comp_name.strip())
                comp = ComponentInfo(comp_name.strip(), comp_path)
                comp.parent_id = self.id
                comp._load_component_config()
                self._components[comp_name] = comp
                self._comp_name_id_map[comp.id] = comp_name
                logger.debug('Component with Name:{0} and Id:{1} loaded successfully'.format(comp_name, comp.id))
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
        logger.debug('Loading details for package...[{0}] from db'.format(pkg_id))
        if db_conn is not None:
            pkg_table = db_conn.table('Package')
            Pkg = Query()
            pkg_record = pkg_table.get(Pkg['Details']['id'] == pkg_id)
            if pkg_record is not None:
                self.__dict__ = pkg_record['Details']
                for comp_id, comp_name in self._comp_name_id_map:
                    comp = ComponentInfo(comp_name, '')
                    comp.load_details(comp_id, db_conn)
                    self._components[comp_name] = comp
                    logger.debug('Component [{0}] with id [{1}] loaded and restored under pkg [{3}]'.format(comp_name, comp_id, self.name))
            logger.debug('Successfully loaded details for pkg [{0}]'.format(self.name))
        else:
            logger.error('Database connection is invalid; Can''t load pkg [{0}] details'.format(pkg_id))
            raise Exception('Database connection is invalid while loading pkg details...[{0}]'.format(pkg_id))

    def get_comp_name_list(self):
        """Returns a list containing name of all components available in this package

        Returns:
            comp_name_list ([str]): List of component names available in this package
        """
        if self._comp_name_list is not None:
            return self._comp_name_list
        else:
            self.load_details()
            return self._comp_name_list

    def get_components(self):
        """Returns instances of all components which are part of this package

        Returns:
            components ([object]): Returns list of components instances
        """
        if self._components is not None:
            return self._components
        else:
            self.load_components()
            return self._components
        return None

    def get_component(self, comp_name):
        """Load component based on the name passed as args and return sane

        Args:
            comp_name (str): Name of the component which needs to be loaded

        Returns:
            An instance of component if found else None
        """
        if self._comp_name_list is not None:
            return self._components[comp_name]

        return None

    def get_component_by_id(self, comp_id):
        """Same as :meth:`get_component` but loads the component based on id

        Args:
            comp_id (uuid): The unique id assigned to an component

        Returns:
            An instance of component or None
        """
        if self._components is not None and self._comp_name_id_map is not None:
            if self._comp_name_id_map[comp_id] is not None:
                return self._comp_name_id_map[comp_id]
            else:
                return None
        else:
            return None

class PackageManager(object):
    def __init__(self, conf_path):
        """:class:`PackageManager` is an interface to the package management system and
            provide functionality (to find, install, load, etc) to manage various kinds of
            packages in the whole system. This class is a backbone of the whole system and
            should always have high priority in whole system.

            PackageManager have following core components:

                * :class:`PackageInstaller` - Install the package in system by updating its info in DB
                * :class:`PackageDownloader` - Downloads the package from relevant source
                * :class:`ArchiveManager` - Expands the package on local file system during installation
                                            & keeps copy of uninstalled archived package in its local cache
                * :class:`PackageSource` - The source of an package
                * :class:`PackageIndexManager` - Maintains the index list of all packages (installed & uninstalled both)

        Notes: :class:`PackageManager` will work as a service and should have a dedicated thread
            for smooth functionality. The thread will be among other threads of high priority
        """
        logger.info('Starting PackageManager...')
        self.packages_map = {}
        self.packages_name_id_map = {}
        self.key_binding_config = configparser.ConfigParser()
        self.key_binding_config.read(os.path.join(conf_path, '{0}.cfg'.format(COMMAND_BINDINGS)))
        self.__load_key_command_bindings()
        logger.debug('Loading PackageManager Configuration...{0}'.format(conf_path))
        self.id = None
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = os.path.abspath(self.__config.get(PACKAGE_INSTALLER, PKG_INSTALL_LOC))
        ###Setup commands
        self.__db_connection = TinyDB(UI_BUILDER_DB_PATH)
        self.installer = PackageInstaller(conf_path)
        self.commands = package_commands.PackageCommands(self)
        self.commands.register_commands()
        self.downloader = PackageDownloader(conf_path)
        self.archive_manager = ArchiveManager(conf_path)
        self.component_manager = components.ComponentManager(self.__db_connection)

    def packages_name_id_map():
        doc = "This property provides the mapping of package id to its name for fast lookup"
        def fget(self):
            return self._packages_name_id_map
        def fset(self, value):
            self._packages_name_id_map = value
        def fdel(self):
            del self._packages_name_id_map
        return locals()
    packages_name_id_map = property(**packages_name_id_map())

    def packages_map():
        doc ="Provides the mapping of package id and its in memory instance for faster loading of packages"
        def fget(self):
            return self._packages_map
        def fset(self, value):
            self._packages_map = value
        def fdel(self):
            del self._packages_map
        return locals()
    packages_map = property(**packages_map())

    def __load_key_command_bindings(self):
        """Loads the binding details between package manager's commands and associated keys
            These binding details will be used by the :class:`CommandManager`
        """
        for key, value in self.key_binding_config.items(PACKAGE_MANAGER):
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
            self.packages_name_id_map[_pkg.name]=_pkg.id
            self.packages_map[_pkg.id] = pkg
            return pkg
        else:
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

    def install_package(self, package_name):
        """Install package on local file system. It will follow the below mentioned workflow for installation-
            1. Request package from :class:`ArchiveManager`-
                1.1. If available in archive cache, ArchiveManager will return it for installation
                1.2. :class:`PackageManager` will forward the package to :class:`PackageInstaller` for further installation
            2. If not found in cache, the request will be forwarded to :class:`PackageIndexManager` to find the source of package
                2.1. If found in index, an instance of :class:`PackageSource` and request will be forwarded to :class:`PackageDownloader` to download package from respective source
                2.2. Once downloaded, request will goto :class:`PackageInstaller` for installation after package unarchived by :class:`ArchiveManager`
                2.3. After installation, :class:`ArchiveManager` and :class:`PackageManager` will update its respective cache
            3. If not found in local index, an 'index refresh' request will be generated and process will start again from step '2' (once the index is refreshed)

        Note:
            Please refer to :class:`PackageIndexManager` for more information on 'PackageIndex' refresh request
        """
        #Step 1 - find package in archive manager and install
        if self.archive_manager.is_package_available(package_name):
            self.installer.install_package(package_name)
        else:
            status = self.download_package(package_name)
            if status == 'SUCCESS':
                self.installer.install_package(package_name)
                return status
            else:
                raise Exception('Package not found...{0}'.format(file_name))

    def install_packages(self):
        """TODO: Docstring for install_packages.
        :returns: TODO
        """
        self.installer.install_packages()

    def uninstall_package(self, package_name):
        """TODO: Docstring for uninstall_package.

        Args:
            package_name (str): Name of the package that needs to be uninstalled

        Returns:
            None
        """
        self.installer.uninstall_package(package_name)

    def activate_packages(self):
        """TODO: Docstring for activate_packages.
        :arg1: TODO
        :returns: TODO
        """
        for pkg_id, pkg in self.packages_map:
            pkg.is_enabled = True

    def activate_package(self, package_name):
        """TODO: Docstring for activate_package.
        :returns: TODO
        """
        pkg = self.packages_map[self.packages_name_id_map[package_name]]
        pkg.is_enabled = True

    def deactivate_package(self, package_name):
        """TODO: Docstring for deactivate_package.
        :package_id: TODO
        :returns: TODO
        """
        pkg = self.packages_map[self.packages_name_id_map[package_name]]
        pkg.is_enabled = False

    def deactivate_packages(self):
        """TODO: Docstring for deactivate_packages.
        :returns: TODO
        """
        for pkg_id, pkg in self.packages_map.iteritems():
            pkg.is_enabled = False

    def list_packages(self):
        """TODO: Docstring for list_packages.
        :returns: TODO
        """
        if self.packages_name_id_map is None or len(self.packages_name_id_map) <= 0:
            self.load_packages()
        pkgs = self.downloader.list_packages()
        if pkgs is not None:
            pkgs['Local Packages'] = self.packages_name_id_map.keys()
        return pkgs

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
                        'Kindly download package first using below command:\n'\
                        'Package download <pkg name>'.format(pkg_name)
        else:
                raise Exception('Package not found...{0}'.format(pkg_name))

    def download_package(self, package_name, source_name=None):
        """TODO: Docstring for download_package.
        :pkg_nam: TODO
        :returns: TODO
        """
        result = None
        if source_name is None:
            #search package in all sources
            for src_name, src in self.downloader.download_src.iteritems():
                result = self.downloader.find_package(src_name, package_name)
                if result is not None:
                    return self.downloader.download(src_name, package_name)
        else:
            return self.downloader.download(source_name, package_name)
        return 'NOT_FOUND'

    def list_sources(self):
        """TODO: Docstring for list_sources.
        :returns: TODO

        """
        return self.downloader.download_src

    def find_package(self, pkg_name):
        """TODO: Docstring for find_package.

        :pkg_name: TODO
        :returns: TODO

        """
        for src_name, src in self.downloader.download_src.iteritems():
            result = self.downloader.find_package(src_name, pkg_name)
            if result is not None:
                return result
        return None

class PackageSource(object):
    """Docstring for PackageSource. """

    def __init__(self):
        """TODO: to be defined1. """
        self.source_name = None
        self.source_type = PackageSource.DEFAULT
        self.uri = None
        self.auth_type = None

    def check_source(self):
        """TODO: Docstring for check_source.
        :returns: TODO

        """
        pass

    async def download(self, pkg, to):
        """TODO: Docstring for download.

        :to: TODO
        :returns: TODO

        """
        return 'SUCCESS'

    async def list(self):
        """TODO: Docstring for list.
        :returns: TODO

        """
        pass

    def package_details(self, package_name):
        """TODO: Docstring for package_details.

        :package_name: TODO
        :returns: TODO

        """
        pass

    async def find_package(self, package_name):
        """TODO: Docstring for find_package.

        :package_name: TODO
        :returns: TODO

        """
        pass

class PackageDownloader(object):
    """Docstring for PackageDownloader. """

    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(conf_path, constants.CONF_FILE_NAME))
        self.download_src_modules_paths = self.config.get(constants.PACKAGE_DOWNLOADER, constants.DOWNLOAD_SOURCE_HANDLERS)
        self.pkg_drop_in_loc = os.path.abspath(self.config.get(constants.PACKAGE_INSTALLER, constants.PKG_DROP_IN_LOC))
        self.download_src = {}
        for src in self.download_src_modules_paths:
            if os.path.exists(src):
                module_files = os.listdir(src)
                if module_files is not None:
                    for mod_file in module_files:
                        if os.path.isfile(os.path.join(src, mod_file)):
                            if mod_file.endswith(constants.MODULE_FILE_POST_FIX):
                                module_name = mod_file.rstrip(constants.MODULE_FILE_POST_FIX)
                                module = importlib.import_module(module_name)
                                for member in dir(module):
                                    obj = getattr(module, member)
                                    if inspect.isclass(obj) and issubclass(obj, PackageSource) and obj is not PackageSource:
                                        self.download_src[obj.source_name] = obj

    def download(self, src_name, package_name):
        """TODO: Docstring for download.
        :returns: TODO

        """
        if src_name is None or package_name is None:
            raise Exception('Source or Package name is null')
        if self.download_src.__contains__(src_name):
            downloader_class = self.download_src[src_name]
            downloader = downloader_class()
            return downloader.download(package_name, self.pkg_drop_in_loc)
        else:
            raise Exception('No such download source is configured...{0}'.format(src_name))

    def list_sources(self):
        """TODO: Docstring for list_sources.
        :returns: TODO

        """
        return self.download_src.keys if self.download_src is not None else []

    async def list_packages(self):
        """TODO: Docstring for list_packages.
        :returns: TODO

        """
        packages = []
        if self.download_src is not None and len(self.download_src) > 0:
            packages = [src.list() for src in self.download_src.values()]
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(packages))

        return packages

    def list_packages_from_src(self, source_name):
        """TODO: Docstring for list_packages_from_src.

        :source_name: TODO
        :returns: TODO

        """
        if source_name is not None and len(self.download_src) > 0:
            if self.download_src.__contains__(source_name):
                return self.download_src[source_name].list()
            else:
                raise Exception('No such download source configured...{0}'.format(source_name))
        else:
            raise Exception('No download source is configured')

    def find_package(self, src_name, pkg_name):
        """TODO: Docstring for find_package.
        :src_name: TODO
        :pkg_name: TODO
        :returns: TODO
        """
        if src_name is not None and pkg_name is not None:
            if self.download_src.__contains__(src_name):
                src = self.download_src[src_name]
                if src is not None:
                    return src.find_package(pkg_name)
                else:
                        raise Exception('Source is not initialized yet...{0}'.format(src_name))
            else:
                raise Exception('No such source configured...{0}'.format(src_name))
        else:
            raise Exception('Source and Package names can''t be null')

class PackageInstaller(object):
    """Installs the package on local system. This class interacts with :class:`PackageDownloader` or :class:`ArchiveManager` to complete its operation """
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
        else:
            logger.info('Package has been installed successfully...{0}'.format(package_name))

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
