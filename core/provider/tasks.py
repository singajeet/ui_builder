"""
tasks.py
Description:
    Threads & Async provider lib
Author:
    Ajeet Singh
Date:
    2/4/2018
"""
from ui_builder.core import constants, id_mgr


class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.id = id_mgr.get_id('ThreadManager')

