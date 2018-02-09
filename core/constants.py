"""
constants.py
Description:
Constant variables definition to be uses application wide
Author:
Ajeet Singh
"""
import configparser
import os
import enum

CONF_PATH = '.'

_config = configparser.ConfigParser()

print('Looking for conf file => {0}'.format(os.path.abspath(os.path.join(CONF_PATH, 'ui_builder.cfg'))))
_config.read(os.path.abspath(os.path.join(CONF_PATH,'ui_builder.cfg')))

#Consts for modules in 'package' lib --------------------------
PACKAGE_DOWNLOADER = 'PackageDownloader'
DOWNLOAD_SOURCE_HANDLERS = 'download_source_handlers'
PACKAGE_INSTALLER='PackageInstaller'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'
PKG_FILE_EXT='package_file_extension'
PKG_OVERWRITE_MODE='pkg_overwrite_mode'
UI_BUILDER_DB = 'ui_builder_db'
PACKAGE_MANAGER = 'PackageManager'
COMMAND_BINDINGS = 'key_to_command_bindings'

#global UI_BUILDER_DB_PATH
UI_BUILDER_DB_PATH = _config.get(PACKAGE_INSTALLER, UI_BUILDER_DB)
PACKAGE_FILE_EXTENSION = _config.get(PACKAGE_INSTALLER, PKG_FILE_EXT)
#--------------------------------------------

CONFIG_SECTION = 'CommandManager'
OVERWRITE_COMMAND_MODE = 'overwrite_command_mode'

class Commands(object):

    """Docstring for Commands. """

    SUCCESS = 0
    FAILED = 1
    SUCCESS_WARNING = 2
    WARNING = 4
    INVALID_COMMAND_OPTION = 8
    INVALID_COMMAND = 16
    INVALID_SUB_COMMAND_OPTION = 32
    INVALID_SUB_COMMAND = 64

#---------------------------------------------
HTTP = 'http'
FTP = 'ftp'
LOCAL_DISK = 'local'
DEFAULT = 'default'

#--------------------------------------------

INSTANCE = 'instance'
PARSED_CMD_VALUES = 'parsed_cmd_values'
PARSED_OPTIONS = 'parsed_options'
PARSED_KW_OPTIONS = 'parsed_kw_options'

CONF_FILE_NAME = 'ui_builder.cfg'

MODULE_FILE_POST_FIX = '.py'

#---------------------------------------------
class ThreadStatus(enum.Enum):
    INVALID = 0
    STOPPED = 1
    RUNNING = 2
    PAUSED = 4
    EVENT_LOOP_RUNNING = 8
    EVENT_LOOP_STOPPED = 16
    EVENT_LOOP_CLOSED = 32
    EVENT_LOOP_NO_CORO = 64
    EVENT_LOOP_INVALID = 128
