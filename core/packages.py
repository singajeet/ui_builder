# coding=utf-8
import utils
import ConfigParser
import uuid
import os
import zipfile
import logging
import init_log
import shutil
import glob
from tinydb import TinyDB, Query, where
import commands


PACKAGE_INSTALLER='PackageInstaller'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'
PKG_OVERWRITE_MODE='pkg_overwrite_mode'
UI_BUILDER_DB = 'ui_builder_db'

PACKAGE_MANAGER = 'PackageManager'
COMMAND_BINDINGS = 'key_to_command_bindings'
#global UI_BUILDER_DB_PATH

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

    def _load_component_config(self):
        """TODO: Docstring for load_component.
        :returns: TODO

        """
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(self.config_path)
        if self.name != self.config_file.get('Details', 'Name'):
            err = 'Can not load component as filename[{0}] and name in config does not match'.format(self.name)
            logger.error(err)
            raise NameError(err)

        self.id = self.config_file.get('Details', 'Id')
        self.description = self.config_file.get('Details', 'Description')
        self.type = self.config_file.get('Details', 'Type')
        self.author = self.config_file.get('Details', 'Author')
        self.version = self.config_file.get('Details', 'Version')
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
            self.config_file = ConfigParser.ConfigParser()
            self.config_file.read(os.path.join(self.location, conf_file))
            self.id = self.config_file.get('Details', 'Id')
            self.name = self.config_file.get('Details', 'Name')
            self.description = self.config_file.get('Details', 'Description')
            self.type = self.config_file.get('Details', 'Type')
            self.author = self.config_file.get('Details', 'Author')
            self.url = self.config_file.get('Details', 'Url')
            self.version = self.config_file.get('Details', 'Version')
            self.company = self.config_file.get('Details', 'Company')
            self._comp_name_list = self.config_file.get('Details', 'Components').split(',')
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

class PackageCommand(object):

    """Docstring for PackageCommand. """
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    LIST = 'list'
    SHOW = 'show'

    def __init__(self, pkg_manager):
        """TODO: to be defined1. """
        self.package_manager = pkg_manager

    def register_commands(self, name, action):
        """TODO: Docstring for register_commands.
        :returns: TODO

        """
        cmd = commands.Command(name)
        act = commands.Action(action)
        cmd._actions.append(act)
        commands.CommandManager.register_command('Packages', name, cmd)

class PackageManager(object):
    def __init__(self, conf_path):
        """TODO: Docstring for __init__.

        :conf_path: TODO
        :returns: TODO

        """
        logger.info('Starting PackageManager...')
        self.key_binding_config = ConfigParser.ConfigParser()
        self.key_binding_config.read(os.path.join(conf_path, '{0}.cfg'.format(COMMAND_BINDINGS)))
        self._load_key_command_bindings()
        logger.debug('Loading PackageManager Configuration...{0}'.format(conf_path))
        self.id = None
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = os.path.abspath(self._config.get(PACKAGE_INSTALLER, PKG_INSTALL_LOC))
        global UI_BUILDER_DB_PATH
        UI_BUILDER_DB_PATH = self._config.get(PACKAGE_INSTALLER, UI_BUILDER_DB)
        ###Setup commands
        self.installer = PackageInstaller(conf_path)
        self.commands = PackageCommands(self)
        self.commands.register_commands()

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

    def load_packages(self):
        """TODO: Docstring for load_packages.
        :returns: TODO

        """
        self.packages_map = {}
        self.packages_name_id_map = {}
        _db = TinyDB(UI_BUILDER_DB_PATH)
        _package_table = _db.table('Package_Index')
        _all_packages = _package_table.all()
        for  pkg_record in _all_packages:
            pkg = PackageInfo('')
            pkg.load_details(pkg_record.id, _db)
            self.packages_name_id_map[pkg_record.name] = pkg_record.id
            self.packages_map[pkg_record.id] = pkg

        logger.debug('Packages map has been initialized successfully!')

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

class PackageDownloader(object):

    """Docstring for PackageDownloader. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

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

    def install_packages(self):
        """TODO: Docstring for install_packages.

        :arg1: TODO
        :returns: TODO

        """
        self._get_archive_files_list()
        for file in self.archive_files:
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
            pkg = PackageInfo(pkg_path)
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
        self.archive_file_list = None

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

        return self.archive_file_list
