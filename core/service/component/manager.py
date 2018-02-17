"""
.. module:: manager
   :platform: Unix, Windows
   :synopsis: Components models API's

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import logging
from tinydb import Query
from ui_builder.core import init_log

#init logs---------------------------------
init_log.config_logs()
LOGGER = logging.getLogger(__name__)


class ComponentManager(object):
    """:class:`ComponentManager` will manage all different types of components \
            in the whole system. Any component "kind" should be registered \
            with :class:`ComponentManager` and any request to install, \
            activate, instance creation should go through this class
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
            self.component_id = _comp_mgr_record['Id']
            self.__registry_name = _comp_mgr_record['RegistryName']
            if self.__registry_name is not None:
                self.__registry_table = db_connection.tables(self.__registry_name)
                self.__registry_map = self.__registry_table.all()
            else:
                raise Exception('CRITICAL: Unable to initiate component manager. \
                                System load can''t continue further', \
                                'No registry name found for ComponentManager in \
                                system_managers table')
        else:
            raise Exception('CRITICAL: Unable to initiate component manager. \
                            System load can''t continue further', \
                            'No entry found for ComponentManager in \
                            system_managers table')

    def register(self, component_id, component_obj, parent_pkg):
        """Registers an instance of Component with ComponentManager
        Args:
            component_id (uuid): The unique id of component
            component_obj (BaseComponentInfo): An instance of ComponentInfo \
                    to be registered
            parent_pkg (BasePackageInfo): An instance of PackageInfo under \
                    which this component should be registered
        Returns:
            status (bool): Returns True if registered successfully else False
        """
        comp_details = component_obj.__dict__.copy()
        #config_file and template_env can be repopulate from the base_path, \
                #so no need to save it in database, this saves the effort \
                #required to serialize and saveing all sub-attributes under \
                #these attributes
        comp_details['config_file'] = None
        comp_details['template_env'] = None
        comp_table = self.__db_connection.table('Components')
        comp_q = Query()
        comp_table\
                .upsert({'Location':component_obj.base_path, \
                         'Details':comp_details}, \
                        comp_q['Details']['id'] == component_id.id)
        LOGGER.debug('Component with name [{0}] and id [{1}] has been \
                     registered under package [{2}]'\
                     .format(component_obj.name, component_obj.id, \
                             parent_pkg.name))
        comp_idx_table = self.__db_connection.table('Components_Index')
        comp_idx_q = Query()
        comp_idx_table.upsert({'Id':component_obj.id, \
                                          'Name':component_obj.name, \
                                          'Package_Id':parent_pkg.id, \
                                          'Package_Name':parent_pkg.name}, \
                                         comp_idx_q['Id'] == component_obj.id)
        return True
