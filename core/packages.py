import ConfigParser
import uuid
import os
import zipfile


PACKAGE_MANAGER='PackageManager'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'

class PackageManager(object):

    """Docstring for PackageManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.expanduser('~/.uo_builder'))
        self._pkg_install_location = self._config.get(PACKAGE_MANAGER, PKG_INSTALL_LOC)
        self._archive_manager = ArchiveManager()

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

    def get_archive_files_list(self):
        self.archive_files = self.archive_manager.load_archives()


class ArchiveManager(object):

    """Docstring for ArchiveManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.expanduser('~/.ui_builder.cfg'))
        self._archive_drop_location = self._config.get(PACKAGE_MANAGER, PKG_DROP_IN_LOC)
        self._archive_file_list = None

    def config():
        doc = "The config property."
        def fget(self):
            return self._config
        def fset(self, value):
            self._config = value
        def fdel(self):
            del self._config
        return locals()
    config = property(**config())

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
                    util.validate_file(file_path)
                    if zipfile.is_zipfile(file_path):
                        self.archive_file_list.append(file_path)
                    else:
                        print('File is not zipped and is skipped...{0}'.format(file))
                except:
                    print('Invalid file and is skipped...{0}'.format(file))
            else:
                print('Not a file and is skipped...{0}'.format(file))

            return self.archive_file_list

