"""
tasks.py
Description:
    Threads & Async provider lib
Author:
    Ajeet Singh
Date:
    2/4/2018
"""
from ui_builder.core import constants
from ui_builder.core.provider import id_mgr
from threading import Thread
import asyncio


class HybridTask(Thread):

    """Docstring for HybridTask. """

    def __init__(self, group=None, target=None,name=None, args=(), kwargs={}):
        """TODO: to be defined1. """
        super(HybridThread, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
        self.loop = asyncio.new_event_loop()

    def start(self):
        """TODO: Docstring for start.

        :arg1: TODO
        :returns: TODO

        """
        super(HybridThread, self).start()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


