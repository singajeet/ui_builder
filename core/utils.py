"""
Utility functions
"""
from os import path

def validate_file(file):
    """TODO: Docstring for validate_file.
    :file: TODO
    :returns: TODO
    """
    if path.exists(file):
        if path.getsize(file) <= 0 or path.isfile(path)==False:
            raise IOError('Can''t open file {0}'.format(file))
        else:
            raise IOError('File not found {0}'.format(file))

