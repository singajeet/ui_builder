"""
.. module:: components
   :platform: Unix, Windows
   :synopsis: Components management API's

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
from ui_builder.core import utils, init_log, constants
import configparser
import uuid
import os
import logging
import importlib
import inspect
from goldfinch import validFileName
from tinydb import TinyDB, Query, where

#init logs---------------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)


class BaseComponentInfo(object):
    """Represents an component in package management system. A component is an object which can contain logic (in form of code),
        resources (image, configuration, etc) and other similar objects.
    """

    def __init__(self, name, path):
        """An :class:`BaseComponentInfo` constructor requires two params -

        Args:
            name (str): Name of the component
            base_path (str): A directory location which contains templates, config files, etc
        """
        self.id = None
        self.name = name
        self.description = None
        self.kind = None
        self.author = None
        self.version = None
        self.is_enabled = True
        self.is_installed = False
        self.base_path = path
        self.security_id = None
        self.package_dependencies = {}
        self.component_dependencies = {}
        self.meta_data = {}

    def load_install_config(self):
        """Loads installation details of a component.
            This function will be used by the :class:`PackageInstaller` class only
        """
        pass

    def load_details(self, component_id, connection):
        """Load details of component from database once component has been installed

        Args:
            component_id (uuid): A unique :class:`uuid.uuid`id assigned to the component
            connection (object): An open connection to metadata object
        """
        pass

class ComponentManager(object):
    """:class:`ComponentManager` will manage all different types of components in the whole system. Any component "kind" should be registered with :class:`ComponentManager` and any request to install, activate, instance creation should go through this class

    Note:
        This is an singleton class and will be shared among objects
    """

    __single_component_manager = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_component_manager):
            cls.__single_component_manager = object.__new__(cls, *args, **kwargs)
        return cls.__single_component_manager

    def __init__(self, db_connection):
        """Init this singleton class with configuration provided as parameter

        Args:
            db_connection (str): Database connection to metadata
        """
        self.__db_connection = db_connection
        _mgr_table = db_connection.tables('system_managers')
        _comp_mgr_record = _mgr_table.get(Query['name'] == 'ComponentManager')
        if _comp_mgr_record is not None:
            self.id = _comp_mgr_record['Id']
            self.__registry_name = _comp_mgr_record['RegistryName']
            if self.__registry_name is not None:
                self.__registry_table = db_connection.tables(self.__registry_name)
                self.__registry_map = self.__registry_table.all()
            else:
                raise Exception('CRITICAL: Unable to initiate component manager. System load can''t continue further', 'No registry name found for ComponentManager in system_managers table')
        else:
            raise Exception('CRITICAL: Unable to initiate component manager. System load can''t continue further', 'No entry found for ComponentManager in system_managers table')

    def register(self, component_id, component_obj, parent_pkg):
        """Registers an instance of Component with ComponentManager

        Args:
            component_id (uuid): The unique id of component
            component_obj (BaseComponentInfo): An instance of ComponentInfo to be registered
            parent_pkg (BasePackageInfo): An instance of PackageInfo under which this component should be registered
        Returns:
            status (bool): Returns True if registered successfully else False
        """
        comp_details = component_obj.__dict__.copy()
        #config_file and template_env can be repopulate from the base_path, so no need to save it in database, this saves the effort required to serialize and saveing all sub-attributes under these attributes
        comp_details['config_file'] = None
        comp_details['template_env'] = None
        comp_table = self.__db_connection.table('Components')
        comp_q = Query()
        comp_entry = comp_table.upsert({'Location':component_obj.base_path, 'Details':comp_details}, comp_q['Details']['id'] == component_id.id)
        logger.debug('Component with name [{0}] and id [{1}] has been registered under package [{2}]'.format(component_obj.name, component_obj.id, parent_pkg.name))
        comp_idx_table = self.__db_connection.table('Components_Index')
        comp_idx_q = Query()
        comp_idx = comp_idx_table.upsert({'Id':component_obj.id, 'Name':component_obj.name, 'Package_Id':parent_pkg.id, 'Package_Name':parent_pkg.name}, comp_idx_q['Id'] == component_obj.id)
        return True
        

class ComponentInfo(BaseComponentInfo):
    """Represents an component in package management system. A component is an object which can contain logic (in form of code),
        resources (image, configuration, etc) and other similar objects. :class:`ComponentInfo` class contains the details about
        an component like, source code, compiled code, templates, version, dependency on other components, etc
    """

    def __init__(self, name, path):
        super(ComponentInfo, self).__init__(name, path)
        """An :class:`ComponentInfo` constructor requires two params -

        Args:
            name (str): Name of the component
            base_path (str): A directory location which contains templates, config files, etc
        """
        self.id = None
        self.name = name
        self.description = None
        self.kind = None
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

    def load_install_config(self):
        """Loads details of component from local config file.
            Config filename and component name should match else component will not load
            This function will be used by the :class:`PackageInstaller` class only
        """
        self.config_file = utils.CheckedConfigParser()
        self.config_file.read(self.config_path)
        if self.name != self.config_file.get('Details', 'Name'):
            err = 'Can not load component as filename[{0}] and name in config does not match'.format(self.name)
            logger.error(err)
            raise NameError(err)

        self.id = self.config_file.get_or_none('Details', 'Id')
        self.description = self.config_file.get_or_none('Details', 'Description')
        self.kind = self.config_file.get_or_none('Details', 'Kind')
        self.author = self.config_file.get_or_none('Details', 'Author')
        self.version = self.config_file.get_or_none('Details', 'Version')
        self.package_dependencies = self.config_file.items('PackageDependencies') if self.config_file.has_section('PackageDependencies') else {}
        self.component_dependencies = self.config_file.items('ComponentDependencies') if self.config_file.has_section('ComponentDependencies') else {}
        logger.info('Component loaded successfully...{0}'.format(self.name))

    def load_details(self, comp_id, db_conn):
        """Load details of component from database once component has been installed

        Args:
            comp_id (uuid): A unique :class:`uuid.uuid`id assigned to the component
            db_conn (object): An open connection to metadata database
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
