# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from tkinter import Tk, filedialog
from typing import TextIO

# internal
from app_defines import DATE_MIN_DEFAULT, LAUCH_DATE, UTF8, Mem
from app_gui_base import ask_filename, get_curdir, getrootconf, int_vars, rootm, setrootconf, window_hcookiesm
from app_gui_defines import (
    CVARS,
    OPTION_VALUES_IMAGES,
    OPTION_VALUES_PARCHI,
    OPTION_VALUES_THREADING,
    OPTION_VALUES_VIDEOS,
    SLASH,
    Options,
)
from app_logger import trace
from app_module import ProcModule
from app_utils import as_date, normalize_path
from app_validators import (
    APIKeyKeyValidator,
    APIKeyUserIdValidator,
    BoolStrValidator,
    DateValidator,
    DummyValidator,
    FolderPathValidator,
    ImagesCBValidator,
    InfoSaveModeValidator,
    JsonValidator,
    ModuleValidator,
    ParchiCBValidator,
    ProxyTypeValidator,
    ProxyValidator,
    RetriesValidator,
    ThreadsCBValidator,
    TimeoutValidator,
    Validator,
    VideosCBValidator,
    WindowPosValidator,
)

__all__ = ('Settings',)


class Settings(ABC):
    """
    Settings !Static!
    """
    INITIAL_SETTINGS: list[str] = []
    AUTOCONFIG_FILENAMES: tuple[str, str, str, str] = ('ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg')
    on_proc_module_change_callback: Callable[[int], None] | None = None
    on_init_autocompletion_callback: Callable[[str], None] | None = None

    @abstractmethod
    def ___this_class_is_static___(self) -> ...:
        ...

    class Setting:
        def __init__(self, sconf: Options, check: Validator, check_fail_message: str) -> None:
            self.conf: Options = sconf
            self.type: type = check.get_value_type()
            self.check: Validator = check
            self.check_fail_message: str = check_fail_message or f'Invalid value \'%s\' for config id \'{self.conf.value:d}\''
            assert self.check_fail_message.count('%s') == 1

        def validate(self, val: int | str) -> bool:
            result = self.check(val)
            if result is False:
                trace(self.check_fail_message % str(val))
            return result

    settings = {
        'path': Setting(Options.PATH, DummyValidator(), ''),  # no validation, str
        'tags': Setting(Options.TAGS, DummyValidator(), ''),  # no validation, str
        'module': Setting(Options.MODULE, ModuleValidator(), 'Invalid module \'%s\'!'),
        'videos': Setting(Options.VIDSETTING, VideosCBValidator(), 'Invalid videos option \'%s\'!'),
        'images': Setting(Options.IMGSETTING, ImagesCBValidator(), 'Invalid images option \'%s\'!'),
        'parchi': Setting(Options.PARCHISETTING, ParchiCBValidator(), 'Invalid parchi option \'%s\'!'),
        'threads': Setting(Options.THREADSETTING, ThreadsCBValidator(), 'Invalid threads option \'%s\'!'),
        'datemin': Setting(Options.DATEMIN, DateValidator(), 'Invalid date value \'%s\'!'),
        'datemax': Setting(Options.DATEMAX, DateValidator(), 'Invalid date value \'%s\'!'),
        'apikey': Setting(Options.APIKEY_KEY, APIKeyKeyValidator(), 'Invalid API key value \'%s\'!'),
        'apiuserid': Setting(Options.APIKEY_USERID, APIKeyUserIdValidator(), 'Invalid API user id value \'%s\'!'),
        'headers': Setting(Options.HEADER_ADD_STR, JsonValidator(), 'Invalid headers json \'%s\'!'),
        'cookies': Setting(Options.COOKIE_ADD_STR, JsonValidator(), 'Invalid cookies json \'%s\'!'),
        'proxytype': Setting(Options.PROXYTYPE, ProxyTypeValidator(), 'Invalid proxytype value \'%s\'!'),
        'proxy': Setting(Options.PROXYSTRING, ProxyValidator(), 'Invalid proxy value \'%s\'!'),
        'ignoreproxy': Setting(Options.IGNORE_PROXY, BoolStrValidator(), 'Invalid ignoreproxy bool value \'%s\'!'),
        'ignoreproxydwn': Setting(Options.PROXY_NO_DOWNLOAD, BoolStrValidator(), 'Invalid ignoreproxydwn bool value \'%s\'!'),
        'cacheprocessedhtml': Setting(Options.CACHE_PROCCED_HTML, BoolStrValidator(), 'Invalid cacheprocessedhtml bool value \'%s\'!'),
        'timeout': Setting(Options.TIMEOUTSTRING, TimeoutValidator(), 'Invalid timeout value \'%s\'!'),
        'retries': Setting(Options.RETRIESSTRING, RetriesValidator(), 'Invalid retries value \'%s\'!'),
        'prefix': Setting(Options.FNAMEPREFIX, BoolStrValidator(), 'Invalid prefix bool value \'%s\'!'),
        'savetags': Setting(Options.SAVE_TAGS, BoolStrValidator(), 'Invalid savetags bool value \'%s\'!'),
        'savesources': Setting(Options.SAVE_SOURCES, BoolStrValidator(), 'Invalid savesources bool value \'%s\'!'),
        'savecomments': Setting(Options.SAVE_COMMENTS, BoolStrValidator(), 'Invalid savecomments bool value \'%s\'!'),
        'infosavemode': Setting(Options.INFO_SAVE_MODE, InfoSaveModeValidator(), 'Invalid infosavemode value \'%s\'!'),
        'extendfilename': Setting(Options.APPEND_SOURCE_AND_TAGS, BoolStrValidator(), 'Invalid extendfilename bool value \'%s\'!'),
        'warndestnonempty': Setting(Options.WARN_NONEMPTY_DEST, BoolStrValidator(), 'Invalid warndestnonempty bool value \'%s\'!'),
        'verbose': Setting(Options.VERBOSE, BoolStrValidator(), 'Invalid verbose bool value \'%s\'!'),
        'revealmodulenames': Setting(Options.REVEALNAMES, BoolStrValidator(), 'Invalid revealmodulenames bool value \'%s\'!'),
        'autocompletion': Setting(Options.AUTOCOMPLETION_ENABLE, BoolStrValidator(), 'Invalid autocompletion bool value \'%s\'!'),
        'taglistspath': Setting(Options.TAGLISTS_PATH, FolderPathValidator(), 'Invalid taglistspath path value \'%s\'!'),
        'windowposition': Setting(Options.WINDOW_POSITION, WindowPosValidator(), 'Invalid windowposition value \'%s\'!'),
    }

    combobox_setting_arrays = {
        Options.VIDSETTING: OPTION_VALUES_VIDEOS,
        Options.IMGSETTING: OPTION_VALUES_IMAGES,
        Options.PARCHISETTING: OPTION_VALUES_PARCHI,
        Options.THREADSETTING: OPTION_VALUES_THREADING,
    }

    duplicating_settings = {
        Options.PROXYSTRING: Options.PROXYSTRING_TEMP,
        Options.PROXYTYPE: Options.PROXYTYPE_TEMP,
        Options.TIMEOUTSTRING: Options.TIMEOUTSTRING_TEMP,
        Options.RETRIESSTRING: Options.RETRIESSTRING_TEMP,
        Options.APIKEY_KEY: Options.APIKEY_KEY_TEMP,
        Options.APIKEY_USERID: Options.APIKEY_USERID_TEMP,
    }

    @staticmethod
    def initialize(*, tk: Tk, on_proc_module_change_callback: Callable[[int], None],
                   on_init_autocompletion_callback: Callable[[str], None]):
        Settings.on_proc_module_change_callback = on_proc_module_change_callback
        Settings.on_init_autocompletion_callback = on_init_autocompletion_callback
        for s in Settings.settings.values():
            s.check.tk = tk

    @staticmethod
    def try_pick_autoconfig() -> None:
        base_path = normalize_path(os.path.abspath(os.curdir))
        try:
            for filename in Settings.AUTOCONFIG_FILENAMES:
                full_path = f'{base_path}{filename}'
                if not os.path.isfile(full_path):
                    continue
                file_size = os.stat(full_path).st_size
                if file_size > 16 * Mem.KB:
                    trace(f'Skipping \'{filename}\', file is too large ({file_size / Mem.KB:.2f})')
                    continue
                trace(f'Trying to autoconfigure using {filename}...')
                try:
                    with open(full_path, 'rt', encoding=UTF8) as rfile:
                        Settings._read_settings(rfile)
                    trace('Ok')
                    break
                except Exception:
                    trace(f'Cannot load settings from {filename}.')
                    continue
        except Exception:
            trace('Error loading settings.')

    @staticmethod
    def save_initial_settings() -> None:
        Settings.INITIAL_SETTINGS = Settings._write_settings()

    @staticmethod
    def reset_all_settings() -> None:
        Settings._read_settings(Settings.INITIAL_SETTINGS, False)

    @staticmethod
    def _write_settings() -> list[str]:
        def to_cfg_line(name: str, value: str | int) -> str:
            return f'{name}={value!s}\n'

        settings_strlist = ['# Ruxx config settings #\n\n']
        for k in Settings.settings:
            myval: str | int
            conf = Settings.settings[k].conf
            if conf == Options.HEADER_ADD_STR:
                myval = window_hcookiesm().get_json_h()
            elif conf == Options.COOKIE_ADD_STR:
                myval = window_hcookiesm().get_json_c()
            elif conf == Options.MODULE:
                myval = ProcModule.value() - 1
            elif conf in Settings.combobox_setting_arrays:
                myval = Settings.combobox_setting_arrays[conf].index(getrootconf(conf))
            elif conf == Options.WINDOW_POSITION:
                myval = f'{rootm().winfo_x():.0f}x{rootm().winfo_y():.0f}'
            else:
                myval = getrootconf(conf)
            if conf == Options.DATEMIN and as_date(myval) <= as_date(DATE_MIN_DEFAULT):
                continue
            elif conf == Options.DATEMAX and as_date(myval) >= LAUCH_DATE:
                continue
            else:
                settings_strlist.append(to_cfg_line(k, myval))
        return settings_strlist

    @staticmethod
    def _read_settings(rfile: TextIO | list[str], set_window_pos=True) -> None:
        for line in rfile:
            line = line.strip(' \n\ufeff')  # remove BOM too
            if line.startswith('#') or line == '':  # comment or a newline
                continue
            kv_k: str
            kv_v: str
            kv_k, kv_v = line.split('=', 1)
            if kv_k in Settings.settings:
                conf = Settings.settings[kv_k].conf
                val = Settings.settings[kv_k].type(kv_v)
                assert Settings.settings[kv_k].validate(val)
                if conf == Options.HEADER_ADD_STR:
                    window_hcookiesm().set_to_h(val)
                elif conf == Options.COOKIE_ADD_STR:
                    window_hcookiesm().set_to_c(val)
                elif conf == Options.MODULE:
                    Settings.on_proc_module_change_callback(val + 1)
                    setrootconf(conf, ProcModule.name())
                    int_vars[CVARS[conf]].set(val + 1)
                elif conf == Options.WINDOW_POSITION:
                    if set_window_pos:
                        rootm().set_position(*(float(dim) for dim in str(val).split('x', 1)))
                elif conf == Options.TAGLISTS_PATH:
                    Settings.on_init_autocompletion_callback(val)
                elif conf in Settings.duplicating_settings:
                    [setrootconf(cnf, val) for cnf in (conf, Settings.duplicating_settings.get(conf))]
                elif conf in Settings.combobox_setting_arrays:
                    setrootconf(conf, Settings.combobox_setting_arrays.get(conf)[val])
                else:
                    setrootconf(conf, val)
            else:
                trace(f'unknown option \'{kv_k}\', skipped')

    @staticmethod
    def save_settings() -> None:
        try:
            filepath = filedialog.asksaveasfilename(initialdir=get_curdir(), filetypes=(('Config files', '*.cfg'), ('All files', '*.*')))
            if filepath and len(filepath) > 0:
                setrootconf(Options.LASTPATH, filepath[:normalize_path(filepath, False).rfind(SLASH) + 1])
                if str(filepath).endswith('.cfg') is False:
                    filepath += '.cfg'
                trace(f'Saving setting to {filepath}...')
                with open(filepath, 'wt', encoding=UTF8) as wfile:
                    wfile.writelines(Settings._write_settings())
                trace('Ok')
        except Exception:
            trace('Error saving settings.')

    @staticmethod
    def load_settings() -> None:
        try:
            filepath = ask_filename((('Config files', '*.cfg'), ('All files', '*.*')))
            if filepath is not None and len(filepath) > 0:
                trace(f'Loading setting from {filepath}...')
                with open(filepath, 'rt', encoding=UTF8) as rfile:
                    Settings._read_settings(rfile)
                trace('Ok')
        except Exception:
            trace('Error loading settings.')

#
#
#########################################
