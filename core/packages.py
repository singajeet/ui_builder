import ConfigParser

PACKAGE_MANAGER='PackageManager'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'

class PackageManager(object):

    """Docstring for PackageManager. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

class ArchiveManager(object):

    """Docstring for ArchiveManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self._config = ConfigManager.ConfigManager()
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
            if os.path.isfile(file):
                try:
                    self._validate_file(file)
                    self.archive_file_list.append(file)
                except:
                    print('Invalid file and is skipped...{0}'.format(file))
            else:
                print('Not a file and is skipped...{0}'.format(file))

            return self.archive_file_list

