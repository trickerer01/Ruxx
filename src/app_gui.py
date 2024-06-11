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
from os import path, system, makedirs
from threading import Thread
from time import sleep as thread_sleep
from tkinter import END, messagebox
from typing import Optional, List, Tuple

# internal
from app_cmdargs import prepare_arglist
from app_debug import __RUXX_DEBUG__
from app_defines import (
    DownloaderStates, DownloadModes, STATE_WORK_START, DEFAULT_HEADERS, DATE_MIN_DEFAULT, PLATFORM_WINDOWS, STATUSBAR_INFO_MAP,
    PROGRESS_VALUE_NO_DOWNLOAD, PROGRESS_VALUE_DOWNLOAD, FMT_DATE, max_progress_value_for_state,
)
from app_download import Downloader
from app_downloaders import get_new_downloader
from app_file_sorter import sort_files_by_type, FileTypeFilter, sort_files_by_size, sort_files_by_score
from app_file_tagger import untag_files, retag_files
from app_gui_base import (
    AskFileTypeFilterWindow, AskFileSizeFilterWindow, AskFileScoreFilterWindow, AskIntWindow, GetRoot, setrootconf, rootm, getrootconf,
    window_hcookiesm, window_proxym, window_timeoutm, window_retriesm, register_menu, register_submenu, create_base_window_widgets,
    text_cmdm, get_icon, init_additional_windows, get_global, config_global, is_global_disabled, is_menu_disabled, is_focusing,
    set_console_shown, unfocus_buttons_once, help_tags, help_about, load_id_list, browse_path, register_menu_command, toggle_console,
    register_submenu_command, register_menu_checkbutton, register_menu_radiobutton, register_menu_separator, get_all_media_files_in_cur_dir,
    update_lastpath, hotkey_text, config_menu,
)
from app_gui_defines import (
    STATE_DISABLED, STATE_NORMAL, COLOR_WHITE, COLOR_BROWN1, COLOR_PALEGREEN, OPTION_VALUES_VIDEOS, OPTION_VALUES_IMAGES,
    OPTION_VALUES_THREADING, OPTION_CMD_VIDEOS, OPTION_CMD_IMAGES, OPTION_CMD_THREADING_CMD, OPTION_CMD_THREADING, OPTION_CMD_FNAMEPREFIX,
    OPTION_CMD_DOWNMODE_CMD, OPTION_CMD_DOWNMODE, OPTION_CMD_DOWNLIMIT_CMD, OPTION_CMD_SAVE_TAGS, OPTION_CMD_SAVE_SOURCES,
    OPTION_CMD_SAVE_COMMENTS, OPTION_CMD_INFO_SAVE_MODE, OPTION_CMD_DATEAFTER_CMD, OPTION_CMD_DATEBEFORE_CMD, OPTION_CMD_PATH_CMD,
    OPTION_CMD_COOKIES_CMD, OPTION_CMD_HEADERS_CMD, OPTION_CMD_PROXY_CMD, OPTION_CMD_IGNORE_PROXY, OPTION_CMD_PROXY_NO_DOWNLOAD,
    OPTION_CMD_TIMEOUT_CMD, OPTION_CMD_RETRIES_CMD, GUI2_UPDATE_DELAY_DEFAULT, THREAD_CHECK_PERIOD_DEFAULT, SLASH, BUT_ALT_F4,
    OPTION_CMD_APPEND_SOURCE_AND_TAGS, OPTION_CMD_VERBOSE, OPTION_CMD_WARN_NONEMPTY_DEST, OPTION_CMD_MODULE_CMD, OPTION_CMD_PARCHI,
    OPTION_VALUES_PARCHI, OPTION_CMD_CACHE_PROCCED_HTML,
    Options, Globals, Menus, SubMenus, Icons, CVARS, hotkeys, menu_items, menu_item_orig_states, gobject_orig_states,
)
from app_module import ProcModule
from app_logger import Logger, trace
from app_settings import Settings
from app_tags_parser import reset_last_tags, parse_tags
from app_utils import normalize_path, confirm_yes_no, ensure_compatibility
from app_validators import DateValidator

__all__ = ('run_ruxx_gui',)

# loaded
download_thread: Optional[Thread] = None
tags_check_thread: Optional[Thread] = None
prev_download_state = True
IS_WIN = sys.platform == PLATFORM_WINDOWS
IS_RAW = '_sitebuiltins' in sys.modules  # ran from console (shell or IDE)
IS_IDE = '_virtualenv' in sys.modules  # ran from IDE
CONSOLEVAL = ctypes.windll.kernel32.GetConsoleProcessList(ctypes.byref(ctypes.c_int(0)), 1) if IS_WIN else -1
HAS_OWN_CONSOLE = CONSOLEVAL == 2  # 1 process is a main window, 2 is the console itself, 3 would be external console
CAN_MANIPULATE_CONSOLE = HAS_OWN_CONSOLE and not IS_RAW
# end loaded

# MODULES
dwn: Optional[Downloader] = None
# END MODULES


# static methods
def file_worker_report(succ_count: int, total_count: int, word1: str) -> None:
    if succ_count == total_count:
        trace(f'Successfully {word1}ed {total_count:d} file(s).')
    elif succ_count > 0:
        trace(f'Warning: only {succ_count:d} / {total_count:d} files were {word1}ed.')
    else:
        trace(f'An error occured while {word1}ing {total_count:d} files.')


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
    module = get_new_downloader()
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
    if filter_type == FileTypeFilter.INVALID:
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
            trace(f'Invalid limt value \'{aw.variable.get()}\'')
        return
    setrootconf(Options.DOWNLOAD_LIMIT, limit)
    config_menu(Menus.DEBUG, SubMenus.DLIMSET, label=f'Set download limit ({limit})...')
    trace(f'Download limit set to {limit:d} item(s).')


def reset_download_limit() -> None:
    setrootconf(Options.DOWNLOAD_LIMIT, 0)
    config_menu(Menus.DEBUG, SubMenus.DLIMSET, label='Set download limit (0)...')
    trace('Download limit was reset.')


def open_download_folder() -> None:
    cur_path = normalize_path(getrootconf(Options.PATH))

    if not path.isdir(cur_path[:(cur_path.find(SLASH) + 1)]):
        messagebox.showerror('Open download folder', f'Path \'{cur_path}\' is invalid.')
        return

    if not path.isdir(cur_path):
        if not confirm_yes_no('Open download folder', f'Path \'{cur_path}\' doesn\'t exist. Create it?'):
            return
        try:
            makedirs(cur_path)
        except Exception:
            trace(f'Unable to create path \'{cur_path}\'.')
            return

    try:
        res = system(f'start "" "{path.abspath(cur_path)}"')
        if res != 0:
            trace(f'Couldn\'t open \'{cur_path}\', error: {res:d}.')
    except Exception:
        trace(f'Couldn\'t open \'{cur_path}\'.')


def set_proc_module(dwnmodule: int) -> None:
    global dwn

    ProcModule.set(dwnmodule)
    dwn = None

    # prefix option
    prefix_opt_text = f'Prefix file names with \'{ProcModule.get_cur_module_name()}_\''

    if GetRoot() is not None:
        config_menu(Menus.EDIT, SubMenus.PREFIX, label=prefix_opt_text)
        # icon
        icontypes = {ProcModule.PROC_RX: Icons.RX, ProcModule.PROC_RN: Icons.RN, ProcModule.PROC_RS: Icons.RS}
        config_global(Globals.MODULE_ICON, image=get_icon(icontypes.get(ProcModule.get(), Icons.RX)))
        # enable/disable features specific to the module
        update_widget_enabled_states()

    # reset tags parser
    reset_last_tags()


def update_widget_enabled_states() -> None:
    downloading = is_downloading()
    i: Menus
    for i in [m for m in Menus.__members__.values() if m < Menus.MAX_MENUS]:
        menu = menu_items.get(i)
        if menu:
            for j in menu.statefuls:
                if i == Menus.ACTIONS and j == SubMenus.CHECKTAGS and is_cheking_tags():  # Check tags, disabled when active
                    newstate = STATE_DISABLED
                elif i == Menus.EDIT and j == SubMenus.SSOURCE and ProcModule.is_rs():  # Save sources, disabled for RS
                    newstate = STATE_DISABLED
                else:
                    newstate = STATE_DISABLED if downloading else menu_item_orig_states[i][j]
                config_menu(i, j, state=newstate)
    gi: Globals
    for gi in [g for g in Globals.__members__.values() if g < Globals.MAX_GOBJECTS]:
        if gi == Globals.COMBOBOX_PARCHI:
            newstate = STATE_DISABLED if not ProcModule.is_rx() else gobject_orig_states[gi]
            config_global(gi, state=newstate)
        elif gi in {Globals.FIELD_DATEMIN, Globals.FIELD_DATEMAX}:
            newstate = STATE_DISABLED if ProcModule.is_rs() else gobject_orig_states[gi]
            get_global(gi).set_state(newstate)
            config_global(gi, state=newstate)


def update_progressbar() -> None:
    try:
        progress_value: Optional[int] = None
        if is_downloading():
            if dwnm().current_state == DownloaderStates.DOWNLOADING:
                progress_value = PROGRESS_VALUE_NO_DOWNLOAD
                if dwnm().total_count_all > 0 and dwnm().processed_count > 0:
                    progress_value += int((PROGRESS_VALUE_DOWNLOAD / dwnm().total_count_all) * dwnm().processed_count)
            else:
                progress_value = 0
                state = STATE_WORK_START
                num_states_no_download = DownloaderStates.DOWNLOADING - STATE_WORK_START
                while state <= num_states_no_download and state < dwnm().current_state:
                    base_value = max_progress_value_for_state(state)
                    progress_value += base_value
                    state = DownloaderStates(state + 1)

        setrootconf(Options.PROGRESS, progress_value or 0)
    except Exception:
        pass

    rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 6, update_progressbar)


def update_statusbar() -> None:
    try:
        state_texts = STATUSBAR_INFO_MAP[dwnm().current_state]
        status_str = state_texts[0]
        if state_texts[1]:
            status_str += str(getattr(dwnm(), state_texts[1], 0))
        if state_texts[2] and state_texts[3] and getattr(dwnm(), state_texts[3], 0) > 0:
            status_str += f'{state_texts[2]}{str(getattr(dwnm(), state_texts[3]))}'

        setrootconf(Options.STATUS, status_str)
    except Exception:
        pass

    rootm().after(GUI2_UPDATE_DELAY_DEFAULT // 6, update_statusbar)


def prepare_cmdline() -> List[str]:
    # base
    newstr = ['Cmd:']
    # + tags
    _, tags_list = parse_tags(str(getrootconf(Options.TAGS)))
    tags_str = ' '.join(tag.replace('+', '%2b').replace(' ', '+') for tag in tags_list)
    newstr.append(tags_str)
    # + module
    module_name = ProcModule.get_cur_module_name()
    newstr.append(OPTION_CMD_MODULE_CMD)
    newstr.append(module_name)
    # + path (tags included)
    pathstr = normalize_path(str(getrootconf(Options.PATH)))
    # if pathstr != normalize_path(path.abspath(curdir)):
    newstr.append(OPTION_CMD_PATH_CMD)
    newstr.append(f'\'{pathstr}\'')
    # + options
    addstr: str
    addstr = OPTION_CMD_VIDEOS[OPTION_VALUES_VIDEOS.index(str(getrootconf(Options.VIDSETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.COMBOBOX_VIDEOS):
        newstr.append(addstr)
    addstr = OPTION_CMD_IMAGES[OPTION_VALUES_IMAGES.index(str(getrootconf(Options.IMGSETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.COMBOBOX_IMAGES):
        newstr.append(addstr)
    addstr = OPTION_CMD_PARCHI[OPTION_VALUES_PARCHI.index(str(getrootconf(Options.PARCHISETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.COMBOBOX_PARCHI):
        newstr.append(addstr)
    addstr = OPTION_CMD_THREADING[OPTION_VALUES_THREADING.index(str(getrootconf(Options.THREADSETTING)))]
    if len(addstr) > 0 and not is_global_disabled(Globals.COMBOBOX_THREADING):
        newstr.append(OPTION_CMD_THREADING_CMD)
        newstr.append(addstr)
    # date min / max
    if not is_global_disabled(Globals.FIELD_DATEMIN) and not is_global_disabled(Globals.FIELD_DATEMAX):
        today_str = datetime.today().strftime(FMT_DATE)
        for datestr in ((Options.DATEMIN, OPTION_CMD_DATEAFTER_CMD), (Options.DATEMAX, OPTION_CMD_DATEBEFORE_CMD)):
            while True:
                try:
                    addstr = str(getrootconf(datestr[0]))
                    assert DateValidator()(addstr)
                    if (
                            (datestr[0] == Options.DATEMIN and addstr != DATE_MIN_DEFAULT) or
                            (datestr[0] == Options.DATEMAX and addstr != today_str)
                    ):
                        newstr.append(datestr[1])
                        newstr.append(addstr)
                    break
                except Exception:
                    setrootconf(datestr[0], DATE_MIN_DEFAULT if datestr[0] == Options.DATEMIN else today_str)
    # headers
    addstr = window_hcookiesm().get_json_h()
    if len(addstr) > 2 and addstr != DEFAULT_HEADERS:  # != "'{}'"
        newstr.append(OPTION_CMD_HEADERS_CMD)
        newstr.append(addstr)
    # cookies
    addstr = window_hcookiesm().get_json_c()
    if len(addstr) > 2:  # != "{}"
        newstr.append(OPTION_CMD_COOKIES_CMD)
        newstr.append(addstr)
    # proxy
    addstr = str(getrootconf(Options.PROXYSTRING))
    if len(addstr) > 0:
        ptype = str(getrootconf(Options.PROXYTYPE))
        addstr = f'{ptype}://{addstr}'
        newstr.append(OPTION_CMD_PROXY_CMD)
        newstr.append(addstr)
    addstr = OPTION_CMD_IGNORE_PROXY[int(getrootconf(Options.IGNORE_PROXY))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_PROXY_NO_DOWNLOAD[int(getrootconf(Options.PROXY_NO_DOWNLOAD))]
    if len(addstr) > 0:
        newstr.append(addstr)
    addstr = OPTION_CMD_CACHE_PROCCED_HTML[int(getrootconf(Options.CACHE_PROCCED_HTML))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # timeout
    addstr = str(getrootconf(Options.TIMEOUTSTRING))
    if len(addstr) > 0:
        newstr.append(OPTION_CMD_TIMEOUT_CMD)
        newstr.append(addstr)
    # retries
    addstr = str(getrootconf(Options.RETRIESSTRING))
    if len(addstr) > 0:
        newstr.append(OPTION_CMD_RETRIES_CMD)
        newstr.append(addstr)
    # prefix
    addstr = OPTION_CMD_FNAMEPREFIX[int(getrootconf(Options.FNAMEPREFIX))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # download mode
    if __RUXX_DEBUG__:
        addstr = OPTION_CMD_DOWNMODE[int(getrootconf(Options.DOWNLOAD_MODE))]
        if len(addstr) > 0:
            newstr.append(OPTION_CMD_DOWNMODE_CMD)
            newstr.append(addstr)
    # download limit
    if __RUXX_DEBUG__:
        addstr = str(getrootconf(Options.DOWNLOAD_LIMIT))
        if int(addstr) > 0:
            newstr.append(OPTION_CMD_DOWNLIMIT_CMD)
            newstr.append(addstr)
    # save tags (dump_tags)
    addstr = OPTION_CMD_SAVE_TAGS[int(getrootconf(Options.SAVE_TAGS))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # save sources (dump_sources)
    addstr = OPTION_CMD_SAVE_SOURCES[int(getrootconf(Options.SAVE_SOURCES))]
    if len(addstr) > 0 and not is_menu_disabled(Menus.EDIT, SubMenus.SSOURCE):
        newstr.append(addstr)
    # save comments (dump_comments)
    addstr = OPTION_CMD_SAVE_COMMENTS[int(getrootconf(Options.SAVE_COMMENTS))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # info save mode: per file (dump_per_item) or merge lists (or normal)
    addstr = OPTION_CMD_INFO_SAVE_MODE[int(getrootconf(Options.INFO_SAVE_MODE))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # extend name with info
    addstr = OPTION_CMD_APPEND_SOURCE_AND_TAGS[int(getrootconf(Options.APPEND_SOURCE_AND_TAGS))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # warn on non-empty folder
    addstr = OPTION_CMD_WARN_NONEMPTY_DEST[int(getrootconf(Options.WARN_NONEMPTY_DEST))]
    if len(addstr) > 0:
        newstr.append(addstr)
    # verbose log
    addstr = OPTION_CMD_VERBOSE[int(getrootconf(Options.VERBOSE))]
    if len(addstr) > 0:
        newstr.append(addstr)

    return newstr


def update_frame_cmdline() -> None:
    cant_update = False
    for gidx in {Globals.FIELD_DATEMIN, Globals.FIELD_DATEMAX}:
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
    with get_new_downloader() as dwn:
        dwn.save_cmdline(cmdline)
        dwn.launch_check_tags(arg_list)


def check_tags_direct_do() -> None:
    global tags_check_thread
    unfocus_buttons_once()
    if is_menu_disabled(Menus.ACTIONS, SubMenus.CHECKTAGS):
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
    config_global(Globals.FIELD_TAGS, bg=COLOR_WHITE)
    config_global(Globals.BUTTON_CHECKTAGS, state=STATE_DISABLED)
    config_menu(Menus.ACTIONS, SubMenus.CHECKTAGS, state=STATE_DISABLED)

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
        config_global(Globals.FIELD_TAGS, bg=COLOR_PALEGREEN if count > 0 else COLOR_BROWN1)
        if count > 0:
            Thread(target=lambda: messagebox.showinfo(title='', message=f'Found {count:d} results!', icon='info')).start()

    thread_sleep(1.5)

    if downloading is False:
        config_global(Globals.FIELD_TAGS, bg=COLOR_WHITE)
        config_global(Globals.BUTTON_CHECKTAGS, state=gobject_orig_states[Globals.BUTTON_CHECKTAGS])
        config_menu(Menus.ACTIONS, SubMenus.CHECKTAGS, state=menu_item_orig_states[Menus.ACTIONS][2])


def check_tags_direct() -> None:
    Thread(target=check_tags_direct_do).start()


def recheck_args() -> Tuple[bool, str]:
    # tags
    if len(str(getrootconf(Options.TAGS))) <= 0:
        return False, 'No tags specified'
    parse_result, _ = parse_tags(str(getrootconf(Options.TAGS)))
    if not parse_result:
        return False, 'Invalid tags'
    # path
    pathstr = normalize_path(path.expanduser(str(getrootconf(Options.PATH))))
    if len(pathstr) <= 0:
        return False, 'No path specified'
    if not path.isdir(pathstr[:(pathstr.find(SLASH) + 1)]):
        return False, 'Invalid path'
    # dates
    dateafter_str = '""'
    datebefore_str = '""'
    # date after
    try:
        dateafter_str = str(getrootconf(Options.DATEMIN))
        datetime.strptime(dateafter_str, FMT_DATE)
    except Exception:
        return False, f'{dateafter_str} is not a valid date format'
    # date before
    try:
        datebefore_str = str(getrootconf(Options.DATEMAX))
        datetime.strptime(datebefore_str, FMT_DATE)
    except Exception:
        return False, f'{datebefore_str} is not a valid date format'
    # dates minmax compare
    if datetime.strptime(datebefore_str, FMT_DATE) < datetime.strptime(dateafter_str, FMT_DATE):
        return False, 'Maximum date cannot be lower than minimum date'
    # Not downloading anything
    if (str(getrootconf(Options.IMGSETTING)) == OPTION_VALUES_IMAGES[0] and
        str(getrootconf(Options.VIDSETTING)) == OPTION_VALUES_VIDEOS[0] and
       (not __RUXX_DEBUG__ or len(OPTION_CMD_DOWNMODE[int(getrootconf(Options.DOWNLOAD_MODE))]) == 0)):
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
        gi: Globals
        for gi in [g for g in Globals.__members__.values() if g < Globals.MAX_GOBJECTS]:
            if gi in (Globals.BUTTON_DOWNLOAD, Globals.MODULE_ICON, Globals.COMBOBOX_PARCHI):
                pass  # config_global(i, state=gobject_orig_states[i])
            elif gi == Globals.BUTTON_CHECKTAGS:
                if not is_cheking_tags():
                    config_global(gi, state=(STATE_DISABLED if downloading else gobject_orig_states[gi]))
            else:
                config_global(gi, state=(STATE_DISABLED if downloading else gobject_orig_states[gi]))
        # special case 1: _download button: turn into cancel button
        dw_button = get_global(Globals.BUTTON_DOWNLOAD)
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

    if is_menu_disabled(Menus.ACTIONS, SubMenus.DOWNLOAD):
        return

    suc, msg = recheck_args()
    if not suc:
        messagebox.showwarning('Nope', msg)
        return

    get_global(Globals.BUTTON_DOWNLOAD).focus_force()

    # force cmd line update
    update_frame_cmdline()
    # prepare arg list
    cmdline = prepare_cmdline()

    # hide modifyable windows
    window_proxym().hide()
    window_hcookiesm().hide()

    # reset temporarily modified elements/widgets
    config_global(Globals.FIELD_TAGS, bg=COLOR_WHITE)

    # launch
    download_thread = Thread(target=start_download_thread, args=(cmdline,))
    download_threadm().killed = False
    download_threadm().gui = True
    download_threadm().start()

    unfocus_buttons_once()


def start_download_thread(cmdline: List[str]) -> None:
    global dwn
    arg_list = prepare_arglist(cmdline[1:])
    with get_new_downloader() as dwn:
        dwn.save_cmdline(cmdline)
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
    window_retriesm().finalize()
    Logger.print_pending_strings()


def init_menus() -> None:
    # 1) File
    register_menu('File', Menus.FILE)
    register_menu_command('Save settings...', Settings.save_settings, Options.ISSAVESETTINGSOPEN, True, get_icon(Icons.SAVE))
    register_menu_command('Load settings...', Settings.load_settings, Options.ISLOADSETTINGSOPEN, True, get_icon(Icons.OPEN))
    register_menu_separator()
    register_menu_command('Reset all settings', Settings.reset_all_settings)
    register_menu_separator()
    register_menu_command('Open download folder', open_download_folder, Options.ACTION_OPEN_DWN_FOLDER, IS_WIN)
    register_menu_separator()
    register_menu_command('Exit', sys.exit)
    if not IS_WIN:
        config_menu(Menus.FILE, SubMenus.OPENFOLDER, state=STATE_DISABLED)  # disable 'Open download folder'
    # 2) Edit
    register_menu('Edit', Menus.EDIT)
    register_menu_checkbutton('Prefix file names with \'rx_\'', CVARS.get(Options.FNAMEPREFIX))
    register_menu_checkbutton('Save tags', CVARS.get(Options.SAVE_TAGS))
    register_menu_checkbutton('Save source links', CVARS.get(Options.SAVE_SOURCES))
    register_menu_checkbutton('Save comments', CVARS.get(Options.SAVE_COMMENTS))
    register_menu_radiobutton('Save info normally', CVARS.get(Options.INFO_SAVE_MODE), 0)
    register_menu_radiobutton('Save info per file', CVARS.get(Options.INFO_SAVE_MODE), 1)
    register_menu_radiobutton('Save and merge info lists', CVARS.get(Options.INFO_SAVE_MODE), 2)
    register_menu_checkbutton('Extend file names with extra info', CVARS.get(Options.APPEND_SOURCE_AND_TAGS))
    register_menu_checkbutton('Warn if download folder is not empty', CVARS.get(Options.WARN_NONEMPTY_DEST))
    register_menu_checkbutton('Verbose log', CVARS.get(Options.VERBOSE))
    # 3) View
    register_menu('View')
    register_menu_checkbutton('Log', CVARS.get(Options.ISLOGOPEN), Logger.wnd.toggle_visibility, hotkey_text(Options.ISLOGOPEN))
    if CAN_MANIPULATE_CONSOLE and __RUXX_DEBUG__:
        register_menu_checkbutton('Console', CVARS.get(Options.ISCONSOLELOGOPEN), toggle_console)
    # 4) Module
    register_menu('Module', Menus.MODULE)
    register_menu_radiobutton('rx', CVARS.get(Options.MODULE), ProcModule.PROC_RX, lambda: set_proc_module(ProcModule.PROC_RX))
    register_menu_radiobutton('rn', CVARS.get(Options.MODULE), ProcModule.PROC_RN, lambda: set_proc_module(ProcModule.PROC_RN))
    register_menu_radiobutton('rs', CVARS.get(Options.MODULE), ProcModule.PROC_RS, lambda: set_proc_module(ProcModule.PROC_RS))
    # 5) Connection
    register_menu('Connection', Menus.CONNECTION)
    register_menu_command('Headers / Cookies...', window_hcookiesm().toggle_visibility, Options.ISHCOOKIESOPEN)
    register_menu_command('Set proxy...', window_proxym().ask, Options.ISPROXYOPEN)
    register_menu_command('Set timeout...', window_timeoutm().ask, Options.ISTIMEOUTOPEN)
    register_menu_command('Set retries count...', window_retriesm().ask, Options.ISRETRIESOPEN)
    register_menu_checkbutton('Download without proxy', CVARS.get(Options.PROXY_NO_DOWNLOAD))
    register_menu_checkbutton('Ignore proxy', CVARS.get(Options.IGNORE_PROXY))
    register_menu_checkbutton('Cache processed HTML', CVARS.get(Options.CACHE_PROCCED_HTML))
    # 6) Action
    register_menu('Actions', Menus.ACTIONS)
    register_menu_command('Download', do_download, Options.ACTION_DOWNLOAD, True)
    register_menu_separator()
    register_menu_command('Check tags', check_tags_direct, Options.ACTION_CHECKTAGS, True)
    # 7) Tools
    register_menu('Tools', Menus.TOOLS)
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
    register_menu_command('About...', help_about, Options.ISABOUTOPEN, True)
    # 9) Debug
    if __RUXX_DEBUG__:
        register_menu('Debug', Menus.DEBUG)
        register_menu_radiobutton('Download: full', CVARS.get(Options.DOWNLOAD_MODE), DownloadModes.FULL.value)
        register_menu_radiobutton('Download: skip', CVARS.get(Options.DOWNLOAD_MODE), DownloadModes.SKIP.value)
        register_menu_radiobutton('Download: touch', CVARS.get(Options.DOWNLOAD_MODE), DownloadModes.TOUCH.value)
        register_menu_command('Set download limit (0)...', set_download_limit)
        register_menu_command('Reset download limit', reset_download_limit)


def init_gui() -> None:
    global tags_check_thread
    # Create all app windows
    create_base_window_widgets()
    init_additional_windows()
    # Window hotkeys in order
    rootm().bind_all(hotkeys.get(Options.ISLOGOPEN), func=lambda _: Logger.wnd.toggle_visibility())
    rootm().bind_all(hotkeys.get(Options.ISPROXYOPEN), func=lambda e: window_proxym().ask() if e.state != 0x20000 else None)
    rootm().bind_all(hotkeys.get(Options.ISHCOOKIESOPEN), func=lambda _: window_hcookiesm().toggle_visibility())
    rootm().bind_all(hotkeys.get(Options.ISTIMEOUTOPEN), func=lambda e: window_timeoutm().ask() if e.state != 0x20000 else None)
    rootm().bind_all(hotkeys.get(Options.ISRETRIESOPEN), func=lambda e: window_retriesm().ask() if e.state != 0x20000 else None)
    rootm().bind(BUT_ALT_F4, func=lambda _: rootm().destroy())
    Logger.wnd.window.bind(BUT_ALT_F4, func=lambda _: Logger.wnd.hide() if Logger.wnd.visible else None)
    window_hcookiesm().window.bind(BUT_ALT_F4, func=lambda _: window_hcookiesm().hide() if window_hcookiesm().visible else None)
    window_proxym().window.bind(BUT_ALT_F4, func=lambda _: window_proxym().cancel() if window_proxym().visible else None)
    window_timeoutm().window.bind(BUT_ALT_F4, func=lambda _: window_timeoutm().cancel() if window_timeoutm().visible else None)
    window_retriesm().window.bind(BUT_ALT_F4, func=lambda _: window_retriesm().cancel() if window_retriesm().visible else None)
    # Main menu
    init_menus()
    # Menu hotkeys
    get_global(Globals.BUTTON_CHECKTAGS).config(command=check_tags_direct)
    get_global(Globals.BUTTON_OPENFOLDER).config(command=browse_path)
    get_global(Globals.BUTTON_DOWNLOAD).config(command=do_download)
    # Init settings if needed
    setrootconf(Options.TAGS, 'sfw')
    setrootconf(Options.DOWNLOAD_LIMIT, 0)
    setrootconf(Options.FNAMEPREFIX, True)
    setrootconf(Options.APPEND_SOURCE_AND_TAGS, True)
    setrootconf(Options.IGNORE_PROXY, IS_IDE)
    setrootconf(Options.CACHE_PROCCED_HTML, IS_IDE)
    setrootconf(Options.SAVE_TAGS, not IS_IDE)
    setrootconf(Options.SAVE_SOURCES, not IS_IDE)
    setrootconf(Options.SAVE_COMMENTS, not IS_IDE)
    setrootconf(Options.WARN_NONEMPTY_DEST, not IS_IDE)
    # Background looping tasks
    update_frame_cmdline()
    update_progressbar()
    update_statusbar()
    update_download_state()
    # Clamp main window and make non-resizable
    rootm().adjust_position()
    # Update window geometry and set own widget bindings
    finalize_additional_windows()
    # OS-specific
    #  Linux
    #   Allow os to automatically adjust the size of message windows
    rootm().option_add('*Dialog.msg.width', 0)
    rootm().option_add('*Dialog.msg.wrapLength', 0)
    # Init Settings system
    Settings.initialize(tk=rootm(), on_proc_module_change_callback=set_proc_module)
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


def dwnm() -> Downloader:
    global dwn
    dwn = dwn or get_new_downloader()
    return dwn

# End Helper wrappers


#########################################
#        PROGRAM WORKFLOW END           #
#########################################

#########################################
#             PROGRAM ENTRY             #
#########################################

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

#########################################
#             PROGRAM END               #
#########################################

#
#
#########################################
