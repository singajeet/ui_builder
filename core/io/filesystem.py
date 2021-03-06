"""
.. module:: filesystem
   :platform: Unix, Windows
   :synopsis: APIs related to file system

.. moduleauthor:: Ajeet Singh <singh.ajeet@gmail.com>
"""
import os
from goldfinch import validFileName
import pathlib
import zipfile
import io
import shutil

class File(object):

    """Represents a file on file system. This class supports :meth:`copy` and :meth:`move` commands only and for all other operations use :mod:`os` or :mod:`pathlib` modules. There are two attributes :attr:`os` and :attr:`path` which provides access to both of the above mentioned modules respectively
    """

    def __init__(self, file_name, create_if_not_exists=False, base_path=None):
        """TODO: to be defined1. """
        self._base_path = None
        self._ext = None

        if create_if_not_exists == False:
            if file_name is None:
                raise Exception('Filename can''t have blank')
            if base_path is None:
                if file_name.find('~') >= 0:
                    src_file = pathlib.Path(file_name).expanduser()
                else:
                    src_file = pathlib.Path(file_name).absolute()
            else:
                if base_path.find('~') >= 0:
                    src_file = pathlib.Path(base_path).expanduser().joinpath(file_name).absolute()
                else:
                    src_file = pathlib.Path(base_path).absolute().joinpath(file_name).absolute()
            if src_file.exists():
                self.name = src_file.name
                self.base_path = src_file.parent.absolute()
                self.content = src_file.read_bytes()
                self._exists = True
                self._size = src_file.stat().st_size
                self.path = src_file.absolute()
            else:
                raise Exception('Invalid file provided')
        else:
            self.name = file_name
            self.base_path = base_path
            self._exists = False
            self._size = 0
            self.path = pathlib.Path()
            self.content = None
        self.os = os

    def name():
        doc = "Full name of file"
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = validFileName(value, initCap=False).decode() if type(validFileName(value, initCap=False)) != str else validFileName(value, initCap=False)
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
        Returns:
            file_path (pathlib.Path): Returns an instance of :class:`Path` if file copied else None
        """
        if destination is not None and destination.find('~') >= 0:
            dest_path = pathlib.Path(destination).expanduser()
        elif destination is not None:
            dest_path = pathlib.Path(destination).absolute()
        else:
            raise Exception('Invalid path provided - {0}'.format(dest_path))

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

    def move(self, destination, force=False, create_path=False):
        """Moves the current file to the destination. Please see :meth:`copy` for more information on arguments
        """
        new_file = self.copy(destination, force, create_path)
        if new_file is not None:
            if new_file.exists():
                old_file = pathlib.Path(self.base_path).joinpath(self.name)
                self.base_path = new_file.parent.absolute()
                old_file.unlink()
                return new_file
        return None

class PackageFile(File):

    """Represents a physical package file in the package management system. This class supports 4 commands...

            * copy
            * move
            * extract_to
    """

    def __init__(self, file_name, create_if_not_exists=False, base_path=None):
        """TODO: to be defined1. """
        super(PackageFile, self).__init__(file_name, create_if_not_exists, base_path)
        if self.exists:
            if not zipfile.is_zipfile(self.path._str):
                raise Exception('Not a valid zip file')

    def extract_to(self, target_path, name_as_sub_folder=True, overwrite=False):
        """Extract the contents of package to the specified path

        Args:
            target_path (str): path to the lication where package needs to be extracted
            name_as_sub_folder (bool): creates a sub folder under target_path with the same name as package file name before extracting contents. Default value is True
            overwrite (bool): Overwrites the contents if already exists in target location
        """
        if target_path is not None and target_path.find('~') >= 0:
            dest_path = pathlib.Path(target_path).expanduser()
        elif target_path is not None:
            dest_path = pathlib.Path(target_path).absolute()
        else:
            raise Exception('Can''t accept blank for destination path')
        if dest_path.exists():
            if name_as_sub_folder==True:
                dest_path = dest_path.joinpath(self.base_name).absolute()
                if not dest_path.exists():
                    dest_path.mkdir(parents=True)
            else:
                if overwrite == True:
                    for f in dest_path.iterdir():
                        if f.is_dir():
                            shutil.rmtree(f)
                        else:
                            f.unlink()
            if len(self.content) > 0:
                file_bytes = io.BytesIO(self.content)
                zippedfile = zipfile.ZipFile(file_bytes)
                zippedfile.extractall(dest_path)
            return dest_path
        else:
            raise Exception('Invalid destination path specified')
