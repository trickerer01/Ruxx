# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import itertools
import json
import os
import pathlib
from collections.abc import Callable
from tkinter import Tk, filedialog
from typing import Protocol, TextIO

from .defines import DATE_MIN_DEFAULT, LAUCH_DATE, UTF8, Mem
from .gui_base import ask_filename, get_curdir, getrootconf, int_vars, rootm, setrootconf, window_hcookiesm
from .gui_defines import (
    CVARS,
    OPTION_VALUES_IMAGES,
    OPTION_VALUES_PARCHI,
    OPTION_VALUES_THREADING,
    OPTION_VALUES_VIDEOS,
    Options,
)
from .logger import trace
from .module import ProcModule
from .utils import as_date
from .validators import (
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

__all__ = ('ConfigMgr', 'register_config_worker')

SETTINGS_FILE_SIZE_LIMIT = 16 * Mem.KB

CONFIG_FILE_TYPES = (
    ('Config files', '*.cfg'),
    ('JSON files', '*.json'),
    ('All files', '*.*'),
)


class ConfigWorker(Protocol):
    @staticmethod
    def read(source: TextIO | list[str], set_window_pos=True) -> None: ...
    def write(self, destination: TextIO | list[str]) -> None: ...
    @staticmethod
    def save(source: list[str] | dict[str, int | str | dict[str, str]], destination: TextIO | list[str]) -> None: ...


class ListConfigWorker:
    @staticmethod
    def read(source: TextIO | list[str], set_window_pos=True) -> None:
        for line in source:
            line = line.strip(' \n\ufeff')  # remove BOM too
            if line.startswith('#') or not line:  # comment or a newline
                continue
            kv_k, kv_v = tuple(line.split('=', 1))
            if kv_k in ConfigMgr.settings:
                conf = ConfigMgr.settings[kv_k].conf
                val: int | str = ConfigMgr.settings[kv_k].type(kv_v)
                assert ConfigMgr.settings[kv_k].validate(val)
                if conf == Options.HEADER_ADD_STR:
                    window_hcookiesm().set_headers_s(val)
                elif conf == Options.COOKIE_ADD_STR:
                    window_hcookiesm().set_cookies_s(val)
                elif conf == Options.MODULE:
                    ConfigMgr.on_proc_module_change_callback(val + 1)
                    setrootconf(conf, ProcModule.name())
                    int_vars[CVARS[conf]].set(val + 1)
                elif conf == Options.WINDOW_POSITION:
                    if set_window_pos:
                        rootm().set_position(*(float(dim) for dim in str(val).split('x', 1)))
                elif conf == Options.TAGLISTS_PATH:
                    ConfigMgr.on_init_autocompletion_callback(val)
                elif conf in ConfigMgr.duplicating_settings:
                    [setrootconf(cnf, val) for cnf in (conf, ConfigMgr.duplicating_settings.get(conf))]
                elif conf in ConfigMgr.combobox_setting_arrays:
                    setrootconf(conf, ConfigMgr.combobox_setting_arrays.get(conf)[val])
                else:
                    setrootconf(conf, val)
            else:
                trace(f'unknown option \'{kv_k}\', skipped')

    def write(self, destination: TextIO | list[str]) -> None:
        def to_cfg_line(name: str, value: str | int) -> str:
            return f'{name}={value!s}\n'

        settings_strlist = ['# Ruxx config settings #\n\n']
        for k in ConfigMgr.settings:
            myval: str | int
            conf = ConfigMgr.settings[k].conf
            if conf == Options.HEADER_ADD_STR:
                myval = window_hcookiesm().get_json_h_s()
            elif conf == Options.COOKIE_ADD_STR:
                myval = window_hcookiesm().get_json_c_s()
            elif conf == Options.MODULE:
                myval = ProcModule.value() - 1
            elif conf in ConfigMgr.combobox_setting_arrays:
                myval = ConfigMgr.combobox_setting_arrays[conf].index(getrootconf(conf))
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
        self.save(settings_strlist, destination)

    @staticmethod
    def save(source: list[str], destination: list[str]) -> None:
        destination.extend(source)


class TextConfigWorker(ListConfigWorker):
    @staticmethod
    def save(source: list[str], destination: TextIO) -> None:
        destination.writelines(source)


class JSONConfigWorker:
    @staticmethod
    def read(source: TextIO, set_window_pos=True) -> None:
        json_: dict[str, int | str | dict[str, str]] = json.load(source)
        for k, v in json_.items():
            if k.startswith('@'):
                continue
            if k in ConfigMgr.settings:
                setting = ConfigMgr.settings[k]
                conf = setting.conf
                if not isinstance(v, dict):
                    val = setting.type(v)
                    assert setting.validate(val)
                else:
                    val = v
                if conf == Options.HEADER_ADD_STR:
                    window_hcookiesm().set_headers(val)
                elif conf == Options.COOKIE_ADD_STR:
                    window_hcookiesm().set_cookies(val)
                elif conf == Options.MODULE:
                    ConfigMgr.on_proc_module_change_callback(val + 1)
                    setrootconf(conf, ProcModule.name())
                    int_vars[CVARS[conf]].set(val + 1)
                elif conf == Options.WINDOW_POSITION:
                    if set_window_pos:
                        rootm().set_position(*(float(dim) for dim in str(val).split('x', 1)))
                elif conf == Options.TAGLISTS_PATH:
                    ConfigMgr.on_init_autocompletion_callback(val)
                elif conf in ConfigMgr.duplicating_settings:
                    [setrootconf(cnf, val) for cnf in (conf, ConfigMgr.duplicating_settings.get(conf))]
                elif conf in ConfigMgr.combobox_setting_arrays:
                    setrootconf(conf, ConfigMgr.combobox_setting_arrays.get(conf)[val])
                else:
                    setrootconf(conf, val)
            else:
                trace(f'unknown option \'{k}\', skipped')

    def write(self, destination: TextIO) -> None:
        json_: dict[str, int | str | dict[str, str]] = {'@comment': '# Ruxx config settings #'}
        for k in ConfigMgr.settings:
            myval: str | int | dict[str, str]
            conf = ConfigMgr.settings[k].conf
            if conf == Options.HEADER_ADD_STR:
                myval = window_hcookiesm().get_json_h()
            elif conf == Options.COOKIE_ADD_STR:
                myval = window_hcookiesm().get_json_c()
            elif conf == Options.MODULE:
                myval = ProcModule.value() - 1
            elif conf in ConfigMgr.combobox_setting_arrays:
                myval = ConfigMgr.combobox_setting_arrays[conf].index(getrootconf(conf))
            elif conf == Options.WINDOW_POSITION:
                myval = f'{rootm().winfo_x():.0f}x{rootm().winfo_y():.0f}'
            else:
                myval = getrootconf(conf)
            if conf == Options.DATEMIN and as_date(myval) <= as_date(DATE_MIN_DEFAULT):
                continue
            elif conf == Options.DATEMAX and as_date(myval) >= LAUCH_DATE:
                continue
            elif conf not in (Options.HEADER_ADD_STR, Options.COOKIE_ADD_STR):
                myval = str(myval)
            json_[k] = myval
        self.save(json_, destination)

    @staticmethod
    def save(source: dict[str, int | str | dict[str, str]], destination: TextIO) -> None:
        json.dump(source, destination, indent=4)
        destination.write('\n')


CONFIG_WORKERS: dict[str, ConfigWorker] = {
    '.default': ListConfigWorker(),
}


def register_config_worker(ext: str, worker: ConfigWorker) -> None:
    assert ext.startswith('.'), 'Config worker extension must start with \'.\''
    assert ext not in CONFIG_WORKERS, f'Config worker for ext {ext} already exists (\'{CONFIG_WORKERS[ext].__class__.__name__}\')!'
    CONFIG_WORKERS[ext] = worker


def get_config_worker(file_name='') -> ConfigWorker:
    file_name = file_name or 'none.default'
    ext = os.path.splitext(file_name)[1]
    assert ext in CONFIG_WORKERS, f'No config worker exists for file {file_name}!'
    return CONFIG_WORKERS[ext]


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


class ConfigMgr:
    """ConfigMgr !Static!"""
    INITIAL_SETTINGS: list[str] = []
    AUTOCONFIG_FILENAMES: tuple[str, str, str, str, str, str, str, str] = tuple(
        ''.join(tup) for tup in itertools.product(('ruxx', 'auto', 'settings', 'config'), ('.cfg', '.json'))
    )
    on_proc_module_change_callback: Callable[[int], None] | None = None
    on_init_autocompletion_callback: Callable[[str], None] | None = None

    def __init__(self) -> None:
        raise RuntimeError(f'{self.__class__.__name__} class should never be instanced!')

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
        register_config_worker('.cfg', TextConfigWorker())
        register_config_worker('.txt', TextConfigWorker())
        register_config_worker('.json', JSONConfigWorker())
        ConfigMgr.on_proc_module_change_callback = on_proc_module_change_callback
        ConfigMgr.on_init_autocompletion_callback = on_init_autocompletion_callback
        for _, s in ConfigMgr.settings.items():
            s.check.tk = tk
        ConfigMgr.try_pick_autoconfig()
        ConfigMgr.save_initial_settings()

    @staticmethod
    def try_pick_autoconfig() -> None:
        base_path = pathlib.Path(os.curdir).resolve()
        try:
            for filename in ConfigMgr.AUTOCONFIG_FILENAMES:
                full_path = base_path / filename
                if not full_path.is_file():
                    continue
                file_size = full_path.stat().st_size
                if file_size > SETTINGS_FILE_SIZE_LIMIT:
                    trace(f'Skipping \'{filename}\', file is too large ({file_size / Mem.KB:.2f})')
                    continue
                trace(f'Trying to autoconfigure using {filename}...')
                try:
                    with open(full_path, 'rt', encoding=UTF8) as rfile:
                        get_config_worker(rfile.name).read(rfile)
                    trace('Ok')
                    break
                except Exception:
                    trace(f'Cannot load settings from {filename}.')
                    continue
        except Exception:
            trace('Error loading settings.')

    @staticmethod
    def save_initial_settings() -> None:
        get_config_worker('').write(ConfigMgr.INITIAL_SETTINGS)

    @staticmethod
    def reset_all_settings() -> None:
        get_config_worker('').read(ConfigMgr.INITIAL_SETTINGS, False)

    @staticmethod
    def save_settings() -> None:
        try:
            if fpath := filedialog.asksaveasfilename(initialdir=get_curdir(), filetypes=CONFIG_FILE_TYPES, confirmoverwrite=True,
                                                     defaultextension='.json', initialfile='config'):
                setrootconf(Options.LASTPATH, pathlib.Path(fpath).parent.as_posix())
                trace(f'Saving setting to {fpath}...')
                with open(fpath, 'wt', encoding=UTF8, newline='\n') as wfile:
                    get_config_worker(wfile.name).write(wfile)
                trace('Ok')
        except Exception:
            trace('Error saving settings.')

    @staticmethod
    def load_settings() -> None:
        try:
            if fpath := ask_filename(CONFIG_FILE_TYPES):
                trace(f'Loading setting from {fpath}...')
                with open(fpath, 'rt', encoding=UTF8) as rfile:
                    get_config_worker(rfile.name).read(rfile)
                trace('Ok')
        except Exception:
            trace('Error loading settings.')

#
#
#########################################
