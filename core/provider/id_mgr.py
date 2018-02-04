"""
id.py
Description:
    Manages UUID/GUID for whole application
Author:
    Ajeet Singh
Date:
    2/4/2018
"""
import uuid
import tinydb
import configparser
import os
from ui_builder.core import constants


def init_tb():
    """TODO: to be defined1. """
    _config = configparser.ConfigParser()
    _config.read(os.path.join(os.path.abspath(constants.CONF_PATH), 'ui_builder.cfg'))
    _db = tinydb.TinyDB(constants.UI_BUILDER_DB_PATH)
    _id_table = self._db.table('app_ids')
    return _id_table

def all_id():
    """TODO: Docstring for get.

    :arg1: TODO
    :returns: TODO

    """
    return init_db().all()

def get_id(obj_name):
    """TODO: Docstring for get_id.
    :returns: TODO

    """
    table = init_db()
    _id = table.get(tinydb.Query()['obj_name'] == obj_name)
    if _id is not None:
        return _id
    else:
        _id = uuid.uuid4()
        table.insert({'obj_name':obj_name, 'id':_id})
        return _id

