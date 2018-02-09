"""
.. module:: filesystem
   :platform: Unix, Windows
   :synopsis: APIs related to file system

.. moduleauthor:: Ajeet Singh <singh.ajeet@gmail.com>
"""
from goldfinch import validFileName
import pathlib

class File(object):

    """Represents a file on file system """

    def __init__(self):
        """TODO: to be defined1. """
        self._name = None
        self._base_name = None
        self._ext = None
        self._base_path = None
        self._size = 0
        self._content = None
        self._exists = False

    def name():
        doc = "Full name of file"
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = validFileName(value)
            self._base_name = value[0:value.rindex('.')]
            self._ext = value[(value.rindex('.')+1):]
        def fdel(self):
            del self._name
        return locals()
    name = property(**name())

    def base_name():
        doc = "First part of filename which appears just before the last dot"
        def fget(self):
            return self._base_name
        return locals()
    base_name = property(**base_name())

    def ext():
        doc = "Second part of filename which appears after the last dot"
        def fget(self):
            return self._ext
        return locals()
    ext = property(**ext())

    def base_path():
        doc = "A valid directory location else None"
        def fget(self):
            return self._base_path
        def fset(self, value):
            self._base_path = value if pathlib.os.path.exists(value) else None
        def fdel(self):
            del self._base_path
        return locals()
    base_path = property(**base_path())

    def size():
        doc = "Size of the file on local file system"
        def fget(self):
            return self._size
        return locals()
    size = property(**size())

    def content():
        doc = "Content of the file in byte format"
        def fget(self):
            return self._content
        def fset(self, value):
            self._content = value
        def fdel(self):
            del self._content
        return locals()
    content = property(**content())

    def exists():
        doc = "Returns True if file exists else False"
        def fget(self):
            return self._exists
        return locals()
    exists = property(**exists())

    def copy(self, destination, force=False, create_path=False):
        """Copy file to new location passed as param. If file already exists and force param is True, it will overwrite the destination file else will return with no operation.

        Args:
            destination (str): The target location where file needs to be copied
            force (bool): If set to True, it will overwrite the file in destination
            create_path (bool): create the destination path if not exists
        """
        dest_path = pathlib.Path(destination)
        if dest_path.exists():
            if dest_path.is_dir():
                dest_file = dest_path.joinpath(self.name)
                if dest_file.exists() and force == True:
                    dest_file.unlink()
                    dest_file.write_bytes(self.content)
                    return dest_file
                elif dest_file.exists() and force == False:
                    return None
                else:
                    dest_file.write_bytes(self.content)
                    return dest_file
            else:
                dest_file = pathlib.Path(dest_path)
                if force == True:
                    dest_file.unlink()
                    dest_file.write_bytes(self.content)
                    return dest_file
                else:
                    return None
        elif create_path == True:
            dest_path = dest_path.mkdir(parents=True)
            dest_file = dest_path.joinpath(self.name)
            dest_file.write_bytes(self.content)
            return dest_file
        else:
            raise Exception('Invalid destination path')
