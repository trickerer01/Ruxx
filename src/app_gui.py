# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import ctypes
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from json import loads as json_loads
from multiprocessing.dummy import current_process
from os import path, curdir, system, makedirs, stat
from threading import Thread
from time import sleep as thread_sleep
from tkinter import messagebox, filedialog, BooleanVar, IntVar, Entry, Button, PhotoImage, END, LEFT
from typing import Optional, Union, Callable, List, Tuple, Iterable

# internal
from app_cmdargs import prepare_arglist
from app_defines import (
    DownloaderStates, DownloadModes, STATE_WORK_START, SUPPORTED_PLATFORMS, MODULE_ABBR_RX, MODULE_ABBR_RN,
    DEFAULT_ENCODING, KNOWN_EXTENSIONS_STR, PLATFORM_WINDOWS, STATUSBAR_INFO_MAP, PROGRESS_VALUE_NO_DOWNLOAD, PROGRESS_VALUE_DOWNLOAD,
    DEFAULT_HEADERS, DATE_MIN_DEFAULT, FMT_DATE,
    max_progress_value_for_state,
)
from app_download_rn import DownloaderRn
from app_download_rx import DownloaderRx
from app_file_parser import prepare_tags_list
from app_file_sorter import sort_files_by_type, FileTypeFilter, sort_files_by_size, sort_files_by_score
from app_file_tagger import untag_files, retag_files
from app_gui_base import (
    AskFileTypeFilterWindow, AskFileSizeFilterWindow, AskFileScoreFilterWindow, AskIntWindow, LogWindow,
    setrootconf, int_vars, rootm, getrootconf, window_hcookiesm, c_menum, window_proxym, c_submenum, register_menu,
    register_submenu, GetRoot, create_base_window_widgets, text_cmdm, get_icon, init_additional_windows,
)
from app_gui_defines import (
    STATE_DISABLED, STATE_NORMAL, hotkeys,
    COLOR_WHITE, COLOR_BROWN1, COLOR_PALEGREEN, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES, OPTION_VALUES_THREADING,
    OPTION_CMD_VIDEOS, OPTION_CMD_IMAGES, OPTION_CMD_THREADING_CMD, OPTION_CMD_THREADING,
    OPTION_CMD_FNAMEPREFIX, OPTION_CMD_DOWNMODE_CMD, OPTION_CMD_DOWNMODE, OPTION_CMD_DOWNLIMIT_CMD, OPTION_CMD_SAVE_TAGS,
    OPTION_CMD_SAVE_SOURCES, OPTION_CMD_DATEAFTER, OPTION_CMD_DATEBEFORE, OPTION_CMD_PATH,
    OPTION_CMD_COOKIES, OPTION_CMD_HEADERS, OPTION_CMD_PROXY, OPTION_CMD_IGNORE_PROXY,
    OPTION_CMD_PROXY_NO_DOWNLOAD, GUI2_UPDATE_DELAY_DEFAULT, THREAD_CHECK_PERIOD_DEFAULT, SLASH,
    OPTION_CMD_APPEND_SOURCE_AND_TAGS, OPTION_CMD_WARN_NONEMPTY_DEST, OPTION_CMD_MODULE, BUTTONS_TO_UNFOCUS,
    OPTION_CMD_PARCHI, OPTION_VALUES_PARCHI, BUT_ALT_F4,
    ProcModule, menu_items, menu_item_orig_states, gobjects, gobject_orig_states, Options, Globals, Menus, Icons, CVARS,
    re_space_mult, re_or_meta_group,
)
from app_help import HELP_TAGS_MSG_RX, HELP_TAGS_MSG_RN, ABOUT_MSG
from app_logger import Logger
from app_revision import APP_NAME, __RUXX_DEBUG__
from app_tags_parser import reset_last_tags, parse_tags
from app_utils import normalize_path, confirm_yes_no
from app_validators import (
    Validator, ValidatorAlwaysTrue, ModuleValidator, VideosCBValidator, ImagesCBValidator, ThreadsCBValidator, JsonValidator,
    BoolStrValidator, ProxyValidator, ProxyTypeValidator, DateValidator, ParchiCBValidator,
)

__all__ = ()

# loaded
download_thread = None  # type: Optional[Thread]
tags_check_thread = None  # type: Optional[Thread]
prev_download_state = True
console_shown = True
IS_RAW = '_sitebuiltins' in sys.modules  # ran from console (shell or IDE)
IS_IDE = '_virtualenv' in sys.modules  # ran from IDE
CONSOLEVAL = ctypes.windll.kernel32.GetConsoleProcessList(ctypes.byref(ctypes.c_int(0)), 1) if sys.platform == PLATFORM_WINDOWS else -1
HAS_OWN_CONSOLE = CONSOLEVAL == 2  # 1 process is a main window, 2 is the console itself, 3 would be external console
CAN_MANIPULATE_CONSOLE = HAS_OWN_CONSOLE and not IS_RAW
# end loaded

# MODULES
dwn = None  # type: Union[None, DownloaderRn, DownloaderRx]
DOWNLOADERS_BY_PROC_MODULE = {
    ProcModule.PROC_RX: DownloaderRx,
    ProcModule.PROC_RN: DownloaderRn,
}
PROC_MODULES_BY_ABBR = {
    MODULE_ABBR_RX: ProcModule.PROC_RX,
    MODULE_ABBR_RN: ProcModule.PROC_RN,
}
# END MODULES


# static methods
def toggle_console() -> None:
    global console_shown
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), not console_shown)
    console_shown = not console_shown


def ensure_compatibility(is_gui: bool) -> None:
    assert sys.version_info >= (3, 7), 'Minimum python version required is 3.7!'
    if sys.platform not in SUPPORTED_PLATFORMS:
        if is_gui:
            messagebox.showinfo('', f'Unsupported OS \'{sys.platform}\'')
        else:
            Logger.log(f'Unsupported OS \'{sys.platform}\'', False, False)
        sys.exit(-1)


def hotkey_text(option: Options) -> str:
    return (
        hotkeys.get(option).upper().replace('CONTROL', 'Ctrl').replace('SHIFT', 'Shift').replace('-', '+').replace('<', '').replace('>', '')
    )


# def niy() -> None:
#     messagebox.showinfo('', 'NIY!')


def get_curdir(prioritize_last_path=True) -> str:
    lastloc = str(getrootconf(Options.OPT_LASTPATH))
    curloc = str(getrootconf(Options.OPT_PATH))
    if prioritize_last_path:
        return lastloc if len(lastloc) > 0 else curloc if path.isdir(curloc) else path.abspath(curdir)
    else:
        return curloc if path.isdir(curloc) else lastloc if len(lastloc) > 0 else path.abspath(curdir)


class Settings(ABC):
    """
    Settings !Static!
    """

    INITIAL_SETTINGS = []  # type: List[str]
    AUTOCONFIG_FILENAMES = ('ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg')

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
        'path': Setting(Options.OPT_PATH, ValidatorAlwaysTrue(), 'Invalid path \'%s\'!'),  # no validation, str
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
        'prefix': Setting(Options.OPT_FNAMEPREFIX, BoolStrValidator(), 'Invalid prefix bool value \'%s\'!'),
        'savetags': Setting(Options.OPT_SAVE_TAGS, BoolStrValidator(), 'Invalid savetags bool value \'%s\'!'),
        'savesources': Setting(Options.OPT_SAVE_SOURCES, BoolStrValidator(), 'Invalid savesources bool value \'%s\'!'),
        'extendfilename': Setting(Options.OPT_APPEND_SOURCE_AND_TAGS, BoolStrValidator(), 'Invalid extendfilename bool value \'%s\'!'),
        'warndestnonempty': Setting(Options.OPT_WARN_NONEMPTY_DEST, BoolStrValidator(), 'Invalid warndestnonempty bool value \'%s\'!'),
    }

    combobox_setting_arrays = {
        Options.OPT_VIDSETTING: OPTION_VALUES_VIDEOS,
        Options.OPT_IMGSETTING: OPTION_VALUES_IMAGES,
        Options.OPT_PARCHISETTING: OPTION_VALUES_PARCHI,
        Options.OPT_THREADSETTING: OPTION_VALUES_THREADING,
    }

    @staticmethod
    def try_pick_autoconfig() -> None:
        base_path = normalize_path(path.abspath(curdir))
        try:
            for filename in Settings.AUTOCONFIG_FILENAMES:
                full_path = f'{base_path}{filename}'
                if not path.isfile(full_path):
                    continue
                file_size = stat(full_path).st_size
                if file_size > (16 * 1024):  # 16 Kb
                    if __RUXX_DEBUG__:
                        Logger.log(f'Skipping \'{filename}\', file is too large ({file_size / 1024:.2f})', False, False)
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
        Settings._read_settings(Settings.INITIAL_SETTINGS)

    @staticmethod
    def _write_settings() -> List[str]:
        def to_cfg_line(name: str, value: Union[str, int]) -> str:
            return f'{name}={str(value)}\n'

        settings = ['# Ruxx config settings #\n\n']
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
            else:
                myval = getrootconf(conf)
            settings.append(to_cfg_line(k, myval))
        return settings

    @staticmethod
    def _read_settings(lines: Iterable[str]) -> None:
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
                    set_proc_module(val + 1)
                    setrootconf(conf, ProcModule.get_cur_module_name())
                    int_vars.get(CVARS.get(conf)).set(val + 1)
                elif conf == Options.OPT_PROXYSTRING:
                    setrootconf(Options.OPT_PROXYSTRING_TEMP, val)
                elif conf == Options.OPT_PROXYTYPE:
                    setrootconf(Options.OPT_PROXYTYPE_TEMP, val)
                elif conf in Settings.combobox_setting_arrays:
                    setrootconf(conf, Settings.combobox_setting_arrays.get(conf)[val])
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


def untag_files_do() -> None:
    filelist = filedialog.askopenfilenames(
        initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),)
    )  # type: Tuple[str]

    if len(filelist) == 0:
        return

    setrootconf(Options.OPT_LASTPATH, filelist[0][:normalize_path(filelist[0], False).rfind(SLASH) + 1])
    untagged_count = untag_files(filelist)
    if untagged_count == len(filelist):
        Logger.log(f'Successfully un-tagged {len(filelist):d} file(s).', False, False)
    elif untagged_count > 0:
        Logger.log(f'Warning: only {untagged_count:d} / {len(filelist):d} files were un-tagged.', False, False)
    else:
        Logger.log(f'An error occured while un-tagging {len(filelist):d} files.', False, False)


def retag_files_do() -> None:
    filelist = filedialog.askopenfilenames(
        initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),)
    )  # type: Tuple[str]

    if len(filelist) == 0:
        return

    setrootconf(Options.OPT_LASTPATH, filelist[0][:normalize_path(filelist[0], False).rfind(SLASH) + 1])
    module = get_new_proc_module()
    retagged_count = retag_files(filelist, module.get_re_tags_to_process(), module.get_re_tags_to_exclude())
    if retagged_count == len(filelist):
        Logger.log(f'Successfully re-tagged {len(filelist):d} file(s).', False, False)
    elif retagged_count > 0:
        Logger.log(f'Warning: only {retagged_count:d} / {len(filelist):d} files were re-tagged.', False, False)
    else:
        Logger.log(f'An error occured while re-tagging {len(filelist):d} files.', False, False)


def sort_files_by_type_do() -> None:
    filelist = filedialog.askopenfilenames(
        initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),)
    )  # type: Tuple[str]

    if len(filelist) == 0:
        return

    aw = AskFileTypeFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)

    filter_type = aw.value()
    if filter_type == FileTypeFilter.FILTER_INVALID:
        return

    setrootconf(Options.OPT_LASTPATH, filelist[0][:normalize_path(filelist[0], False).rfind(SLASH) + 1])
    result = sort_files_by_type(filelist, filter_type)
    if result == len(filelist):
        Logger.log(f'Successfully sorted {len(filelist):d} file(s).', False, False)
    elif result > 0:
        Logger.log(f'Warning: only {result:d} / {len(filelist):d} files were sorted.', False, False)
    else:
        Logger.log(f'An error occured while sorting {len(filelist):d} files.', False, False)


def sort_files_by_size_do() -> None:
    filelist = filedialog.askopenfilenames(
        initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),)
    )  # type: Tuple[str]

    if len(filelist) == 0:
        return

    aw = AskFileSizeFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)

    thresholds_mb = aw.value()
    if thresholds_mb is None:
        return

    setrootconf(Options.OPT_LASTPATH, filelist[0][:normalize_path(filelist[0], False).rfind(SLASH) + 1])
    result = sort_files_by_size(filelist, thresholds_mb)
    if result == len(filelist):
        Logger.log(f'Successfully sorted {len(filelist):d} file(s).', False, False)
    elif result > 0:
        Logger.log(f'Warning: only {result:d} / {len(filelist):d} files were sorted.', False, False)
    else:
        Logger.log(f'An error occured while sorting {len(filelist):d} files.', False, False)


def sort_files_by_score_do() -> None:
    filelist = filedialog.askopenfilenames(
        initialdir=get_curdir(), filetypes=(('All supported', KNOWN_EXTENSIONS_STR),)
    )  # type: Tuple[str]

    if len(filelist) == 0:
        return

    aw = AskFileScoreFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)

    thresholds = aw.value()
    if thresholds is None:
        return

    setrootconf(Options.OPT_LASTPATH, filelist[0][:normalize_path(filelist[0], False).rfind(SLASH) + 1])
    result = sort_files_by_score(filelist, thresholds)
    if result == len(filelist):
        Logger.log(f'Successfully sorted {len(filelist):d} file(s).', False, False)
    elif result > 0:
        Logger.log(f'Warning: only {result:d} / {len(filelist):d} files were sorted.', False, False)
    else:
        Logger.log(f'An error occured while sorting {len(filelist):d} files.', False, False)


def set_download_limit() -> None:
    aw = AskIntWindow(rootm(), lambda x: x >= 0)
    aw.finalize()
    rootm().wait_window(aw.window)

    limit = aw.value()
    if limit is None:
        if aw.variable.get() != '':
            Logger.log(f'Invalid limt value \'{aw.variable.get()}\'', False, False)
        return

    setrootconf(Options.OPT_DOWNLOAD_LIMIT, limit)
    menu_items.get(Menus.MENU_DEBUG)[0].entryconfig(3, label=f'Set download limit ({limit})...')
    Logger.log(f'Download limit set to {limit:d} item(s).', False, False)


def reset_download_limit() -> None:
    setrootconf(Options.OPT_DOWNLOAD_LIMIT, 0)
    menu_items.get(Menus.MENU_DEBUG)[0].entryconfig(3, label='Set download limit (0)...')
    Logger.log('Download limit was reset.', False, False)


def open_download_folder() -> None:
    cur_path = normalize_path(getrootconf(Options.OPT_PATH))

    if not path.isdir(cur_path[:(cur_path.find(SLASH) + 1)]):
        messagebox.showerror('Open download folder', f'Path \'{cur_path}\' is invalid.')
        return

    if not path.isdir(cur_path):
        if not confirm_yes_no('Open download folder', f'Path \'{cur_path}\' doesn\'t exist. Create it?'):
            return
        try:
            makedirs(cur_path)
        except Exception:
            Logger.log(f'Unable to create path \'{cur_path}\'.', False, False)
            return

    try:
        res = system(f'start "" "{path.abspath(cur_path)}"')
        if res != 0:
            Logger.log(f'Couldn\'t open \'{cur_path}\', error: {res:d}.', False, False)
    except Exception:
        Logger.log(f'Couldn\'t open \'{cur_path}\'.', False, False)


def get_new_proc_module() -> Union[DownloaderRn, DownloaderRx]:
    return DOWNLOADERS_BY_PROC_MODULE[ProcModule.CUR_PROC_MODULE]()


def set_proc_module(dwnmodule: int) -> None:
    global dwn

    ProcModule.set(dwnmodule)
    dwn = None

    # prefix option
    prefix_opt_text = f'Prefix file names with \'{ProcModule.get_cur_module_name()}_\''

    if GetRoot() is not None:
        menu_items.get(Menus.MENU_EDIT)[0].entryconfig(0, label=prefix_opt_text)
        # icon
        config_global(Globals.GOBJECT_MODULE_ICON, image=get_icon(Icons.ICON_RX) if ProcModule.is_rx() else get_icon(Icons.ICON_RN))
        # enable/disable features specific to the module
        update_widget_enabled_states()

    # reset tags parser
    reset_last_tags()


def get_global(index: Globals) -> Union[Entry, Button]:
    return gobjects[index]


def config_global(index: Globals, **kwargs) -> None:
    get_global(index).config(kwargs)


def update_widget_enabled_states() -> None:
    downloading = is_downloading()
    for i in [m for m in Menus.__members__.values() if m < Menus.MAX_MENUS]:  # type: Menus
        if menu_items.get(i)[0] is not None:
            for j in menu_items.get(i)[1]:
                if i == Menus.MENU_ACTIONS and j == 1 and is_cheking_tags():  # Check tags, disabled when active
                    newstate = STATE_DISABLED
                else:
                    newstate = STATE_DISABLED if downloading else menu_item_orig_states[i][j]
                menu_items.get(i)[0].entryconfig(j, state=newstate)
    for gi in [g for g in Globals.__members__.values() if g < Globals.MAX_GOBJECTS]:  # type: Globals
        if gi == Globals.GOBJECT_COMBOBOX_PARCHI:
            config_global(gi, state=(STATE_DISABLED if not ProcModule.is_rx() else gobject_orig_states[gi]))


def is_focusing(gidx: Globals) -> bool:
    try:
        return rootm().focus_get() == get_global(gidx)
    except Exception:
        return False


def update_progressbar() -> None:
    try:
        progress_value = None  # type: Optional[int]
        if is_downloading():
            assert dwnm().current_state < DownloaderStates.MAX_STATES

            if dwnm().current_state == DownloaderStates.STATE_DOWNLOADING:
                progress_value = PROGRESS_VALUE_NO_DOWNLOAD
                if dwnm().total_count_all > 0 and dwnm().processed_count > 0:
                    progress_value += int((PROGRESS_VALUE_DOWNLOAD / dwnm().total_count_all) * dwnm().processed_count)
            else:
                progress_value = 0
                state = STATE_WORK_START
                num_states_no_download = DownloaderStates.STATE_DOWNLOADING - STATE_WORK_START
                while state <= num_states_no_download and state < dwnm().current_state:
                    base_value = max_progress_value_for_state(state)
                    progress_value += base_value
                    state = DownloaderStates(state + 1)

        setrootconf(Options.OPT_PROGRESS, progress_value or 0)
    except Exception:
        pass

    rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 6, update_progressbar)


def update_statusbar() -> None:
    try:
        state_text1 = STATUSBAR_INFO_MAP[dwnm().current_state][0]
        state_text2 = STATUSBAR_INFO_MAP[dwnm().current_state][1]
        state_text3 = STATUSBAR_INFO_MAP[dwnm().current_state][2]
        state_text4 = STATUSBAR_INFO_MAP[dwnm().current_state][3]
        status_str = state_text1
        if state_text2:
            status_str += str(dwnm().__getattribute__(state_text2))
        if state_text3 and state_text4 and dwnm().__getattribute__(state_text4) > 0:
            status_str += f'{state_text3}{str(dwnm().__getattribute__(state_text4))}'

        setrootconf(Options.OPT_STATUS, status_str)
    except Exception:
        pass

    rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 6, update_statusbar)


def prepare_cmdline() -> List[str]:

    def normalize_tag(ntag: str) -> str:
        return ntag.replace('+', '%2b').replace(' ', '+')

    # fill the str
    # base
    newstr = ['Cmd:']
    # + tags
    tags_line = str(getrootconf(Options.OPT_TAGS))
    if len(tags_line) > 0 and (tags_line.find('  ') != -1 or tags_line.find('\n') != -1):
        tags_line = re_space_mult.sub(r' ', tags_line.replace('\n', ' '))
        setrootconf(Options.OPT_TAGS, tags_line)
    parse_suc, tags_list = parse_tags(tags_line)
    # append id boundaries tags if present in id fields and not in tags
    tags_str = ' '.join(normalize_tag(tag) for tag in tags_list)
    newstr.append(tags_str)
    # + module
    module_name = ProcModule.get_cur_module_name()
    newstr.append(OPTION_CMD_MODULE)
    newstr.append(module_name)
    # + path (tags included)
    pathstr = normalize_path(str(getrootconf(Options.OPT_PATH)))
    # if pathstr != normalize_path(path.abspath(curdir)):
    newstr.append(OPTION_CMD_PATH)
    newstr.append(f'\'{pathstr}\'')
    # + options
    addstr = OPTION_CMD_VIDEOS[OPTION_VALUES_VIDEOS.index(str(getrootconf(Options.OPT_VIDSETTING)))]  # type: str
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_IMAGES[OPTION_VALUES_IMAGES.index(str(getrootconf(Options.OPT_IMGSETTING)))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_PARCHI[OPTION_VALUES_PARCHI.index(str(getrootconf(Options.OPT_PARCHISETTING)))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_THREADING[OPTION_VALUES_THREADING.index(str(getrootconf(Options.OPT_THREADSETTING)))]
    if len(addstr) > 0:
        newstr.append(OPTION_CMD_THREADING_CMD)
        newstr.append(addstr)
    # date min / max
    today_str = datetime.today().strftime(FMT_DATE)
    for datestr in ((Options.OPT_DATEMIN, OPTION_CMD_DATEAFTER), (Options.OPT_DATEMAX, OPTION_CMD_DATEBEFORE)):
        while True:
            try:
                addstr = str(getrootconf(datestr[0]))
                assert DateValidator()(addstr)
                if (
                        (datestr[0] == Options.OPT_DATEMIN and addstr != DATE_MIN_DEFAULT) or
                        (datestr[0] == Options.OPT_DATEMAX and addstr != today_str)
                ):
                    newstr.append(datestr[1])
                    newstr.append(addstr)
                break
            except Exception:
                setrootconf(datestr[0], DATE_MIN_DEFAULT if datestr[0] == Options.OPT_DATEMIN else today_str)
    # headers
    addstr = window_hcookiesm().get_json_h()
    if len(addstr) > 2 and addstr != DEFAULT_HEADERS:  # != "'{}'"
        newstr.append(OPTION_CMD_HEADERS)
        newstr.append(addstr)
    # cookies
    addstr = window_hcookiesm().get_json_c()
    if len(addstr) > 2:  # != "{}"
        newstr.append(OPTION_CMD_COOKIES)
        newstr.append(addstr)
    # proxy
    addstr = str(getrootconf(Options.OPT_PROXYSTRING))
    if len(addstr) > 0:
        ptype = str(getrootconf(Options.OPT_PROXYTYPE))
        addstr = f'{ptype}://{addstr}'
        newstr.append(OPTION_CMD_PROXY)
        newstr.append(addstr)
    addstr = OPTION_CMD_IGNORE_PROXY[int(getrootconf(Options.OPT_IGNORE_PROXY))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_PROXY_NO_DOWNLOAD[int(getrootconf(Options.OPT_PROXY_NO_DOWNLOAD))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # prefix
    addstr = OPTION_CMD_FNAMEPREFIX[int(getrootconf(Options.OPT_FNAMEPREFIX))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # download mode
    if __RUXX_DEBUG__:
        addstr = OPTION_CMD_DOWNMODE[int(getrootconf(Options.OPT_DOWNLOAD_MODE))]
        if len(addstr) > 0:
            newstr.append(OPTION_CMD_DOWNMODE_CMD)
            newstr.append(addstr)
    # download limit
    if __RUXX_DEBUG__:
        addstr = str(getrootconf(Options.OPT_DOWNLOAD_LIMIT))
        if int(addstr) > 0:
            newstr.append(OPTION_CMD_DOWNLIMIT_CMD)
            newstr.append(addstr)
    # save tags (dump_tags)
    addstr = OPTION_CMD_SAVE_TAGS[int(getrootconf(Options.OPT_SAVE_TAGS))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # save sources (dump source)
    addstr = OPTION_CMD_SAVE_SOURCES[int(getrootconf(Options.OPT_SAVE_SOURCES))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # extend name with info
    addstr = OPTION_CMD_APPEND_SOURCE_AND_TAGS[int(getrootconf(Options.OPT_APPEND_SOURCE_AND_TAGS))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_WARN_NONEMPTY_DEST[int(getrootconf(Options.OPT_WARN_NONEMPTY_DEST))]
    if len(addstr) > 0:
        newstr.append(addstr)

    return newstr


def update_frame_cmdline() -> None:
    cant_update = False
    for gidx in {Globals.GOBJECT_FIELD_DATEMAX, Globals.GOBJECT_FIELD_DATEMIN}:
        cant_update |= is_focusing(gidx)

    if not cant_update:
        args_list = prepare_cmdline()
        newstr = ' '.join(args_list)
        oldstr = text_cmdm().get(1.0, END)
        if oldstr != f'{newstr}\n':
            text_cmdm().config(state=STATE_NORMAL)
            text_cmdm().delete(1.0, END)
            text_cmdm().insert(1.0, newstr)
            text_cmdm().config(state=STATE_DISABLED)

    rootm().after(int(GUI2_UPDATE_DELAY_DEFAULT * 3), update_frame_cmdline)


def check_tags_direct() -> None:
    global tags_check_thread

    def normalize_tag(tag: str) -> str:
        return tag.replace('+', '%2b').replace(' ', '+')

    config_global(Globals.GOBJECT_BUTTON_CHECKTAGS, state=STATE_DISABLED)
    menu_items.get(Menus.MENU_ACTIONS)[0].entryconfig(menu_items.get(Menus.MENU_ACTIONS)[1][1], state=STATE_DISABLED)

    cur_tags = str(getrootconf(Options.OPT_TAGS))

    count = 0
    mydwn = None  # type: Union[None, DownloaderRn, DownloaderRx]
    res, tags_list = parse_tags(cur_tags)
    if re_or_meta_group.match(cur_tags):  # `or` group with meta tag
        Logger.log('Error: cannot check tags with meta tag(s) within \'or\' group', False, False)
    elif res:
        mydwn = get_new_proc_module()
        tags_str = mydwn.get_tags_concat_char().join(normalize_tag(tag) for tag in tags_list)

        full_addr = mydwn.form_tags_search_address(tags_str, 1)
        # init proxy / headers & cookies if needed
        proxstr = str(getrootconf(Options.OPT_PROXYSTRING))
        if len(proxstr) > 0 and len(OPTION_CMD_IGNORE_PROXY[int(getrootconf(Options.OPT_IGNORE_PROXY))]) == 0:
            proxy = f'{str(getrootconf(Options.OPT_PROXYTYPE))}://{proxstr}'
            mydwn.proxies = {'http': proxy, 'https': proxy}
        else:
            mydwn.proxies = None
        headstr = window_hcookiesm().get_json_h()
        if len(headstr) > 4:  # != "'{}'"
            hj = json_loads(headstr)
            mydwn.add_headers.update(hj)
        cookstr = window_hcookiesm().get_json_c()
        if len(cookstr) > 4:  # != "'{}'"
            cj = json_loads(cookstr)
            mydwn.add_cookies.update(cj)
        mydwn.session = mydwn.make_session()

        try:
            count = mydwn.get_items_query_size_or_html(full_addr, 1)
            if not isinstance(count, int):
                count = 1
        except (Exception, SystemExit):
            pass

    downloading = is_downloading()
    if downloading is False:
        config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_PALEGREEN if count > 0 else COLOR_BROWN1)
        if mydwn and count > 0:
            Thread(target=lambda: messagebox.showinfo(title='', message=f'Found {count:d} results!', icon='info')).start()

    thread_sleep(1.5)

    if downloading is False:
        config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_WHITE)
        config_global(Globals.GOBJECT_BUTTON_CHECKTAGS, state=gobject_orig_states[Globals.GOBJECT_BUTTON_CHECKTAGS])
        menu_items.get(Menus.MENU_ACTIONS)[0].entryconfig(
            menu_items.get(Menus.MENU_ACTIONS)[1][1], state=menu_item_orig_states[Menus.MENU_ACTIONS][2])

    tags_check_thread = None


def check_tags_direct_do() -> None:
    global tags_check_thread

    if menu_items.get(Menus.MENU_ACTIONS)[0].entrycget(menu_items.get(Menus.MENU_ACTIONS)[1][1], 'state') == STATE_DISABLED:
        return

    assert tags_check_thread is None

    tags_check_thread = Thread(target=check_tags_direct)
    tags_check_thread.start()


def parse_tags_field(tags: str) -> bool:
    result, _ = parse_tags(tags)
    return result


def recheck_args() -> Tuple[bool, str]:
    # tags
    if len(str(getrootconf(Options.OPT_TAGS))) <= 0:
        return False, 'No tags specified'
    if not parse_tags_field(str(getrootconf(Options.OPT_TAGS))):
        return False, 'Invalid tags'
    # path
    pathstr = normalize_path(str(getrootconf(Options.OPT_PATH)))
    if len(pathstr) <= 0:
        return False, 'No path specified'
    if not path.isdir(pathstr[:(pathstr.find(SLASH) + 1)]):
        return False, 'Invalid path'
    # dates
    dateafter_str = '""'
    datebefore_str = '""'
    # date after
    try:
        dateafter_str = str(getrootconf(Options.OPT_DATEMIN))
        datetime.strptime(dateafter_str, FMT_DATE)
    except Exception:
        return False, f'{dateafter_str} is not a valid date format'
    # date before
    try:
        datebefore_str = str(getrootconf(Options.OPT_DATEMAX))
        datetime.strptime(datebefore_str, FMT_DATE)
    except Exception:
        return False, f'{datebefore_str} is not a valid date format'
    # dates minmax compare
    if datetime.strptime(datebefore_str, FMT_DATE) < datetime.strptime(dateafter_str, FMT_DATE):
        return False, 'Maximum date cannot be lower than minimum date'
    # Not downloading anything
    if str(getrootconf(Options.OPT_IMGSETTING)) == OPTION_VALUES_IMAGES[0] and \
            str(getrootconf(Options.OPT_VIDSETTING)) == OPTION_VALUES_VIDEOS[0] and \
            (not __RUXX_DEBUG__ or len(OPTION_CMD_DOWNMODE[int(getrootconf(Options.OPT_DOWNLOAD_MODE))]) == 0):
        return False, 'Not downloading anything'

    return True, ''


def is_downloading() -> bool:
    return (download_thread is not None) and download_threadm().is_alive()


def is_cheking_tags() -> bool:
    return tags_check_thread is not None


def update_download_state() -> None:
    global download_thread
    global prev_download_state

    downloading = is_downloading()
    if prev_download_state != downloading:
        update_widget_enabled_states()
        for gi in [g for g in Globals.__members__.values() if g < Globals.MAX_GOBJECTS]:  # type: Globals
            if gi in (Globals.GOBJECT_BUTTON_DOWNLOAD, Globals.GOBJECT_MODULE_ICON, Globals.GOBJECT_COMBOBOX_PARCHI):
                pass  # config_global(i, state=gobject_orig_states[i])
            elif gi == Globals.GOBJECT_BUTTON_CHECKTAGS:
                if not is_cheking_tags():
                    config_global(gi, state=(STATE_DISABLED if downloading else gobject_orig_states[gi]))
            else:
                config_global(gi, state=(STATE_DISABLED if downloading else gobject_orig_states[gi]))
        # special case 1: _download button: turn into cancel button
        dw_button = get_global(Globals.GOBJECT_BUTTON_DOWNLOAD)
        if downloading:
            dw_button.config(text='Cancel', command=cancel_download)
        else:
            dw_button.config(text='Download', command=do_download)

    if not downloading and (download_thread is not None):
        download_threadm().join()  # make thread terminate
        del download_thread
        download_thread = None

    prev_download_state = downloading

    rootm().after(int(THREAD_CHECK_PERIOD_DEFAULT), update_download_state)


def cancel_download() -> None:
    if is_downloading():
        download_threadm().killed = True


def do_download() -> None:
    global download_thread

    if menu_items.get(Menus.MENU_ACTIONS)[0].entrycget(menu_items.get(Menus.MENU_ACTIONS)[1][0], 'state') == STATE_DISABLED:
        return

    suc, msg = recheck_args()
    if not suc:
        messagebox.showwarning('Nope', msg)
        return

    get_global(Globals.GOBJECT_BUTTON_DOWNLOAD).focus_force()

    # force cmd line update
    update_frame_cmdline()
    # prepare arg list
    cmdline = prepare_cmdline()

    # hide modifyable windows
    window_proxym().hide()
    window_hcookiesm().hide()

    # reset temporarily modified elements/widgets
    config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_WHITE)

    # launch
    download_thread = Thread(target=start_download_thread, args=(cmdline,))
    download_threadm().killed = False
    download_threadm().gui = True
    download_threadm().start()

    unfocus_buttons_once()


def start_download_thread(cmdline: List[str]) -> None:
    global dwn
    global download_thread

    arg_list = prepare_arglist(cmdline[1:])
    with get_new_proc_module() as dwn:
        dwn.launch(arg_list)


def unfocus_buttons() -> None:
    unfocus_buttons_once()
    rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 3, unfocus_buttons)


def unfocus_buttons_once() -> None:
    for g in BUTTONS_TO_UNFOCUS:
        if is_focusing(g):
            rootm().focus_set()
            break


# def quit_with_msg(title='Exit', message='Really?') -> None:
#     if messagebox.askokcancel(title=title, message=message, icon='warning'):
#         sys.exit()


def help_tags(title: str = 'Tags') -> None:
    message = HELP_TAGS_MSG_RX if ProcModule.is_rx() else HELP_TAGS_MSG_RN
    messagebox.showinfo(title=title, message=message, icon='info')


def help_about(title: str = f'About {APP_NAME}', message: str = ABOUT_MSG) -> None:
    messagebox.showinfo(title=title, message=message, icon='info')


def load_id_list() -> None:
    filepath = ask_filename((('Text files', '*.txt'), ('All files', '*.*')))
    if filepath:
        success, file_tags = prepare_tags_list(filepath)
        if success:
            setrootconf(Options.OPT_TAGS, file_tags)
            # reset settings for immediate downloading
            setrootconf(Options.OPT_DATEMIN, DATE_MIN_DEFAULT)
            setrootconf(Options.OPT_DATEMAX, datetime.today().strftime(FMT_DATE))
        else:
            messagebox.showwarning(message=f'Unable to load ids from {filepath[filepath.rfind("/") + 1:]}!')


def ask_filename(ftypes: Iterable[Tuple[str, str]]) -> str:
    fullpath = filedialog.askopenfilename(filetypes=ftypes, initialdir=get_curdir())
    if fullpath and len(fullpath) > 0:
        setrootconf(Options.OPT_LASTPATH, fullpath[:normalize_path(fullpath, False).rfind(SLASH) + 1])  # not bound
    return fullpath


def browse_path() -> None:
    loc = str(filedialog.askdirectory(initialdir=get_curdir()))
    if len(loc) > 0:
        setrootconf(Options.OPT_PATH, loc)
        setrootconf(Options.OPT_LASTPATH, loc[:normalize_path(loc, False).rfind(SLASH) + 1])  # not bound


def register_menu_command(label: str, command: Callable[[], None], hotkey_opt: Options = None, do_bind: bool = False,
                          icon: PhotoImage = None) -> None:
    try:
        accelerator = hotkey_text(hotkey_opt)
    except Exception:
        accelerator = None
    c_menum().add_command(label=label, image=icon, compound=LEFT, command=command, accelerator=accelerator)
    if accelerator and (do_bind is True):
        rootm().bind(hotkeys.get(hotkey_opt), func=lambda _: command())


def register_submenu_command(label: str, command: Callable[[], None], hotkey_opt: Options = None, do_bind: bool = False,
                             icon: PhotoImage = None) -> None:
    try:
        accelerator = hotkey_text(hotkey_opt)
    except Exception:
        accelerator = None
    c_submenum().add_command(label=label, image=icon, compound=LEFT, command=command, accelerator=accelerator)
    if accelerator and (do_bind is True):
        rootm().bind(hotkeys.get(hotkey_opt), func=lambda _: command())


def register_menu_checkbutton(label: str, variablename: str, command: Callable = None, hotkey_str: str = None) -> None:
    BooleanVar(rootm(), False, variablename)
    c_menum().add_checkbutton(label=label, command=command, variable=variablename, accelerator=hotkey_str)


def register_menu_radiobutton(label: str, variablename: str, value: int, command: Callable = None, hotkey_str: str = None) -> None:
    if variablename not in int_vars:
        int_vars[variablename] = IntVar(rootm(), value=value, name=variablename)  # needed so it won't be discarded
    c_menum().add_radiobutton(label=label, command=command, variable=int_vars.get(variablename), value=value, accelerator=hotkey_str)


def register_menu_separator() -> None:
    c_menum().add_separator()

# end static methods

#########################################
#        PROGRAM WORKFLOW START         #
#########################################


def finalize_additional_windows() -> None:
    Logger.wnd.finalize()
    window_proxym().finalize()
    window_hcookiesm().finalize()
    Logger.print_pending_strings()


def init_menus() -> None:
    # 1) File
    register_menu('File', Menus.MENU_FILE)
    register_menu_command('Save settings...', Settings.save_settings, Options.OPT_ISSAVESETTINGSOPEN, True, get_icon(Icons.ICON_SAVE))
    register_menu_command('Load settings...', Settings.load_settings, Options.OPT_ISLOADSETTINGSOPEN, True, get_icon(Icons.ICON_OPEN))
    register_menu_separator()
    register_menu_command('Reset all settings', Settings.reset_all_settings)
    register_menu_separator()
    register_menu_command('Open download folder', open_download_folder, Options.OPT_ACTION_OPEN_DWN_FOLDER, True)
    register_menu_separator()
    register_menu_command('Exit', sys.exit)
    if sys.platform != PLATFORM_WINDOWS:
        c_menum().entryconfig(5, state=STATE_DISABLED)  # disable 'Open download folder'
    # 2) Edit
    register_menu('Edit', Menus.MENU_EDIT)
    register_menu_checkbutton('Prefix file names with \'rx_\'', CVARS.get(Options.OPT_FNAMEPREFIX))
    register_menu_checkbutton('Save tags', CVARS.get(Options.OPT_SAVE_TAGS))
    register_menu_checkbutton('Save source links', CVARS.get(Options.OPT_SAVE_SOURCES))
    register_menu_checkbutton('Extend file names with extra info', CVARS.get(Options.OPT_APPEND_SOURCE_AND_TAGS))
    register_menu_checkbutton('Warn if download folder is not empty', CVARS.get(Options.OPT_WARN_NONEMPTY_DEST))
    # 3) View
    register_menu('View')
    register_menu_checkbutton('Log', CVARS.get(Options.OPT_ISLOGOPEN), Logger.wnd.toggle_visibility, hotkey_text(Options.OPT_ISLOGOPEN))
    if CAN_MANIPULATE_CONSOLE and __RUXX_DEBUG__:
        register_menu_checkbutton('Console', CVARS.get(Options.OPT_ISCONSOLELOGOPEN), toggle_console)
    # 4) Module
    register_menu('Module', Menus.MENU_MODULE)
    register_menu_radiobutton('rx', CVARS.get(Options.OPT_MODULE), ProcModule.PROC_RX, lambda: set_proc_module(ProcModule.PROC_RX))
    register_menu_radiobutton('rn', CVARS.get(Options.OPT_MODULE), ProcModule.PROC_RN, lambda: set_proc_module(ProcModule.PROC_RN))
    # 5) Connection
    register_menu('Connection', Menus.MENU_CONNECTION)
    register_menu_command('Headers / Cookies...', window_hcookiesm().toggle_visibility, Options.OPT_ISHCOOKIESOPEN)
    register_menu_command('Set proxy...', window_proxym().ask, Options.OPT_ISPROXYOPEN)
    register_menu_checkbutton('Download without proxy', CVARS.get(Options.OPT_PROXY_NO_DOWNLOAD))
    register_menu_checkbutton('Ignore proxy', CVARS.get(Options.OPT_IGNORE_PROXY))
    # 6) Action
    register_menu('Actions', Menus.MENU_ACTIONS)
    register_menu_command('Download', do_download, Options.OPT_ACTION_DOWNLOAD, True)
    register_menu_separator()
    register_menu_command('Check tags', check_tags_direct_do, Options.OPT_ACTION_CHECKTAGS, True)
    # 7) Tools
    register_menu('Tools', Menus.MENU_TOOLS)
    register_menu_command('Load from ID list...', load_id_list)
    register_menu_separator()
    register_menu_command('Un-tag files...', untag_files_do)
    register_menu_command('Re-tag files...', retag_files_do)
    register_menu_separator()
    register_submenu('Sort files into subfolders...')
    register_submenu_command('by type', sort_files_by_type_do)
    register_submenu_command('by size', sort_files_by_size_do)
    register_submenu_command('by score', sort_files_by_score_do)
    # 8) Help
    register_menu('Help')
    register_menu_command('Tags', help_tags)
    register_menu_separator()
    register_menu_command('About...', help_about, Options.OPT_ISABOUTOPEN, True)
    # register_menu_command('License', help_license)
    # 9) Debug
    if __RUXX_DEBUG__:
        register_menu('Debug', Menus.MENU_DEBUG)
        register_menu_radiobutton('Download: full', CVARS.get(Options.OPT_DOWNLOAD_MODE), DownloadModes.DOWNLOAD_FULL.value)
        register_menu_radiobutton('Download: skip', CVARS.get(Options.OPT_DOWNLOAD_MODE), DownloadModes.DOWNLOAD_SKIP.value)
        register_menu_radiobutton('Download: touch', CVARS.get(Options.OPT_DOWNLOAD_MODE), DownloadModes.DOWNLOAD_TOUCH.value)
        register_menu_command('Set download limit (0)...', set_download_limit)
        register_menu_command('Reset download limit', reset_download_limit)


def init_gui() -> None:
    global tags_check_thread

    create_base_window_widgets()

    # additional windows
    Logger.wnd = LogWindow(rootm())
    Logger.wnd.window.wm_protocol('WM_DELETE_WINDOW', Logger.wnd.on_destroy)
    init_additional_windows()
    rootm().bind_all(hotkeys.get(Options.OPT_ISLOGOPEN), func=lambda _: Logger.wnd.toggle_visibility())
    rootm().bind_all(hotkeys.get(Options.OPT_ISPROXYOPEN), func=lambda e: window_proxym().ask() if e.state != 0x20000 else None)
    rootm().bind_all(hotkeys.get(Options.OPT_ISHCOOKIESOPEN), func=lambda _: window_hcookiesm().toggle_visibility())
    rootm().bind(BUT_ALT_F4, func=lambda _: rootm().destroy())
    Logger.wnd.window.bind(BUT_ALT_F4, func=lambda _: Logger.wnd.hide() if Logger.wnd.visible else None)
    window_hcookiesm().window.bind(BUT_ALT_F4, func=lambda _: window_hcookiesm().hide() if window_hcookiesm().visible else None)
    window_proxym().window.bind(BUT_ALT_F4, func=lambda _: window_proxym().cancel() if window_proxym().visible else None)
    # Main menu
    init_menus()

    get_global(Globals.GOBJECT_BUTTON_CHECKTAGS).config(command=check_tags_direct_do)
    get_global(Globals.GOBJECT_BUTTON_OPENFOLDER).config(command=browse_path)
    get_global(Globals.GOBJECT_BUTTON_DOWNLOAD).config(command=do_download)

    # Init settings if needed
    setrootconf(Options.OPT_TAGS, 'sfw')
    setrootconf(Options.OPT_DOWNLOAD_LIMIT, 0)
    setrootconf(Options.OPT_FNAMEPREFIX, True)
    setrootconf(Options.OPT_APPEND_SOURCE_AND_TAGS, True)
    setrootconf(Options.OPT_IGNORE_PROXY, IS_IDE)
    setrootconf(Options.OPT_SAVE_TAGS, not IS_IDE)
    setrootconf(Options.OPT_SAVE_SOURCES, not IS_IDE)
    setrootconf(Options.OPT_WARN_NONEMPTY_DEST, not IS_IDE)

    # Background looping tasks
    update_frame_cmdline()
    update_progressbar()
    update_statusbar()
    update_download_state()
    # unfocus_buttons

    rootm().adjust_size()

    finalize_additional_windows()

    Settings.try_pick_autoconfig()
    Settings.save_initial_settings()

    # Init finish
    rootm().finalize()


# Helper funcs: solve unnecessary NoneType warnings
def download_threadm() -> Thread:
    assert download_thread
    return download_thread


def dwnm() -> Union[DownloaderRn, DownloaderRx]:
    global dwn

    if dwn is None:
        dwn = DOWNLOADERS_BY_PROC_MODULE.get(ProcModule.CUR_PROC_MODULE)()

    return dwn

# End Helper funcs


#########################################
#         PROGRAM WORKFLOW END          #
#########################################

#########################################
#             PROGRAM ENTRY             #
#########################################

if __name__ == '__main__':
    running_in_gui = len(sys.argv) < 2
    Logger.init(not running_in_gui)
    ensure_compatibility(running_in_gui)

    if not running_in_gui:
        current_process().killed = False
        arglist = prepare_arglist(sys.argv[1:])
        set_proc_module(PROC_MODULES_BY_ABBR[arglist.module])
        with get_new_proc_module() as dwn:
            dwn.launch(arglist)
    else:
        if CAN_MANIPULATE_CONSOLE:
            Logger.pending_strings.append('[Launcher] Hiding own console...')
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            ctypes.windll.user32.DeleteMenu(
                ctypes.windll.user32.GetSystemMenu(ctypes.windll.kernel32.GetConsoleWindow(), 0), 0xF060, ctypes.c_ulong(0)
            )
            console_shown = False
        init_gui()

    sys.exit(0)

#########################################
#              PROGRAM END              #
#########################################

#
#
#########################################
