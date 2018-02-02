"""
Utility functions
"""
from os import path
import ConfigParser

def validate_file(file):
    """TODO: Docstring for validate_file.
    :file: TODO
    :returns: TODO
    """
    if path.exists(file):
        if path.getsize(file) <= 0 or path.isfile(file)==False:
            raise IOError('Can''t open file {0}'.format(file))
    else:
        raise IOError('File not found {0}'.format(file))

class FormattedStr(object):

    """Docstring for FormattedStr. """

    def __init__(self):
        """TODO: to be defined1. """
        self.formatted_txt = ''

    def format(self, label, val):
        """TODO: Docstring for format.
        :returns: TODO

        """
        self.formatted_txt += '{0}: {1}\n'.format(label, val)

    def get_str(self):
        """TODO: Docstring for get_str.
        :returns: TODO

        """
        return self.formatted_txt

    def print_str(self):
        """TODO: Docstring for print.
        :returns: TODO

        """
        if self.formatted_txt != '':
            print(self.formatted_txt)


class CheckedConfigParser(ConfigParser.ConfigParser):
    def get_or_none(self, section, option):
        """TODO: Docstring for get_or_none.

        :section: TODO
        :option: TODO
        :returns: TODO

        """
        if self.has_section(section) and self.has_option(option):
            return self.get(section, option)
        else:
            return None
