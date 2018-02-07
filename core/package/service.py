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
import importlib
import inspect
import asyncio
from tinydb import TinyDB, Query, where
from ui_builder.core.package import package_commands


#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)

class ComponentInfo(object):
    """Docstring for Component. """

    def __init__(self, name, path):
        """TODO: to be defined1. """
        self.id = None
        self.name = name
        self.description = None
        self.type = None
        self.author = None
        self.version = None
        self.is_enabled = True
        self.is_installed = False
        self.base_parent_id = None
        self.base_path = path
        self.template_path = os.path.join(path, '{0}.html'.format(name))
        self.config_path = os.path.join(path,'{0}.comp'.format(name))
        self.security_id = None
        self.package_dependencies = {}
        self.component_dependencies = {}

    def _load_component_config(self):
        """TODO: Docstring for load_component.
        :returns: TODO

        """
        self.config_file = utils.CheckedConfigParser()
        self.config_file.read(self.config_path)
        if self.name != self.config_file.get('Details', 'Name'):
            err = 'Can not load component as filename[{0}] and name in config does not match'.format(self.name)
            logger.error(err)
            raise NameError(err)

        self.id = self.config_file.get_or_none('Details', 'Id')
        self.description = self.config_file.get_or_none('Details', 'Description')
        self.type = self.config_file.get_or_none('Details', 'Type')
        self.author = self.config_file.get_or_none('Details', 'Author')
        self.version = self.config_file.get_or_none('Details', 'Version')
        self.package_dependencies = self.config_file.items('PackageDependencies') if self.config_file.has_section('PackageDependencies') else {}
        self.component_dependencies = self.config_file.items('ComponentDependencies') if self.config_file.has_section('ComponentDependencies') else {}
        logger.info('Component loaded successfully...{0}'.format(self.name))

    def load_details(self, comp_id, db_conn):
        """TODO: Docstring for load_details.
        :returns: TODO

        """
        logger.debug('Loading details for component [{0}] from db'.format(comp_id))
        if db_conn is not None:
            comp_table = db_conn.table('Components')
            Comp = Query()
            comp_record = comp_table.get(Comp['Details']['id'] == comp_id)
            if comp_record is not None:
                self.__dict__ = comp_record['Details']
            else:
                logger.warn('Unable load details for comp [{0}] from db'.format(comp_id))
            logger.debug('Details loaded succeasfully for component...{0}'.format(self.name))
        else:
            err = 'Database connection is invalid; Can''t load component details for...{0}'.format(comp_id)
            logger.error(err)
            raise Exception(err)

class PackageInfo(object):
    """Docstring for Package. """

    def __init__(self, location=None):
        """TODO: to be defined1. """
        self.id = None
        self.location = location
        self.config_file = None
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
        doc = "The config_file property."
        def fget(self):
            return self._config_file
        def fset(self, value):
            self._config_file = value
        def fdel(self):
            del self._config_file
        return locals()
    config_file = property(**config_file())

    def location():
        doc = "The location property."
        def fget(self):
            return self._location
        def fset(self, value):
            self._location = value
        def fdel(self):
            del self._location
        return locals()
    location = property(**location())

    def is_enabled():
        doc = "The is_enabled property."
        def fget(self):
            return self._is_enabled
        def fset(self, value):
            self._is_enabled = value
        def fdel(self):
            del self._is_enabled
        return locals()
    is_enabled = property(**is_enabled())

    def is_installed():
        doc = "The is_installed property."
        def fget(self):
            return self._is_installed
        def fset(self, value):
            self._is_installed = value
        def fdel(self):
            del self._is_installed
        return locals()
    is_installed = property(**is_installed())

    def _load_pkg_config(self):
        """TODO: Will be called by installer only
        :returns: TODO

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
        """TODO: Docstring for load_components.
        :returns: TODO

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
        """TODO: Docstring for load_details.

        :arg1: TODO
        :returns: TODO

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
        """TODO: Docstring for get_comp_name_list.
        :returns: TODO

        """
        if self._comp_name_list is not None:
            return self._comp_name_list
        else:
            self.load_details()
            return self._comp_name_list

    def get_components(self):
        """TODO: Docstring for get_components.
        :returns: TODO

        """
        if self._components is not None:
            return self._components
        else:
            self.load_components()
            return self._components

        return None

    def get_component(self, comp_name):
        """TODO: Docstring for get_component.
        :returns: TODO

        """
        if self._comp_name_list is not None:
            return self._components[comp_name]

        return None

    def get_component_by_id(self, comp_id):
        if self._components is not None and self._comp_name_id_map is not None:
            if self._comp_name_id_map[comp_id] is not None:
                return self._comp_name_id_map[comp_id]
            else:
                return None
        else:
            return None

class PackageManager(object):
    def __init__(self, conf_path):
        """TODO: Docstring for __init__.
        :conf_path: TODO
        :returns: TODO
        """
        logger.info('Starting PackageManager...')
        self.packages_map = {}
        self.packages_name_id_map = {}
        self.key_binding_config = ConfigParser.ConfigParser()
        self.key_binding_config.read(os.path.join(conf_path, '{0}.cfg'.format(COMMAND_BINDINGS)))
        self._load_key_command_bindings()
        logger.debug('Loading PackageManager Configuration...{0}'.format(conf_path))
        self.id = None
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = os.path.abspath(self._config.get(PACKAGE_INSTALLER, PKG_INSTALL_LOC))
        ###Setup commands
        self.installer = PackageInstaller(conf_path)
        self.commands = package_commands.PackageCommands(self)
        self.commands.register_commands()
        self.downloader = PackageDownloader(conf_path)
        self.archive_mgr = ArchiveManager(conf_path)

    def packages_name_id_map():
        doc = "The packages_name_id_map property."
        def fget(self):
            return self._packages_name_id_map
        def fset(self, value):
            self._packages_name_id_map = value
        def fdel(self):
            del self._packages_name_id_map
        return locals()
    packages_name_id_map = property(**packages_name_id_map())

    def packages_map():
        doc = "The packages_map property."
        def fget(self):
            return self._packages_map
        def fset(self, value):
            self._packages_map = value
        def fdel(self):
            del self._packages_map
        return locals()
    packages_map = property(**packages_map())

    def _load_key_command_bindings(self):
        for key, value in self.key_binding_config.items(PACKAGE_MANAGER):
            self._key_to_command_mapping[key] = value

    def load_package(self, pkg_name):
        """TODO: Docstring for load_package.
        :returns: TODO
        """
        _db = TinyDB(UI_BUILDER_DB_PATH)
        _pkg_table = _db.table('Package_Index')
        _pkg = _pkg_table.get(Query()['name'] == pkg_name)
        if _pkg is not None:
            pkg = PackageInfo('')
            pkg.load_details(_pkg.id, _db)
            self.packages_name_id_map[_pkg.name]=_pkg.id
            self.packages_map[_pkg.id] = pkg

    def load_packages(self):
        """TODO: Docstring for load_packages.
        :returns: TODO
        """
        _db = TinyDB(UI_BUILDER_DB_PATH)
        _package_table = _db.table('Package_Index')
        _all_packages = _package_table.all()
        for  pkg_record in _all_packages:
            pkg = PackageInfo('')
            pkg.load_details(pkg_record.id, _db)
            self.packages_name_id_map[pkg_record.name] = pkg_record.id
            self.packages_map[pkg_record.id] = pkg
        logger.debug('Packages map has been initialized successfully!')

    def install_package(self, file_name):
        """TODO: Docstring for install_package.
        :arg1: TODO
        :returns: TODO
        """
        if self.archive_mgr.is_package_available(file_name):
            self.installer.install_package(file_name)
        else:
            status = self.download_package(file_name)
            if status == 'SUCCESS':
                self.installer.install_package(file_name)
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
                for comp in self._comp_name_list:
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
    """Docstring for PackageInstaller. """
    def __init__(self, conf_path):
        """TODO: to be defined1. """
        logger.debug('Loading PackageInstaller Configuration...{0}'.format(conf_path))
        self.id = None
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = os.path.abspath(self._config.get(PACKAGE_INSTALLER, PKG_INSTALL_LOC))
        logger.debug('Packages will be installed in following location...{0}'.format(self.pkg_install_location))
        self.archive_manager = ArchiveManager(conf_path)
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


    def archive_manager():
        doc = "The archive_manager property."
        def fget(self):
            return self._archive_manager
        def fset(self, value):
            self._archive_manager = value
        def fdel(self):
            del self._archive_manager
        return locals()
    archive_manager = property(**archive_manager())

    def archive_files():
        doc = "The archive_files property."
        def fget(self):
            return self._archive_files
        def fset(self, value):
            self._archive_files = value
        def fdel(self):
            del self._archive_files
        return locals()
    archive_files = property(**archive_files())

    def _get_archive_files_list(self):
        self.archive_files = self.archive_manager.load_archives()

    def uninstall_package(self, package_name):
        """TODO: Docstring for uninstall_packages.

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

    def install_packages(self):
        """TODO: Docstring for install_packages.
        :arg1: TODO
        :returns: TODO
        """
        self._get_archive_files_list()
        for file in self.archive_files:
            self.install_package(file)

    def install_package(self, file_name):
        """TODO: Docstring for install_package.
        :returns: TODO
        """
        file = self.archive_manager.load_archive(file_name)
        pkg_path = self._extract_package(file)
        pkg = self._validate_package(pkg_path)
        registered = self._register_package(pkg)
        if registered == False:
            logger.warn('Unable to register pkg from the following file, check logs for more info...{0}'.format(pkg_path))
        else:
            logger.info('Package from following file is installed...{0}'.format(pkg_path))

    def _extract_package(self, file):
        """TODO: Docstring for extract_package.
        :file: TODO
        :returns: TODO
        """
        logger.debug('Extracting package content...{0}'.format(file))
        pkg_overwrite_mode = self._config.get(PACKAGE_INSTALLER, PKG_OVERWRITE_MODE)
        pkg_file_name = os.path.basename(file)
        pkg_dir_name = os.path.join(self.pkg_install_location, pkg_file_name.rstrip('.zip'))
        if pkg_overwrite_mode.upper() == 'on'.upper():
            logger.info('Overwrite mode is on, package content will be replaced with new files')
            if os.path.exists(pkg_dir_name):
                shutil.rmtree(pkg_dir_name)
        zip_pkg = zipfile.ZipFile(file)
        zip_pkg.extractall(self.pkg_install_location)
        logger.debug('Pkg extracted to...{0}'.format(pkg_dir_name))
        return pkg_dir_name

    def _validate_package(self, pkg_path):
        """TODO: Docstring for validate_package.
        :pkg_path: TODO
        :returns: TODO
        """
        logger.debug('Validating package at location...{0}'.format(pkg_path))
        #find .pkg files
        pkg_file = glob.glob(os.path.join(pkg_path, '*.pkg'))
        if len(pkg_file) == 1:
            pkg = Package(pkg_path)
            logger.debug('Package definition found at...{0}'.format(pkg_file[0]))
            return pkg
        elif len(pkg_file) > 1:
            logger.warn('Multiple .pkg files found. A valid package should have only one .pkg file')
            return None
        else:
            logger.warn('No .pkg file found. A package should have exactly one .pkg file')
        return None

    def _register_package(self, pkg):
        """TODO: Docstring for install_package.
        :returns: TODO
        """
        logger.debug('Loading package details stored at...{0}'.format(pkg._location))
        pkg._load_pkg_config()
        logger.debug('Open connection to database: {0}'.format(UI_BUILDER_DB_PATH))
        #global UI_BUILDER_DB_PATH
        db = TinyDB(UI_BUILDER_DB_PATH)
        q = Query()
        pkg_table = db.table('Packages')
        pkg.is_enabled = True
        pkg.is_installed = True
        pkg_details = pkg.__dict__.copy()
        #we will not save config and component objects
        pkg_details['_config_file'] = None
        pkg_details['_components'] = None
        pkg_entry = pkg_table.upsert({'Location':pkg._location, 'Details':pkg_details}, q['Details']['id'] == pkg.id)
        logger.debug('Package with name [{0}] and id [{1}] has been registered'.format(pkg.name, pkg.id))
        pkg_idx_table = db.table('Package_Index')
        idx_q = Query()
        pkg_idx = pkg_idx_table.upsert({'Id':pkg.id, 'Name':pkg.name}, idx_q['Id'] == pkg.id)
        logger.debug('Processing child components now...')
        comp_table = db.table('Components')
        for name, comp in pkg._components.iteritems():
            comp_details = comp.__dict__.copy()
            comp_details['config_file'] = None
            comp_details['template_env'] = None
            comp_q = Query()
            comp_entry = comp_table.upsert({'Location':comp.base_path, 'Details':comp_details}, comp_q['Details']['id'] == comp.id)
            logger.debug('Component with name [{0}] and id [{1}] has been registered under package [{2}]'.format(comp.name, comp.id, pkg.name))
            comp_idx_table = db.table('Components_Index')
            comp_idx_q = Query()
            comp_idx = comp_idx_table.upsert({'Id':comp.id, 'Name':comp.name, 'Package_Id':pkg.id, 'Package_Name':pkg.name}, comp_idx_q['Id'] == comp.id)
        return True

class ArchiveManager(object):
    """Docstring for ArchiveManager. """
    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path, 'ui_builder.cfg'))
        self.archive_drop_location = os.path.abspath(self._config.get(PACKAGE_INSTALLER, PKG_DROP_IN_LOC))
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

    def load_archive(self, file_name):
        """TODO: Docstring for load_archive.
        :returns: TODO

        """
        for file in os.listdir(self.archive_drop_location):
            if file == file_name:
                file_path = os.path.join(self.archive_drop_location, file)
                if os.path.isfile(file_path):
                    try:
                        utils.validate_file(file_path)
                        if zipfile.is_zipfile(file_path):
                            return file_path
                        else:
                            logger.debug('File is not zipped and is skipped...{0}'.format(file))
                    except Exception as msg:
                        logger.warn('Invalid file and is skipped...{0}'.format(file))

    def load_archives(self):
        """TODO: Docstring for load_archives.
        :returns: TODO

        """
        self.archive_file_list = []
        for file in os.listdir(self.archive_drop_location):
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

        return self.archive_file_listi

    def is_package_available(self, pkg_file_name):
        """TODO: Docstring for is_package_available.
        :pkg_file_name: TODO
        :returns: TODO
        """
        if pkg_file_name is not None:
            if pkg_file_name.endswith('.pkg'):
                pkg_file = os.path.join(self.archive_drop_location, pkg_file_name)
            else:
                pkg_file_name = '{0}.pkg'.format(pkg_file_name)
                pkg_file = os.path.join(self.archive_drop_location, pkg_file_name)
            if os.path.exists(pkg_file):
                return True
            else:
                return False
        else:
            return False
