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
""" Public """
CONF_FILE_NAME = 'ui_builder.cfg'
CONF_PATH = '.'
""" Private """
__CONFIG = configparser.ConfigParser()
__CONFIG.read(os.path.abspath(os.path.join(CONF_PATH, CONF_FILE_NAME)))
__UI_BUILDER_DB = 'ui_builder_db'

#misc------------------------------
""" Public """
MODULE_FILE_POST_FIX = '.py'

#package --------------------------
""" Private """
__PACKAGE_INSTALLER = 'PackageInstaller'
__PKG_DROP_IN_LOC = 'package_drop_in_loc'
__PKG_INSTALL_LOC = 'package_install_loc'
__PKG_FILE_EXT = 'package_file_extension'
__PKG_OVERWRITE_MODE = 'pkg_overwrite_mode'
__PACKAGE_MANAGER = 'PackageManager'
""" Public """
UI_BUILDER_DB_PATH = __CONFIG.get(__PACKAGE_INSTALLER, __UI_BUILDER_DB)
PACKAGE_FILE_EXTENSION = __CONFIG.get(__PACKAGE_INSTALLER, __PKG_FILE_EXT)

#download-------------------------------------------
""" Private """
__DOWNLOAD_CONFIG_SECTION = 'DownloadManager'
__DOWNLOAD_SOURCE_HANDLERS = 'download_source_handlers'
__DOWNLOADER_PLUGINS_CONF = 'downloader_plugins'
__SAVE_DOWNLOADS_TO = 'save_downloads_to'
""" Public """
DOWNLOADER_PLUGINS_PATH = __CONFIG.get(__DOWNLOAD_CONFIG_SECTION, __DOWNLOADER_PLUGINS_CONF)
SAVE_DOWNLOADS_TO_PATH = __CONFIG.get(__DOWNLOAD_CONFIG_SECTION, __SAVE_DOWNLOADS_TO)
DOWNLOAD_PLUGIN_FILTER = 'DownloadPlugins'

#components----------------------------------------
""" Private """
__COMPONENT_MANAGER = 'ComponentManager'

#commands--------------------------------------------
""" Private """
__COMMAND_BINDINGS = 'key_to_command_bindings'
__CMD_CONFIG_SECTION = 'CommandManager'
__OVERWRITE_COMMAND_MODE = 'overwrite_command_mode'
""" Public """
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
""" Public """
HTTP = 'http'
FTP = 'ftp'
LOCAL_DISK = 'local'
DEFAULT = 'default'

#parser--------------------------------------------
""" Public """
INSTANCE = 'instance'
PARSED_CMD_VALUES = 'parsed_cmd_values'
PARSED_OPTIONS = 'parsed_options'
PARSED_KW_OPTIONS = 'parsed_kw_options'

#tasks---------------------------------------------
""" Public """
class ThreadStatus(enum.Enum):
    """ThreadStatus related constants
    """
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
""" Private """
__PLUGIN_CONFIG_SECTION = 'Plugins'
__PKG_SOURCE_PLUGIN = 'source_plugins'
""" Public """
PKG_SOURCE_PLUGIN_PATH = __CONFIG.get(__PLUGIN_CONFIG_SECTION, __PKG_SOURCE_PLUGIN)
