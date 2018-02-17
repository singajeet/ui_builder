"""
.. module:: package
   :platform: Unix, Windows
   :synopsis: Package management functionality

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import aiohttp

class Web(object):
    """Provides session for accessing web resources
    """

    __single_web_session = None

    def __new__(cls, *args, **kwargs):
        """Class instance creator
        """
        if cls != type(cls.__single_web_session):
            cls.__single_web_session = object.__new__(cls, *args, **kwargs)
        return cls.__single_web_session

    def __init__(self):
        """Web session instance creator
        """
        if self._SESSION is None:
            self._SESSION = aiohttp.ClientSession()

    @property
    def SESSION(self):
        """A single instance web session property
        """
        return self._SESSION
