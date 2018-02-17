"""
.. module:: models
   :platform: Unix, Windows
   :synopsis: Components models API's

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import os
import logging
from tinydb import Query
from ui_builder.core import utils, init_log


#init logs---------------------------------
init_log.config_logs()
LOGGER = logging.getLogger(__name__)


class BaseComponentInfo(object):
    """Represents an component in package management system. \
            A component is an object which can contain logic (in form of code),
        resources (image, configuration, etc) and other similar objects.
    """

    def __init__(self, name, path):
        """An :class:`BaseComponentInfo` constructor requires two params -

        Args:
            name (str): Name of the component
            base_path (str): A directory location which contains templates, \
                    config files, etc
        """
        self.component_id = None
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

    def load_details(self, comp_id, db_conn):
        """Load details of component from database once component has been installed

        Args:
            component_id (uuid): A unique :class:`uuid.uuid`id assigned to the component
            connection (object): An open connection to metadata object
        """
        pass

class ComponentInfo(BaseComponentInfo):
    """Represents an component in package management system. A component is \
            an object which can contain logic (in form of code), resources \
            (image, configuration, etc) and other similar objects. \
            :class:`ComponentInfo` class contains the details about an \
            component like, source code, compiled code, templates, version, \
            dependency on other components, etc
    """

    def __init__(self, name, path):
        super(ComponentInfo, self).__init__(name, path)
        """An :class:`ComponentInfo` constructor requires two params -
        Args:
            name (str): Name of the component
            base_path (str): A directory location which contains templates, \
                    config files, etc
        """
        self.component_id = None
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
        self.config_path = os.path.join(path, '{0}.comp'.format(name))
        self.config_file = None
        self.security_id = None
        self.package_dependencies = {}
        self.component_dependencies = {}

    def load_install_config(self):
        """Loads details of component from local config file.
            Config filename and component name should match else component \
                    will not load. This function will be used by the \
                    :class:`PackageInstaller` class only
        """
        self.config_file = utils.CheckedConfigParser()
        self.config_file.read(self.config_path)
        if self.name != self.config_file.get('Details', 'Name'):
            err = 'Can not load component as filename[%s] and name \
                    in config does not match' % self.name
            LOGGER.error(err)
            raise NameError(err)
        self.component_id = self.config_file.get_or_none('Details', 'Id')
        self.description = self.config_file.get_or_none('Details', 'Description')
        self.kind = self.config_file.get_or_none('Details', 'Kind')
        self.author = self.config_file.get_or_none('Details', 'Author')
        self.version = self.config_file.get_or_none('Details', 'Version')
        self.package_dependencies = self.config_file\
                .items('PackageDependencies') if self.config_file\
                .has_section('PackageDependencies') else {}
        self.component_dependencies = self.config_file\
                .items('ComponentDependencies') if self\
                .config_file.has_section('ComponentDependencies') else {}
        LOGGER.info('Component loaded successfully...%s', self.name)

    def load_details(self, comp_id, db_conn):
        """Load details of component from database once component has \
                been installed

        Args:
            comp_id (uuid): A unique :class:`uuid.uuid`id assigned to the \
                    component
            db_conn (object): An open connection to metadata database
        """
        LOGGER.debug('Loading details for component [%s] from db', comp_id)
        if db_conn is not None:
            comp_table = db_conn.table('Components')
            query = Query()
            comp_record = comp_table.get(query['Details']['id'] == comp_id)
            if comp_record is not None:
                self.__dict__ = comp_record['Details']
            else:
                LOGGER.warn('Unable load details for comp [%s] from db', comp_id)
            LOGGER.debug('Details loaded succeasfully for component...%s', self.name)
        else:
            err = 'Database connection is invalid; Can''t load \
                    component details for...%s' % comp_id
            LOGGER.error(err)
            raise Exception(err)
