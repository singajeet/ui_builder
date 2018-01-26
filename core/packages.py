import utils
import ConfigParser
import uuid
import os
import zipfile
from jinja2 import BaseLoader,TemplateNotFound,Template,Environment


PACKAGE_MANAGER='PackageManager'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'

class ComponentLoader(BaseLoader):

    """Docstring for ComponentLoader. """

    def __init__(self):
        """TODO: to be defined1. """
        BaseLoader.__init__(self, path)
        self.path = path

    def get_source(self, environment, template):
        """TODO: Docstring for get_source.

        :environment: TODO
        :returns: TODO

        """
        path = os.path.join('./', template)
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            with file(path) as f:
                source = f.read().decode('utf-8')
                return source, path, lambda: mtime == os.path.getmtime(path)

class Component(object):

    """Docstring for Component. """

    def __init__(self, name, path):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self.name = None
        self.description = None
        self.type = None
        self.author = None
        self.version = None
        self._base_path = path
        self.template_path = os.path.join(self._base_path, '{0}.html'.format(name))
        self.config_path = os.path.join(self._base_path,'{0}.comp'.format(self.name))
        self.security_id = None

    def load_component(self):
        """TODO: Docstring for load_component.
        :returns: TODO

        """
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(self.config_path)
        if self.name != self.config_file.get('Details', 'Name'):
            raise NameError('Can not load component as filename[{0}] and name in config does not match'.format(self.name))

        self.description = self.config_file.get('Details', 'Description')
        self.type = self.config_file.get('Details', 'Type')
        self.author = self.config_file.get('Details', 'Author')
        self.version = self.config_file.get('Details', 'Version')
        self.template_env = Environment(loader = ComponentLoader(self.template_path))


class Package(object):

    """Docstring for Package. """

    def __init__(self, location=None):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self.location = location
        self.config_file = None
        self.name = None
        self.description = None
        self.type = None
        self.author = None
        self.url = None
        self.company = None
        self.version = None
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

    def load_details(self):
        """TODO: Docstring for load_details.
        :returns: TODO

        """
        temp_pkg_files = os.path.listdir(self.location)
        conf_file = ''
        for f in temp_pkg_files:
            if d.endswith('.pkg'):
                conf_file = f
                break

        if conf_file == '':
            raise NameError('No config file found for this package')
        else:
            self.config_file = ConfigParser.ConfigParser()
            self.config_file.read(os.path.join(self.location, conf_file))
            self.name = self.config_file.get('Details', 'Name')
            self.description = self.config_file.get('Details', 'Description')
            self.type = self.config_file.get('Details', 'Type')
            self.author = self.config_file.get('Details', 'Author')
            self.url = self.config_file.get('Details', 'Url')
            self.version = self.config_file.get('Details', 'Version')
            self.company = self.config_file.get('Details', 'Company')
            self._comp_name_list = self.config_file.get('Details', 'Components').split(',')

    def get_comp_name_list(self):
        """TODO: Docstring for get_comp_name_list.
        :returns: TODO

        """
        if self._comp_name_list is not None:
            return self._comp_name_list
        else:
            self.load_details()
            return self._comp_name_list

    def load_components(self):
        """TODO: Docstring for load_components.
        :returns: TODO

        """
        if self._comp_name_list is None:
            self.load_details()

        if self._comp_name_list is not None:
            for comp_name in self._comp_name_list:
                comp_path = os.path.join(self.location, comp_name.strip())
                comp = Component(comp_name, comp_path)
                comp.load_component()
                self._components[comp_name] = comp
                self._comp_name_id_map[comp.id] = comp
        else:
            raise Exception('Can not load components of package...{0}'.format(self.name))

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

    """Docstring for PackageManager. """

    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path,'ui_builder.cfg'))
        self.pkg_install_location = self._config.get(PACKAGE_MANAGER, PKG_INSTALL_LOC)
        self.archive_manager = ArchiveManager()

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

    def load_packages(self):
        """TODO: Docstring for load_packages.
        :returns: TODO

        """
        self._get_archive_files_list()
        self.install_packages()

    def activate_packages(self):
        """TODO: Docstring for activate_packages.

        :arg1: TODO
        :returns: TODO

        """
        pass

    def activate_package(self, package_id):
        """TODO: Docstring for activate_package.
        :returns: TODO

        """
        pass

    def deactivate_package(self, package_id):
        """TODO: Docstring for deactivate_package.

        :package_id: TODO
        :returns: TODO

        """
        pass

    def install_packages(self):
        """TODO: Docstring for install_packages.

        :arg1: TODO
        :returns: TODO

        """
        for file in self.archive_files:
            self._extract_package(file)

    def install_package(self, package_id):
        """TODO: Docstring for install_package.

        :package_id: TODO
        :returns: TODO

        """
        pass

    def _extract_package(self, file):
        """TODO: Docstring for extract_package.

        :file: TODO
        :returns: TODO

        """
        zip_pkg = zipfile.ZipFile(file)
        parent_dir = os.path.dirname(file)
        zip_pkg.extractall(parent_dir)

    def _validate_package(self, arg1):
        """TODO: Docstring for validate_package.

        :arg1: TODO
        :returns: TODO

        """
        pass

    def _register_package(self, package_location):
        """TODO: Docstring for install_package.
        :returns: TODO

        """
        pass


class ArchiveManager(object):

    """Docstring for ArchiveManager. """

    def __init__(self, conf_path):
        """TODO: to be defined1. """
        self.id = uuid.uuid4()
        self._config = ConfigParser.ConfigParser()
        self._config.read(os.path.join(conf_path, 'ui_builder.cfg'))
        self.archive_drop_location = os.path.abspath(self._config.get(PACKAGE_MANAGER, PKG_DROP_IN_LOC))
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
                        print('File is not zipped and is skipped...{0}'.format(file))
                except Exception as msg:
                    print('Invalid file and is skipped...{0}'.format(file))
            else:
                print('Not a file and is skipped...{0}'.format(file))

        return self.archive_file_list
