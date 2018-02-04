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

_id_table = None

def _init_tb():
    """TODO: to be defined1. """
    _config = configparser.ConfigParser()
    _config.read(os.path.join(os.path.abspath(constants.CONF_PATH), 'ui_builder.cfg'))
    _db = tinydb.TinyDB(constants.UI_BUILDER_DB_PATH)
    _id_table = _db.table('app_ids')

def _check_db():
    """TODO: Docstring for _check_db.
    :returns: TODO

    """
    if _id_table is None:
        _init_tb()
        if _id_table is None:
            raise Exception('Can''t find the ID''s table. Kindly check configured metadata database')

def all_id():
    """TODO: Docstring for get.

    :arg1: TODO
    :returns: TODO

    """
    _check_db()
    return _id_table.all()

def get_id(obj_name):
    """TODO: Docstring for get_id.
    :returns: TODO

    """
    _check_db()
    _id = _id_table.get(tinydb.Query()['obj_name'] == obj_name)
    if _id is not None:
        return _id['id']
    else:
        _id = uuid.uuid4()
        _id_table.insert({'obj_name':obj_name, 'id':_id})
        return _id

def find_id(obj_name):
    """TODO: Docstring for find_id.
    :returns: TODO

    """
    _check_db()
    _id = _id_table.get(tinydb.Query()['obj_name'] == obj_name)
    return _id['id']

def find_name(obj_id):
    """TODO: Docstring for find_name.
    :returns: TODO

    """
    _check_db()
    _obj_name = _id_table.get(tinydb.Query()['id'] == obj_id)
    return _obj_name['obj_name']
