"""
.. module:: installer
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import configparser
import os
import glob
from ui_builder.core import constants
from tinydb import TinyDB, Query
from ui_builder.core.service.package.models import PackageInfo
from ui_builder.core.service.component import manager


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
        self.pkg_install_location = os.path.abspath(self._config.get(constants.PACKAGE_INSTALLER, constants.PKG_INSTALL_LOC))
        logger.debug('Packages will be installed in following location...{0}'.format(self.pkg_install_location))
        self.package_manager = package_manager
        self.component_manager = manager.ComponentManager(package_manager.db_connection)

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
        db = TinyDB(constants.UI_BUILDER_DB_PATH)
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
