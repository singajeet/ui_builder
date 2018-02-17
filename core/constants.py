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


#init----------------------------------------
CONF_FILE_NAME = 'ui_builder.cfg'
CONF_PATH = '.'

_config = configparser.ConfigParser()
_config.read(os.path.abspath(os.path.join(CONF_PATH, CONF_FILE_NAME)))

UI_BUILDER_DB = 'ui_builder_db'

#misc------------------------------
MODULE_FILE_POST_FIX = '.py'

#package --------------------------
PACKAGE_DOWNLOADER = 'PackageDownloader'
DOWNLOAD_SOURCE_HANDLERS = 'download_source_handlers'
PACKAGE_INSTALLER='PackageInstaller'
PKG_DROP_IN_LOC='package_drop_in_loc'
PKG_INSTALL_LOC='package_install_loc'
PKG_FILE_EXT='package_file_extension'
PKG_OVERWRITE_MODE='pkg_overwrite_mode'
PACKAGE_MANAGER = 'PackageManager'
UI_BUILDER_DB_PATH = _config.get(PACKAGE_INSTALLER, UI_BUILDER_DB)
PACKAGE_FILE_EXTENSION = _config.get(PACKAGE_INSTALLER, PKG_FILE_EXT)
#components----------------------------------------
COMPONENT_MANAGER='ComponentManager'

#commands--------------------------------------------
COMMAND_BINDINGS = 'key_to_command_bindings'
CMD_CONFIG_SECTION = 'CommandManager'
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

#??---------------------------------------------
HTTP = 'http'
FTP = 'ftp'
LOCAL_DISK = 'local'
DEFAULT = 'default'

#parser--------------------------------------------
INSTANCE = 'instance'
PARSED_CMD_VALUES = 'parsed_cmd_values'
PARSED_OPTIONS = 'parsed_options'
PARSED_KW_OPTIONS = 'parsed_kw_options'

#tasks---------------------------------------------
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

#plugins----------------------------------
PLUGIN_CONFIG_SECTION = 'Plugins'
PKG_SOURCE_PLUGIN = 'source_plugins'
PKG_SOURCE_PLUGIN_PATH = _config.get(PLUGIN_CONFIG_SECTION, PKG_SOURCE_PLUGIN)

