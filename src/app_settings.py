# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import ABC, abstractmethod
from os import path, curdir, stat
from tkinter import filedialog, Tk
from typing import Union, List, Iterable, Callable, Optional

# internal
from app_defines import Mem, DEFAULT_ENCODING
from app_gui_base import window_hcookiesm, getrootconf, setrootconf, int_vars, get_curdir, ask_filename, rootm
from app_gui_defines import (
    Options, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES, OPTION_VALUES_PARCHI, OPTION_VALUES_THREADING, CVARS, SLASH,
)
from app_module import ProcModule
from app_logger import Logger
from app_utils import normalize_path
from app_validators import (
    Validator, ValidatorAlwaysTrue, ModuleValidator, VideosCBValidator, ImagesCBValidator, ParchiCBValidator, ThreadsCBValidator,
    DateValidator, JsonValidator, ProxyTypeValidator, ProxyValidator, BoolStrValidator, TimeoutValidator, WindowPosValidator,
)

__all__ = ('Settings',)


class Settings(ABC):
    """
    Settings !Static!
    """
    INITIAL_SETTINGS = []  # type: List[str]
    AUTOCONFIG_FILENAMES = ('ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg')
    on_proc_module_change_callback = None  # type: Optional[Callable[[int], None]]

    @abstractmethod
    def ___this_class_is_static___(self) -> ...:
        ...

    class Setting:
        def __init__(self, sconf: Options, check: Validator, check_fail_message: str = None) -> None:
            self.conf = sconf
            self.type = check.get_value_type()
            self.check = check
            self.check_fail_message = check_fail_message or f'Invalid value \'%s\' for config id \'{self.conf.value:d}\''
            assert self.check_fail_message.count('%s') == 1

        def validate(self, val: Union[int, str]) -> bool:
            result = self.check(val)
            if result is False:
                Logger.log(self.check_fail_message % str(val), False, False)
            return result

    settings = {
        'tags': Setting(Options.OPT_TAGS, ValidatorAlwaysTrue()),  # no validation, str
        'module': Setting(Options.OPT_MODULE, ModuleValidator(), 'Invalid module \'%s\'!'),
        'path': Setting(Options.OPT_PATH, ValidatorAlwaysTrue()),  # no validation, str
        'videos': Setting(Options.OPT_VIDSETTING, VideosCBValidator(), 'Invalid videos option \'%s\'!'),
        'images': Setting(Options.OPT_IMGSETTING, ImagesCBValidator(), 'Invalid images option \'%s\'!'),
        'parchi': Setting(Options.OPT_PARCHISETTING, ParchiCBValidator(), 'Invalid parchi option \'%s\'!'),
        'threads': Setting(Options.OPT_THREADSETTING, ThreadsCBValidator(), 'Invalid threads option \'%s\'!'),
        'datemin': Setting(Options.OPT_DATEMIN, DateValidator(), 'Invalid date value \'%s\'!'),
        'datemax': Setting(Options.OPT_DATEMAX, DateValidator(), 'Invalid date value \'%s\'!'),
        'headers': Setting(Options.OPT_HEADER_ADD_STR, JsonValidator(), 'Invalid headers json \'%s\'!'),
        'cookies': Setting(Options.OPT_COOKIE_ADD_STR, JsonValidator(), 'Invalid cookies json \'%s\'!'),
        'proxytype': Setting(Options.OPT_PROXYTYPE, ProxyTypeValidator(), 'Invalid proxy type value \'%s\'!'),
        'proxy': Setting(Options.OPT_PROXYSTRING, ProxyValidator(), 'Invalid proxy value \'%s\'!'),
        'ignoreproxy': Setting(Options.OPT_IGNORE_PROXY, BoolStrValidator(), 'Invalid ignoreproxy bool value \'%s\'!'),
        'ignoreproxydwn': Setting(Options.OPT_PROXY_NO_DOWNLOAD, BoolStrValidator(), 'Invalid ignoreproxydwn bool value \'%s\'!'),
        'timeout': Setting(Options.OPT_TIMEOUTSTRING, TimeoutValidator(), 'Invalid timeout value \'%s\'!'),
        'prefix': Setting(Options.OPT_FNAMEPREFIX, BoolStrValidator(), 'Invalid prefix bool value \'%s\'!'),
        'savetags': Setting(Options.OPT_SAVE_TAGS, BoolStrValidator(), 'Invalid savetags bool value \'%s\'!'),
        'savesources': Setting(Options.OPT_SAVE_SOURCES, BoolStrValidator(), 'Invalid savesources bool value \'%s\'!'),
        'savecomments': Setting(Options.OPT_SAVE_COMMENTS, BoolStrValidator(), 'Invalid savecomments bool value \'%s\'!'),
        'extendfilename': Setting(Options.OPT_APPEND_SOURCE_AND_TAGS, BoolStrValidator(), 'Invalid extendfilename bool value \'%s\'!'),
        'warndestnonempty': Setting(Options.OPT_WARN_NONEMPTY_DEST, BoolStrValidator(), 'Invalid warndestnonempty bool value \'%s\'!'),
        'windowposition': Setting(Options.OPT_WINDOW_POSITION, WindowPosValidator(), 'Invalid windowposition value \'%s\'!'),
    }

    combobox_setting_arrays = {
        Options.OPT_VIDSETTING: OPTION_VALUES_VIDEOS,
        Options.OPT_IMGSETTING: OPTION_VALUES_IMAGES,
        Options.OPT_PARCHISETTING: OPTION_VALUES_PARCHI,
        Options.OPT_THREADSETTING: OPTION_VALUES_THREADING,
    }

    @staticmethod
    def initialize(*, tk: Tk, on_proc_module_change_callback: Callable[[int], None]):
        Settings.on_proc_module_change_callback = on_proc_module_change_callback
        for s in Settings.settings.values():
            s.check.tk = tk

    @staticmethod
    def try_pick_autoconfig() -> None:
        base_path = normalize_path(path.abspath(curdir))
        try:
            for filename in Settings.AUTOCONFIG_FILENAMES:
                full_path = f'{base_path}{filename}'
                if not path.isfile(full_path):
                    continue
                file_size = stat(full_path).st_size
                if file_size > 16 * Mem.KB:
                    Logger.log(f'Skipping \'{filename}\', file is too large ({file_size / Mem.KB:.2f})', False, False)
                    continue
                Logger.log(f'Trying to autoconfigure using {filename}...', False, False)
                try:
                    with open(full_path, 'rt', encoding=DEFAULT_ENCODING) as rfile:
                        Settings._read_settings(rfile.readlines())
                    Logger.log('Ok', False, False)
                    break
                except Exception:
                    Logger.log(f'Cannot load settings from {filename}.', False, False)
                    continue
        except Exception:
            Logger.log('Error loading settings.', False, False)

    @staticmethod
    def save_initial_settings() -> None:
        Settings.INITIAL_SETTINGS = Settings._write_settings()

    @staticmethod
    def reset_all_settings() -> None:
        Settings._read_settings(Settings.INITIAL_SETTINGS, False)

    @staticmethod
    def _write_settings() -> List[str]:
        def to_cfg_line(name: str, value: Union[str, int]) -> str:
            return f'{name}={str(value)}\n'

        settings_strlist = ['# Ruxx config settings #\n\n']
        for k in Settings.settings:
            # noinspection PyUnusedLocal
            myval = ...  # type: Union[str, int]
            conf = Settings.settings.get(k).conf
            if conf == Options.OPT_HEADER_ADD_STR:
                myval = window_hcookiesm().get_json_h()
            elif conf == Options.OPT_COOKIE_ADD_STR:
                myval = window_hcookiesm().get_json_c()
            elif conf == Options.OPT_MODULE:
                myval = ProcModule.get() - 1
            elif conf in Settings.combobox_setting_arrays:
                myval = Settings.combobox_setting_arrays.get(conf).index(getrootconf(conf))
            elif conf == Options.OPT_WINDOW_POSITION:
                myval = f'{rootm().winfo_x():.0f}x{rootm().winfo_y():.0f}'
            else:
                myval = getrootconf(conf)
            settings_strlist.append(to_cfg_line(k, myval))
        return settings_strlist

    @staticmethod
    def _read_settings(lines: Iterable[str], set_window_pos=True) -> None:
        for line in lines:
            line = line.strip(' \n\ufeff')  # remove BOM too
            if line.startswith('#') or line == '':  # comment or a newline
                continue
            kv_k, kv_v = line.split('=', 1)  # type: str, str
            if kv_k in Settings.settings:
                conf = Settings.settings.get(kv_k).conf
                val = Settings.settings.get(kv_k).type(kv_v)
                assert Settings.settings.get(kv_k).validate(val)
                if conf == Options.OPT_HEADER_ADD_STR:
                    window_hcookiesm().set_to_h(val)
                elif conf == Options.OPT_COOKIE_ADD_STR:
                    window_hcookiesm().set_to_c(val)
                elif conf == Options.OPT_MODULE:
                    Settings.on_proc_module_change_callback(val + 1)
                    setrootconf(conf, ProcModule.get_cur_module_name())
                    int_vars.get(CVARS.get(conf)).set(val + 1)
                elif conf == Options.OPT_PROXYSTRING:
                    setrootconf(Options.OPT_PROXYSTRING, val)
                    setrootconf(Options.OPT_PROXYSTRING_TEMP, val)
                elif conf == Options.OPT_PROXYTYPE:
                    setrootconf(Options.OPT_PROXYTYPE, val)
                    setrootconf(Options.OPT_PROXYTYPE_TEMP, val)
                elif conf == Options.OPT_TIMEOUTSTRING:
                    setrootconf(Options.OPT_TIMEOUTSTRING, val)
                    setrootconf(Options.OPT_TIMEOUTSTRING_TEMP, val)
                elif conf in Settings.combobox_setting_arrays:
                    setrootconf(conf, Settings.combobox_setting_arrays.get(conf)[val])
                elif conf == Options.OPT_WINDOW_POSITION:
                    if set_window_pos:
                        rootm().set_position(*(float(dim) for dim in val.split('x', 1)))
                else:
                    setrootconf(conf, val)
            else:
                Logger.log(f'unknown option \'{kv_k}\', skipped', False, False)

    @staticmethod
    def save_settings() -> None:
        try:
            filepath = filedialog.asksaveasfilename(initialdir=get_curdir(), filetypes=(('Config files', '*.cfg'), ('All files', '*.*')))
            if filepath and len(filepath) > 0:
                setrootconf(Options.OPT_LASTPATH, filepath[:normalize_path(filepath, False).rfind(SLASH) + 1])
                if str(filepath).endswith('.cfg') is False:
                    filepath += '.cfg'
                Logger.log(f'Saving setting to {filepath}...', False, False)
                with open(filepath, 'wt', encoding=DEFAULT_ENCODING) as wfile:
                    wfile.writelines(Settings._write_settings())
                Logger.log('Ok', False, False)
        except Exception:
            Logger.log('Error saving settings.', False, False)

    @staticmethod
    def load_settings() -> None:
        try:
            filepath = ask_filename((('Config files', '*.cfg'), ('All files', '*.*')))
            if filepath is not None and len(filepath) > 0:
                Logger.log(f'Loading setting from {filepath}...', False, False)
                with open(filepath, 'rt', encoding=DEFAULT_ENCODING) as rfile:
                    Settings._read_settings(rfile.readlines())
                Logger.log('Ok', False, False)
        except Exception:
            Logger.log('Error loading settings.', False, False)

#
#
#########################################
