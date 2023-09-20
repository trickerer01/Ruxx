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
from datetime import datetime
from multiprocessing.dummy import current_process
from os import path, system, makedirs
from threading import Thread
from time import sleep as thread_sleep
from tkinter import messagebox, END
from typing import Optional, Union, List, Tuple, Sequence

# internal
from app_cmdargs import prepare_arglist
from app_defines import (
    DownloaderStates, DownloadModes, STATE_WORK_START, MODULE_ABBR_RX, MODULE_ABBR_RN, MODULE_ABBR_RS, DEFAULT_HEADERS, DATE_MIN_DEFAULT,
    PLATFORM_WINDOWS, STATUSBAR_INFO_MAP, PROGRESS_VALUE_NO_DOWNLOAD, PROGRESS_VALUE_DOWNLOAD, FMT_DATE, max_progress_value_for_state,
)
from app_download_rn import DownloaderRn
from app_download_rx import DownloaderRx
from app_download_rs import DownloaderRs
from app_file_sorter import sort_files_by_type, FileTypeFilter, sort_files_by_size, sort_files_by_score
from app_file_tagger import untag_files, retag_files
from app_gui_base import (
    AskFileTypeFilterWindow, AskFileSizeFilterWindow, AskFileScoreFilterWindow, AskIntWindow, setrootconf, rootm, getrootconf,
    window_hcookiesm, window_proxym, window_timeoutm, register_menu, register_submenu, GetRoot, create_base_window_widgets,
    text_cmdm, get_icon, init_additional_windows, get_global, config_global, is_global_disabled, is_menu_disabled, is_focusing,
    set_console_shown, unfocus_buttons_once, help_tags, help_about, load_id_list, browse_path, register_menu_command, toggle_console,
    register_submenu_command, register_menu_checkbutton, register_menu_radiobutton, register_menu_separator, get_all_media_files_in_cur_dir,
    update_lastpath, hotkey_text, config_menu,
)
from app_gui_defines import (
    STATE_DISABLED, STATE_NORMAL, COLOR_WHITE, COLOR_BROWN1, COLOR_PALEGREEN, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES,
    OPTION_VALUES_THREADING, OPTION_CMD_VIDEOS, OPTION_CMD_IMAGES, OPTION_CMD_THREADING_CMD, OPTION_CMD_THREADING, OPTION_CMD_FNAMEPREFIX,
    OPTION_CMD_DOWNMODE_CMD, OPTION_CMD_DOWNMODE, OPTION_CMD_DOWNLIMIT_CMD, OPTION_CMD_SAVE_TAGS, OPTION_CMD_SAVE_SOURCES,
    OPTION_CMD_SAVE_COMMENTS, OPTION_CMD_DATEAFTER, OPTION_CMD_DATEBEFORE, OPTION_CMD_PATH, OPTION_CMD_COOKIES, OPTION_CMD_HEADERS,
    OPTION_CMD_PROXY, OPTION_CMD_IGNORE_PROXY, OPTION_CMD_PROXY_NO_DOWNLOAD, OPTION_CMD_TIMEOUT, GUI2_UPDATE_DELAY_DEFAULT,
    THREAD_CHECK_PERIOD_DEFAULT, SLASH, BUT_ALT_F4, OPTION_CMD_APPEND_SOURCE_AND_TAGS, OPTION_CMD_WARN_NONEMPTY_DEST, OPTION_CMD_MODULE,
    OPTION_CMD_PARCHI, OPTION_VALUES_PARCHI,
    ProcModule, menu_items, menu_item_orig_states, gobject_orig_states, Options, Globals, Menus, SubMenus, Icons, CVARS, hotkeys,
)
from app_re import re_space_mult
from app_logger import Logger
from app_revision import __RUXX_DEBUG__
from app_settings import Settings
from app_tags_parser import reset_last_tags, parse_tags
from app_utils import normalize_path, confirm_yes_no, ensure_compatibility
from app_validators import DateValidator

__all__ = ('run_ruxx', 'run_ruxx_gui')

# loaded
download_thread = None  # type: Optional[Thread]
tags_check_thread = None  # type: Optional[Thread]
prev_download_state = True
IS_RAW = '_sitebuiltins' in sys.modules  # ran from console (shell or IDE)
IS_IDE = '_virtualenv' in sys.modules  # ran from IDE
CONSOLEVAL = ctypes.windll.kernel32.GetConsoleProcessList(ctypes.byref(ctypes.c_int(0)), 1) if sys.platform == PLATFORM_WINDOWS else -1
HAS_OWN_CONSOLE = CONSOLEVAL == 2  # 1 process is a main window, 2 is the console itself, 3 would be external console
CAN_MANIPULATE_CONSOLE = HAS_OWN_CONSOLE and not IS_RAW
# end loaded

# MODULES
dwn = None  # type: Union[None, DownloaderRn, DownloaderRx, DownloaderRs]
DOWNLOADERS_BY_PROC_MODULE = {
    ProcModule.PROC_RX: DownloaderRx,
    ProcModule.PROC_RN: DownloaderRn,
    ProcModule.PROC_RS: DownloaderRs,
}
PROC_MODULES_BY_ABBR = {
    MODULE_ABBR_RX: ProcModule.PROC_RX,
    MODULE_ABBR_RN: ProcModule.PROC_RN,
    MODULE_ABBR_RS: ProcModule.PROC_RS,
}
# END MODULES


# static methods
def file_worker_report(succ_count: int, total_count: int, word1: str) -> None:
    if succ_count == total_count:
        Logger.log(f'Successfully {word1}ed {total_count:d} file(s).', False, False)
    elif succ_count > 0:
        Logger.log(f'Warning: only {succ_count:d} / {total_count:d} files were {word1}ed.', False, False)
    else:
        Logger.log(f'An error occured while {word1}ing {total_count:d} files.', False, False)


def untag_files_do() -> None:
    filelist = get_all_media_files_in_cur_dir()
    if len(filelist) == 0:
        return
    update_lastpath(filelist[0])
    untagged_count = untag_files(filelist)
    file_worker_report(untagged_count, len(filelist), 'un-tagg')


def retag_files_do() -> None:
    filelist = get_all_media_files_in_cur_dir()
    if len(filelist) == 0:
        return
    update_lastpath(filelist[0])
    module = get_new_proc_module()
    retagged_count = retag_files(filelist, module.get_re_tags_to_process(), module.get_re_tags_to_exclude())
    file_worker_report(retagged_count, len(filelist), 're-tagg')


def sort_files_by_type_do() -> None:
    filelist = get_all_media_files_in_cur_dir()
    if len(filelist) == 0:
        return
    aw = AskFileTypeFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)
    filter_type = aw.value()
    if filter_type == FileTypeFilter.FILTER_INVALID:
        return
    update_lastpath(filelist[0])
    result = sort_files_by_type(filelist, filter_type)
    file_worker_report(result, len(filelist), 'sort')


def sort_files_by_size_do() -> None:
    filelist = get_all_media_files_in_cur_dir()
    if len(filelist) == 0:
        return
    aw = AskFileSizeFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)
    thresholds_mb = aw.value()
    if thresholds_mb is None:
        return
    update_lastpath(filelist[0])
    result = sort_files_by_size(filelist, thresholds_mb)
    file_worker_report(result, len(filelist), 'sort')


def sort_files_by_score_do() -> None:
    filelist = get_all_media_files_in_cur_dir()
    if len(filelist) == 0:
        return
    aw = AskFileScoreFilterWindow(rootm())
    aw.finalize()
    rootm().wait_window(aw.window)
    thresholds = aw.value()
    if thresholds is None:
        return
    update_lastpath(filelist[0])
    result = sort_files_by_score(filelist, thresholds)
    file_worker_report(result, len(filelist), 'sort')


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
    config_menu(Menus.MENU_DEBUG, SubMenus.DLIMSET, label=f'Set download limit ({limit})...')
    Logger.log(f'Download limit set to {limit:d} item(s).', False, False)


def reset_download_limit() -> None:
    setrootconf(Options.OPT_DOWNLOAD_LIMIT, 0)
    config_menu(Menus.MENU_DEBUG, SubMenus.DLIMSET, label='Set download limit (0)...')
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


def get_new_proc_module() -> Union[DownloaderRn, DownloaderRx, DownloaderRs]:
    return DOWNLOADERS_BY_PROC_MODULE[ProcModule.CUR_PROC_MODULE]()


def set_proc_module(dwnmodule: int) -> None:
    global dwn

    ProcModule.set(dwnmodule)
    dwn = None

    # prefix option
    prefix_opt_text = f'Prefix file names with \'{ProcModule.get_cur_module_name()}_\''

    if GetRoot() is not None:
        config_menu(Menus.MENU_EDIT, SubMenus.PREFIX, label=prefix_opt_text)
        # icon
        icons = {ProcModule.PROC_RX: Icons.ICON_RX, ProcModule.PROC_RN: Icons.ICON_RN, ProcModule.PROC_RS: Icons.ICON_RS}
        config_global(Globals.GOBJECT_MODULE_ICON, image=get_icon(icons.get(ProcModule.get())))
        # enable/disable features specific to the module
        update_widget_enabled_states()

    # reset tags parser
    reset_last_tags()


def update_widget_enabled_states() -> None:
    downloading = is_downloading()
    for i in [m for m in Menus.__members__.values() if m < Menus.MAX_MENUS]:  # type: Menus
        menu = menu_items.get(i)
        if menu:
            for j in menu.statefuls:
                if i == Menus.MENU_ACTIONS and j == SubMenus.CHECKTAGS and is_cheking_tags():  # Check tags, disabled when active
                    newstate = STATE_DISABLED
                elif i == Menus.MENU_EDIT and j == SubMenus.SSOURCE and ProcModule.is_rs():  # Save sources, disabled for RS
                    newstate = STATE_DISABLED
                else:
                    newstate = STATE_DISABLED if downloading else menu_item_orig_states[i][j]
                config_menu(i, j, state=newstate)
    for gi in [g for g in Globals.__members__.values() if g < Globals.MAX_GOBJECTS]:  # type: Globals
        if gi == Globals.GOBJECT_COMBOBOX_PARCHI:
            config_global(gi, state=(STATE_DISABLED if not ProcModule.is_rx() else gobject_orig_states[gi]))
        elif gi in {Globals.GOBJECT_FIELD_DATEMIN, Globals.GOBJECT_FIELD_DATEMAX}:
            config_global(gi, state=(STATE_DISABLED if ProcModule.is_rs() else gobject_orig_states[gi]))


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
    if len(addstr) > 0 and not is_global_disabled(Globals.GOBJECT_COMBOBOX_VIDEOS):
        newstr.append(addstr)
    addstr = OPTION_CMD_IMAGES[OPTION_VALUES_IMAGES.index(str(getrootconf(Options.OPT_IMGSETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.GOBJECT_COMBOBOX_IMAGES):
        newstr.append(addstr)
    addstr = OPTION_CMD_PARCHI[OPTION_VALUES_PARCHI.index(str(getrootconf(Options.OPT_PARCHISETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.GOBJECT_COMBOBOX_PARCHI):
        newstr.append(addstr)
    addstr = OPTION_CMD_THREADING[OPTION_VALUES_THREADING.index(str(getrootconf(Options.OPT_THREADSETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.GOBJECT_COMBOBOX_THREADING):
        newstr.append(OPTION_CMD_THREADING_CMD)
        newstr.append(addstr)
    # date min / max
    if not is_global_disabled(Globals.GOBJECT_FIELD_DATEMIN) and not is_global_disabled(Globals.GOBJECT_FIELD_DATEMAX):
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
    # timeout
    addstr = str(getrootconf(Options.OPT_TIMEOUTSTRING))
    if len(addstr) > 0:
        newstr.append(OPTION_CMD_TIMEOUT)
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
    # save sources (dump_sources)
    addstr = OPTION_CMD_SAVE_SOURCES[int(getrootconf(Options.OPT_SAVE_SOURCES))]
    if len(addstr) > 0 and not is_menu_disabled(Menus.MENU_EDIT, SubMenus.SSOURCE):
        newstr.append(addstr)
    # save comments (dump_comments)
    addstr = OPTION_CMD_SAVE_COMMENTS[int(getrootconf(Options.OPT_SAVE_COMMENTS))]
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


def start_check_tags_thread(cmdline: List[str]) -> None:
    global dwn
    arg_list = prepare_arglist(cmdline[1:])
    with get_new_proc_module() as dwn:
        dwn.launch_check_tags(arg_list)


def check_tags_direct_do() -> None:
    global tags_check_thread
    unfocus_buttons_once()
    if is_menu_disabled(Menus.MENU_ACTIONS, SubMenus.CHECKTAGS):
        return

    suc, msg = recheck_args()
    if not suc:
        Thread(target=lambda: messagebox.showwarning('Nope', msg)).start()
        return

    update_frame_cmdline()
    # hide modifyable windows
    window_proxym().hide()
    window_hcookiesm().hide()

    # reset temporarily modified elements/widgets
    config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_WHITE)
    config_global(Globals.GOBJECT_BUTTON_CHECKTAGS, state=STATE_DISABLED)
    config_menu(Menus.MENU_ACTIONS, SubMenus.CHECKTAGS, state=STATE_DISABLED)

    # launch
    cmdline = prepare_cmdline()
    unfocus_buttons_once()
    try:
        tags_check_thread = Thread(target=start_check_tags_thread, args=(cmdline,))
        tags_check_threadm().killed = False
        tags_check_threadm().gui = True
        tags_check_threadm().start()
        tags_check_threadm().join()
    except Exception:
        return
    finally:
        tags_check_thread = None

    count = dwnm().total_count
    downloading = is_downloading()
    if downloading is False:
        config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_PALEGREEN if count > 0 else COLOR_BROWN1)
        if count > 0:
            Thread(target=lambda: messagebox.showinfo(title='', message=f'Found {count:d} results!', icon='info')).start()

    thread_sleep(1.5)

    if downloading is False:
        config_global(Globals.GOBJECT_FIELD_TAGS, bg=COLOR_WHITE)
        config_global(Globals.GOBJECT_BUTTON_CHECKTAGS, state=gobject_orig_states[Globals.GOBJECT_BUTTON_CHECKTAGS])
        config_menu(Menus.MENU_ACTIONS, SubMenus.CHECKTAGS, state=menu_item_orig_states[Menus.MENU_ACTIONS][2])


def check_tags_direct() -> None:
    Thread(target=check_tags_direct_do).start()


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

    if is_menu_disabled(Menus.MENU_ACTIONS, SubMenus.DOWNLOAD):
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
    arg_list = prepare_arglist(cmdline[1:])
    with get_new_proc_module() as dwn:
        dwn.launch_download(arg_list)

# end static methods

#########################################
#        PROGRAM WORKFLOW START         #
#########################################


def finalize_additional_windows() -> None:
    Logger.wnd.finalize()
    window_proxym().finalize()
    window_hcookiesm().finalize()
    window_timeoutm().finalize()
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
        config_menu(Menus.MENU_FILE, SubMenus.OPENFOLDER, state=STATE_DISABLED)  # disable 'Open download folder'
    # 2) Edit
    register_menu('Edit', Menus.MENU_EDIT)
    register_menu_checkbutton('Prefix file names with \'rx_\'', CVARS.get(Options.OPT_FNAMEPREFIX))
    register_menu_checkbutton('Save tags', CVARS.get(Options.OPT_SAVE_TAGS))
    register_menu_checkbutton('Save source links', CVARS.get(Options.OPT_SAVE_SOURCES))
    register_menu_checkbutton('Save comments', CVARS.get(Options.OPT_SAVE_COMMENTS))
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
    register_menu_radiobutton('rs', CVARS.get(Options.OPT_MODULE), ProcModule.PROC_RS, lambda: set_proc_module(ProcModule.PROC_RS))
    # 5) Connection
    register_menu('Connection', Menus.MENU_CONNECTION)
    register_menu_command('Headers / Cookies...', window_hcookiesm().toggle_visibility, Options.OPT_ISHCOOKIESOPEN)
    register_menu_command('Set proxy...', window_proxym().ask, Options.OPT_ISPROXYOPEN)
    register_menu_command('Set timeout...', window_timeoutm().ask, Options.OPT_ISTIMEOUTOPEN)
    register_menu_checkbutton('Download without proxy', CVARS.get(Options.OPT_PROXY_NO_DOWNLOAD))
    register_menu_checkbutton('Ignore proxy', CVARS.get(Options.OPT_IGNORE_PROXY))
    # 6) Action
    register_menu('Actions', Menus.MENU_ACTIONS)
    register_menu_command('Download', do_download, Options.OPT_ACTION_DOWNLOAD, True)
    register_menu_separator()
    register_menu_command('Check tags', check_tags_direct, Options.OPT_ACTION_CHECKTAGS, True)
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
    # Create all app windows
    create_base_window_widgets()
    init_additional_windows()
    # Window hotkeys in order
    rootm().bind_all(hotkeys.get(Options.OPT_ISLOGOPEN), func=lambda _: Logger.wnd.toggle_visibility())
    rootm().bind_all(hotkeys.get(Options.OPT_ISPROXYOPEN), func=lambda e: window_proxym().ask() if e.state != 0x20000 else None)
    rootm().bind_all(hotkeys.get(Options.OPT_ISHCOOKIESOPEN), func=lambda _: window_hcookiesm().toggle_visibility())
    rootm().bind_all(hotkeys.get(Options.OPT_ISTIMEOUTOPEN), func=lambda e: window_timeoutm().ask() if e.state != 0x20000 else None)
    rootm().bind(BUT_ALT_F4, func=lambda _: rootm().destroy())
    Logger.wnd.window.bind(BUT_ALT_F4, func=lambda _: Logger.wnd.hide() if Logger.wnd.visible else None)
    window_hcookiesm().window.bind(BUT_ALT_F4, func=lambda _: window_hcookiesm().hide() if window_hcookiesm().visible else None)
    window_proxym().window.bind(BUT_ALT_F4, func=lambda _: window_proxym().cancel() if window_proxym().visible else None)
    window_timeoutm().window.bind(BUT_ALT_F4, func=lambda _: window_timeoutm().cancel() if window_timeoutm().visible else None)
    # Main menu
    init_menus()
    # Menu hotkeys
    get_global(Globals.GOBJECT_BUTTON_CHECKTAGS).config(command=check_tags_direct)
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
    setrootconf(Options.OPT_SAVE_COMMENTS, not IS_IDE)
    setrootconf(Options.OPT_WARN_NONEMPTY_DEST, not IS_IDE)
    # Background looping tasks
    update_frame_cmdline()
    update_progressbar()
    update_statusbar()
    update_download_state()
    # Clamp main window and make non-resizable
    rootm().adjust_size()
    # Update window geometry and set own widget bindings
    finalize_additional_windows()
    # OS-specific
    #  Linux
    #   Allow os to automatically adjust the size of message windows
    rootm().option_add('*Dialog.msg.width', 0)
    rootm().option_add('*Dialog.msg.wrapLength', 0)
    # Init Settings system
    Settings.initialize(on_proc_module_change_callback=set_proc_module)
    Settings.try_pick_autoconfig()
    Settings.save_initial_settings()
    # Main window binding, BG fix-ups and main loop
    rootm().finalize()


# Helper wrappers: solve unnecessary NoneType warnings
def download_threadm() -> Thread:
    assert download_thread
    return download_thread


def tags_check_threadm() -> Thread:
    assert tags_check_thread
    return tags_check_thread


def dwnm() -> Union[DownloaderRn, DownloaderRx, DownloaderRs]:
    global dwn
    if dwn is None:
        dwn = DOWNLOADERS_BY_PROC_MODULE.get(ProcModule.CUR_PROC_MODULE)()
    return dwn

# End Helper wrappers


#########################################
#        PROGRAM WORKFLOW END           #
#########################################

#########################################
#             PROGRAM ENTRY             #
#########################################

def run_ruxx(args: Sequence[str]) -> None:
    Logger.init(True)
    ensure_compatibility()
    current_process().killed = False
    arglist = prepare_arglist(args)
    set_proc_module(PROC_MODULES_BY_ABBR[arglist.module])
    with get_new_proc_module() as cdwn:
        if arglist.get_maxid:
            cdwn.launch_get_max_id(arglist)
        else:
            cdwn.launch_download(arglist)


def run_ruxx_gui() -> None:
    Logger.init(False)
    ensure_compatibility()
    if CAN_MANIPULATE_CONSOLE:
        Logger.pending_strings.append('[Launcher] Hiding own console...')
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        ctypes.windll.user32.DeleteMenu(
            ctypes.windll.user32.GetSystemMenu(ctypes.windll.kernel32.GetConsoleWindow(), 0), 0xF060, ctypes.c_ulong(0)
        )
        set_console_shown(False)
    init_gui()
    Logger.init(True)
    cancel_download()


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        run_ruxx(sys.argv[1:])
    else:
        run_ruxx_gui()
    sys.exit(0)

#########################################
#             PROGRAM END               #
#########################################

#
#
#########################################
