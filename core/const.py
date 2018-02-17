"""
.. module:: const
   :platform: Unix, Windows
   :synopsis: Components models API's

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import sys


class _const:
    class ConstError(TypeError):
        pass
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value
sys.modules[__name__] = _const()
