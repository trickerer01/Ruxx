# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
import sys
from abc import abstractmethod
from argparse import Namespace
from collections.abc import Iterable, MutableSet, Callable
from multiprocessing.dummy import Pool, current_process
from multiprocessing.pool import ThreadPool
from os import makedirs, listdir, path, remove
from threading import Thread, Lock as ThreadLock
from time import sleep as thread_sleep

# requirements
from iteration_utilities import unique_everseen

# internal
from app_debug import __RUXX_DEBUG__
from app_defines import (
    ThreadInterruptException, DownloaderStates, DownloadModes, ItemInfo, Comment, Mem,
    DATE_MIN_DEFAULT, CONNECT_TIMEOUT_BASE, UTF8, SOURCE_DEFAULT, PLATFORM_WINDOWS, DATE_MAX_DEFAULT, INT_BOUNDS_DEFAULT,
)
from app_download_base import DownloaderBase
from app_gui_defines import UNDERSCORE, NEWLINE, NEWLINE_X2
from app_logger import trace
from app_module import ProcModule
from app_network import ThreadedHtmlWorker, DownloadInterruptException, thread_exit
from app_re import re_favorited_by_tag, re_infolist_filename, re_pool_tag
from app_revision import APP_NAME, APP_VERSION
from app_tagger import append_filtered_tags
from app_tags_parser import convert_taglist
from app_task import extract_neg_and_groups, split_tags_into_tasks
from app_utils import confirm_yes_no, normalize_path, trim_undersores, format_score

# annotations
if False is True:
    # native
    from re import Match

__all__ = ('Downloader',)


LINE_BREAKS_AT = 99 if sys.platform == PLATFORM_WINDOWS else 90
BR = "=" * LINE_BREAKS_AT
"""line breaker"""


class Downloader(DownloaderBase):
    """
    Downloader !Abstract!
    """
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self._exception_checker: Thread | None = None
        self._thread_exception_lock = ThreadLock()
        self._thread_exceptions = dict[str, list[str]]()
        self._file_name_ext_cache: dict[str, tuple[str, str]] = dict()

    @property
    def total_count_all(self) -> int:
        return len(self.items_raw_all)

    def __del__(self) -> None:
        self.__cleanup()

    def __enter__(self) -> Downloader:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__cleanup()

    def __cleanup(self) -> None:
        # self.current_state = DownloaderStates.IDLE
        # self._file_name_ext_cache.clear()  # do not
        self.raw_html_cache.clear()
        self.filtered_out_ids_cache.clear()
        if self.session:
            self.session.close()
            self.session = None
        self._thread_exceptions.clear()
        if self._exception_checker:
            self._exception_checker.join()
            self._exception_checker = None

    def _start_exception_checker(self) -> None:
        self._exception_checker = Thread(target=self._thread_exceptions_checker)
        self._exception_checker.start()

    def _thread_exceptions_checker(self) -> None:
        while self.current_state != DownloaderStates.IDLE:
            with self._thread_exception_lock:
                if not all(not excl for excl in self._thread_exceptions):
                    break
            thread_sleep(0.5)

    # threaded
    def _on_thread_exception(self, thread_name: str) -> None:
        import traceback
        with self._thread_exception_lock:
            if thread_name not in self._thread_exceptions:
                self._thread_exceptions[thread_name] = list()
            self._thread_exceptions[thread_name].append(traceback.format_exc())
            self.my_root_thread.killed = True

    # threaded
    def _inc_proc_count(self) -> None:
        if self.maxthreads_items > 1:
            with self.item_lock:
                self.processed_count += 1
        else:
            self.processed_count += 1

    def save_cmdline(self, cmdline: Iterable[str]):
        self.cmdline = ' '.join(cmdline)

    def _at_launch(self) -> None:
        if self.verbose:
            trace(f'Python {sys.version}\nBase args: {" ".join(sys.argv)}\nMy args: {self.cmdline}')

    def get_tags_count(self, offset=0) -> int:
        """Public, needed by tests"""
        return len(self.tags_str_arr[offset].split(self._get_tags_concat_char()))

    def _register_parent_post(self, parents: MutableSet[str], item_id: str) -> None:
        if item_id not in self.known_parents:
            parents.add(item_id)

    def _try_append_extra_info(self, item_abbrname: str, maxlen: int) -> str:
        if not self.append_info:
            return item_abbrname

        if maxlen <= 0:
            return item_abbrname

        info = self.item_info_dict_all.get(item_abbrname)
        if info is None:
            return item_abbrname

        add_string = format_score(info.score)
        add_string = append_filtered_tags(add_string, info.tags, self.get_re_tags_to_process(), self.get_re_tags_to_exclude())
        add_string = trim_undersores(add_string)
        if len(add_string) > 0:
            add_string = f'{UNDERSCORE}{add_string}'
        while len(add_string) > maxlen:
            add_string = add_string[:max(0, add_string.rfind(UNDERSCORE))]

        return f'{item_abbrname}{add_string}'

    # threaded
    def _download(self, link: str, item_id: str, dest: str) -> None:
        if self.download_mode != DownloadModes.SKIP:
            with self.item_lock:
                if not path.isdir(self.dest_base):
                    try:
                        makedirs(self.dest_base)
                    except Exception:
                        thread_exit('ERROR: Unable to create subfolder!')

        try:
            result = self.download_file(link, item_id, dest, self.download_mode)
        except DownloadInterruptException:
            return

        if self.download_mode == DownloadModes.TOUCH or 0 < result.file_size == result.expected_size:
            result.result_str = f'{result.result_str}done ({result.file_size / Mem.MB:.2f} Mb)'
            with self.item_lock:
                self.success_count += 1
        else:
            result.result_str = f'{result.result_str}failed'
            if result.retries >= self.retries:
                result.result_str = f'{result.result_str} (could not download file after {result.retries:d} tries)'
            with self.item_lock:
                self.fail_count += 1
                self.failed_items.append(item_id)

        trace(result.result_str, True)

    @abstractmethod
    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        ...

    def _process_image(self, raw: str, item_id: str) -> None:
        self._send_to_download(raw, item_id, False)

    def _process_video(self, raw: str, item_id: str) -> None:
        self._send_to_download(raw, item_id, True)

    @abstractmethod
    def _process_item(self, raw: str) -> None:
        ...

    # threaded
    def _get_page_items(self, n: int, c_page: int, page_max: int) -> None:
        if self.is_killed():
            return

        items_per_page = self._get_items_per_page()
        pnum = n + 1
        prev_c = (c_page - 1) * items_per_page
        curmax_c = min(c_page * items_per_page, self.total_count_old)

        if not self.get_max_id:
            trace(f'page: {pnum:d} / {page_max + 1:d}\t({prev_c + 1:d}-{curmax_c:d} / {self.total_count_old:d})', True)

        try:
            while True:
                if self.is_killed():
                    return
                try:
                    raw_html_page = self.fetch_html(self._form_page_num_address(n))
                    if raw_html_page is None:
                        trace(f'ERROR: ProcPage: unable to retreive html for page {pnum:d}!', True)
                        raise ConnectionError

                    if self._is_search_overload_page(raw_html_page):
                        trace(f'Warning (W2): search was dropped on page {pnum:d} (too many threads?), retrying...', True)
                        raise KeyError

                    items_raw_temp = self._get_all_post_tags(raw_html_page)
                    if len(items_raw_temp) == 0:
                        trace(f'ERROR: ProcPage: cannot find picture or video on page {pnum:d}, retrying...', True)
                        if __RUXX_DEBUG__:
                            trace(f'HTML:\n{str(raw_html_page)}', True)
                        raise KeyError

                    break
                except ConnectionError:
                    return
                except KeyError:
                    items_raw_temp = list()
                    thread_sleep(min(10.0, max(CONNECT_TIMEOUT_BASE / 4, self.timeout / 2)))
                    continue

            # convert to pure strings
            self.items_raw_per_page[n] = [str(item) for item in items_raw_temp]
            with self.items_all_lock:
                total_count_temp = 0
                for k in self.items_raw_per_page:
                    total_count_temp += len(self.items_raw_per_page[k])
                self.total_count = total_count_temp

            if ProcModule.is_rp() or ProcModule.is_en():
                thread_sleep(1.0)
        except Exception:
            self._on_thread_exception(current_process().getName())
            raise

    def _fetch_task_items(self, tag_str: str) -> None:
        self.current_state = DownloaderStates.SEARCHING
        self.url = self._form_tags_search_address(tag_str)

        page_size = self._get_items_per_page()
        total_count_or_html = self._get_items_query_size_or_html(self.url)

        if isinstance(total_count_or_html, int):
            self.total_count = total_count_or_html
            self.minpage = 0
            self.maxpage = (self.total_count - 1) // page_size  # (self.total_count + page_size - 1) // page_size - 1

            if self.total_count <= 0:
                trace('Nothing to process: query result is empty')
                return

            trace(f'Total {self.total_count:d} item(s) found across {self._num_pages():d} page(s)')

            if 0 < self._get_max_search_depth() <= self.total_count:
                if self._supports_native_id_filter():
                    trace('\nFATAL: too many results, won\'t be able to fetch html for all the pages!\nTry adding an ID filter.')
                    return
                elif self._get_max_search_depth() < self.total_count:
                    trace('\nFATAL: too many results, won\'t be able to fetch html for all the pages!\nTry to refine your search.')
                    return
                else:
                    pages_depth = (self._get_max_search_depth() + self._get_items_per_page() - 1) // self._get_items_per_page()
                    trace(f'\nWarning (W3): too many results, can only fetch html for {pages_depth:d} pages!\n')
                    thread_sleep(4.0)

            self.total_pages = self._num_pages()

            if self._supports_native_id_filter() is False and self._get_id_bounds() != INT_BOUNDS_DEFAULT:
                pageargs_ex1 = ((DownloaderStates.SCANNING_PAGES1, True), (DownloaderStates.SCANNING_PAGES1, False))

                def page_filter_ex1(st: DownloaderStates, di: bool) -> int:
                    self.current_state = st
                    trace(f'[{self._get_module_abbr().upper()}] Looking for {"min" if di else "max"} page by id...')
                    return self._get_page_boundary_by_id(di, self._get_id_bounds()[1 - int(di)])

                for fstate, direction in pageargs_ex1:
                    if direction is True:
                        self.minpage = page_filter_ex1(fstate, direction)
                    else:
                        self.maxpage = page_filter_ex1(fstate, direction)
                    self.total_pages = self._num_pages()

            pageargs = ((DownloaderStates.SCANNING_PAGES1, True), (DownloaderStates.SCANNING_PAGES2, False))

            def page_filter(st: DownloaderStates, di: bool) -> int:
                self.current_state = st
                if not self.favorites_search_user and not self.pool_search_str:
                    trace(f'Looking for {"min" if di else "max"} page by date...')
                    return self._get_page_boundary_by_date(di)
                else:
                    return self.minpage if di else self.maxpage

            for fstate, direction in pageargs:
                if direction is True:
                    self.minpage = page_filter(fstate, direction)
                else:
                    self.maxpage = page_filter(fstate, direction)
                self.total_pages = self._num_pages()

            self.total_count = min(self._num_pages() * page_size, self.total_count)
            trace(f'new totalcount: {self.total_count:d}')
            trace(f'Scanning pages {self.minpage + 1:d} - {self.maxpage + 1:d}')

            self.total_count_old = self.total_count
            self.total_count = 0

            if self.maxthreads_items > 1 and self._num_pages() > 1:
                trace(f'  ...using {self.maxthreads_items:d} threads...')
                c_page = 0
                arr_temp = list()
                for n in range(self.minpage, self.maxpage + 1):
                    c_page += 1
                    arr_temp.append((n, c_page, self.maxpage))

                active_pool: ThreadPool
                with Pool(max(2, self.maxthreads_items // (4 if ProcModule.is_rp() else 2))) as active_pool:
                    ress = list()
                    for larr in arr_temp:
                        ress.append(active_pool.apply_async(self._get_page_items, args=larr))
                    active_pool.close()
                    while len(ress) > 0:
                        self.catch_cancel_or_ctrl_c()
                        while len(ress) > 0 and ress[0].ready():
                            ress.pop(0)
                        thread_sleep(0.2)
            else:
                c_page = 0
                for n in range(self.minpage, self.maxpage + 1):
                    self.catch_cancel_or_ctrl_c()
                    c_page += 1
                    self._get_page_items(n, c_page, self.maxpage)

            # move out async result into a linear array
            self.items_raw_per_task = [''] * self.total_count
            cur_idx = 0
            for k in range(self.minpage, self.maxpage + 1):
                cur_l = self.items_raw_per_page[k]
                for i in range(len(cur_l)):
                    self.items_raw_per_task[cur_idx] = cur_l[i]
                    cur_idx += 1

            self.items_raw_per_page.clear()

            self.items_raw_per_task = list(unique_everseen(self.items_raw_per_task))
        else:
            # we have been redirected to a page with our single result! compose item string manually
            if __RUXX_DEBUG__:
                trace('Warning (W1): A single match redirect was hit, forming item string manually')

            self.total_count = 1
            self.items_raw_per_task = [self._form_item_string_manually(total_count_or_html)]

    def _extract_custom_argument_tags(self) -> None:
        fav_user_tags = list(filter(lambda x: x, [re_favorited_by_tag.fullmatch(t) for t in self.tags_str_arr]))
        self._extract_favorite_user(fav_user_tags)
        if self.favorites_search_user and self._is_fav_search_conversion_required():
            [self.tags_str_arr.remove(f.string) for f in fav_user_tags]
        pool_tags = list(filter(lambda x: x, [re_pool_tag.fullmatch(t) for t in self.tags_str_arr]))
        self._extract_pool_id(pool_tags)
        if self.pool_search_str and self._is_pool_search_conversion_required():
            [self.tags_str_arr.remove(f.string) for f in pool_tags]
        assert not (not not self.favorites_search_user and not not self.pool_search_str)

    def _try_preprocess_favorites(self) -> None:
        # all we need here is to gather post ids from user's favorites page(s)
        if self.favorites_search_user:
            convert_msg = ', additional search will be performed' if self._is_fav_search_conversion_required() else ''
            trace(f'Favorites search detected ({self.favorites_search_user}){convert_msg}')
            if self._is_fav_search_conversion_required():
                if self._is_fav_search_single_step():
                    return
                try:
                    self._fetch_task_items(self.favorites_search_user)
                    self._extract_cur_task_infos(set())
                    ids_list = sorted(int(self.item_info_dict_per_task[full_id].id) for full_id in self.item_info_dict_per_task)
                    cc = self._get_tags_concat_char()
                    sc = self._get_idval_equal_seaparator()
                    ids_tag_base = f'{cc}~{cc}'.join(f'id{sc}{ii:d}' for ii in ids_list)
                    self.tags_str_arr[0:] = [f"({cc}{ids_tag_base}{cc})" if len(ids_list) > 1 else ids_tag_base, *self.tags_str_arr]
                    self.items_raw_per_task.clear()
                    self.item_info_dict_per_task.clear()
                    self.total_count_old = self.total_count = 0
                except ThreadInterruptException:
                    trace(f'task {self.current_task_num:d} aborted...')
                    raise
                except Exception:
                    trace(f'task {self.current_task_num:d} failed...')
                    raise
            self._clean_favorite_user()

    def _try_preprocess_pool(self) -> None:
        # all we need here is to gather post ids from pool page(s)
        if self.pool_search_str:
            convert_msg = ', additional search will be performed' if self._is_pool_search_conversion_required() else ''
            trace(f'Pool search detected ({self.pool_search_str}){convert_msg}')
            if self._is_pool_search_conversion_required():
                try:
                    self._fetch_task_items(self.pool_search_str)
                    self._extract_cur_task_infos(set())
                    ids_list = sorted(int(self.item_info_dict_per_task[full_id].id) for full_id in self.item_info_dict_per_task)
                    cc = self._get_tags_concat_char()
                    sc = self._get_idval_equal_seaparator()
                    ids_tag_base = f'{cc}~{cc}'.join(f'id{sc}{ii:d}' for ii in ids_list)
                    self.tags_str_arr[0:] = [f"({cc}{ids_tag_base}{cc})" if len(ids_list) > 1 else ids_tag_base, *self.tags_str_arr]
                    self.items_raw_per_task.clear()
                    self.item_info_dict_per_task.clear()
                    self.total_count_old = self.total_count = 0
                except ThreadInterruptException:
                    trace(f'task {self.current_task_num:d} aborted...')
                    raise
                except Exception:
                    trace(f'task {self.current_task_num:d} failed...')
                    raise
            self._clean_pool_id()

    def _after_filter(self, sleep_time: float = None) -> None:
        self.total_count = len(self.items_raw_all if self.current_state == DownloaderStates.DOWNLOADING else self.items_raw_per_task)
        trace(f'new totalcount: {self.total_count:d}')
        if sleep_time:
            thread_sleep(sleep_time)

    def _apply_filter(self, state: DownloaderStates, func: Callable[..., None], *args, sleep_time: float = None) -> None:
        self.current_state = state
        func(*args)
        self._after_filter(sleep_time)

    def _process_tags(self, tag_str: str) -> None:
        self._fetch_task_items(self._consume_custom_module_tags(tag_str))

        self._after_filter(0.025)

        self._apply_filter(DownloaderStates.FILTERING_ITEMS1, self._filter_last_items)
        self._apply_filter(DownloaderStates.FILTERING_ITEMS2, self._filter_first_items)
        self._apply_filter(DownloaderStates.FILTERING_ITEMS3, self._filter_items_by_type)
        self._apply_filter(DownloaderStates.FILTERING_ITEMS4, self._filter_items_by_previous_tasks)
        self._apply_filter(DownloaderStates.FILTERING_ITEMS4, self._filter_existing_items)

        # store items info for future processing
        # custom filters may exclude certain items from the infos dict
        task_parents: set[str] = set()
        self._extract_cur_task_infos(task_parents)

        if self.current_task_num <= self.orig_tasks_count:
            self._apply_filter(DownloaderStates.FILTERING_ITEMS4, self._filter_items_matching_negative_and_groups, task_parents)
            self._apply_filter(DownloaderStates.FILTERING_ITEMS4, self._filter_items_by_module_filters, task_parents)

        self.items_raw_all: list[str] = list(unique_everseen(self.items_raw_all + self.items_raw_per_task))
        self.item_info_dict_all.update(self.item_info_dict_per_task)
        if self.current_task_num > 1:
            trace(f'overall totalcount: {self.total_count_all:d}')

        if len(task_parents) > 0:
            trace(f'\nParent post(s) detected! Scheduling {len(task_parents):d} extra task(s)!')
            parent_messages = list()
            for parent in sorted(task_parents):
                new_task_str = f'parent{self._get_idval_equal_seaparator()}{parent}'
                self.tags_str_arr.append(new_task_str)
                parent_messages.append(f' {new_task_str}')
            trace('\n'.join(parent_messages))
            self.known_parents.update(task_parents)

    def _download_all(self) -> None:
        if self.total_count_all <= 0:
            trace('\nNothing to download: queue is empty')
            return

        if self.default_sort:
            self.items_raw_all = sorted(self.items_raw_all, key=lambda x: int(self._extract_id(x)))
            if self.current_task_num > 1:
                trace(f'\nApplying overall date filter after {self._tasks_count()} tasks...')
                self.items_raw_all.reverse()
                self._apply_filter(DownloaderStates.DOWNLOADING, self._filter_last_items)
                self._apply_filter(DownloaderStates.DOWNLOADING, self._filter_first_items)
                self.items_raw_all.reverse()
                ids_to_preserve = list()
                ids_to_pop = list()
                for index in range(len(self.items_raw_all)):
                    h = self._local_addr_from_string(str(self.items_raw_all[index]))
                    ids_to_preserve.append(f'{self._get_module_abbr_p()}{self._extract_id(h)}')
                for ifi in self.item_info_dict_all:
                    if ifi not in ids_to_preserve:
                        ids_to_pop.append(ifi)
                [self.item_info_dict_all.pop(ifi) for ifi in ids_to_pop]

        if self.reverse_download_order:
            self.items_raw_all.reverse()

        if self.download_limit > 0:
            if self.total_count_all > self.download_limit:
                trace(f'\nShrinking queue down to {self.download_limit:d} item(s)...')
                self.items_raw_all = self.items_raw_all[:self.download_limit]
            else:
                trace('\nShrinking queue down is not required!')

        min_id = self._extract_id(min(self.items_raw_all, key=lambda x: int(self._extract_id(x))))
        max_id = self._extract_id(max(self.items_raw_all, key=lambda x: int(self._extract_id(x))))
        trace(f'\nProcessing {self.total_count_all:d} item(s), bound {min_id} to {max_id}')

        self.current_state = DownloaderStates.DOWNLOADING
        trace(f'{self.total_count_all:d} item(s) scheduled, {self.maxthreads_items:d} thread(s) max\nWorking...\n')

        if self.maxthreads_items > 1 and self.total_count_all > 1:
            active_pool: ThreadPool
            with Pool(self.maxthreads_items) as active_pool:
                ress = list()
                for iarr in self.items_raw_all:
                    ress.append(active_pool.apply_async(self._process_item, args=(iarr,)))
                active_pool.close()
                while len(ress) > 0:
                    self.catch_cancel_or_ctrl_c()
                    while len(ress) > 0 and ress[0].ready():
                        ress.pop(0)
                    thread_sleep(0.2)
        else:
            for i in range(self.total_count_all):
                self.catch_cancel_or_ctrl_c()
                self._process_item(self.items_raw_all[i])

        skip_all = self.download_mode == DownloadModes.SKIP
        trace(f'\nAll {"skipped" if skip_all else "processed"} ({self.total_count_all:d} item(s))...')

    def _extract_negative_and_groups(self) -> None:
        split_always = self._split_or_group_into_tasks_always()
        self.tags_str_arr[0:], self.neg_and_groups = extract_neg_and_groups(' '.join(self.tags_str_arr), split_always)

    def _parse_tags(self) -> None:
        cc = self._get_tags_concat_char()
        sc = self._get_idval_equal_seaparator()
        split_always = self._split_or_group_into_tasks_always()
        # join by ' ' is required by tests, although normally len(args.tags) == 1
        for t in self.tags_str_arr:
            if len(t) > 2 and f'{t[0]}{t[-1]}' == '()' and f'{t[:2]}{t[-2:]}' != f'({"+" * 2})':
                thread_exit(f'Error: invalid tag \'{t}\'! Looks like \'or\' group but not fully contatenated by \'+\'')
        # conflict: non-default sorting
        sort_checker = (lambda s: (s.startswith('order=') and s != 'order=id_desc') if ProcModule.is_rn() else
                                  (s.startswith('sort:') and s != 'sort:id' and s != 'sort:id:desc'))
        self.default_sort = not any(sort_checker(tag) for tag in self.tags_str_arr)
        self.tags_str_arr[0:] = split_tags_into_tasks(self.tags_str_arr, cc, sc, split_always)
        self.orig_tasks_count = self._tasks_count()
        if not self.default_sort:
            if self._tasks_count() > 1:
                thread_exit('Error: cannot use non-default sorting with multi-task query!')
            if self.date_min != DATE_MIN_DEFAULT or self.date_max != DATE_MAX_DEFAULT:
                thread_exit('Error: cannot use both sort tag and date filter at the same time!')

    def _process_all_tags(self) -> None:
        if self.warn_nonempty:
            if self._has_gui():
                if path.isdir(self.dest_base) and len(listdir(self.dest_base)) > 0:
                    if not confirm_yes_no(title='Download', msg=f'Destination folder \'{self.dest_base}\' is not empty. Continue anyway?'):
                        return
            else:
                trace('Warning (W1): argument \'-warn_nonempty\' is ignored in non-GUI mode')

        if self.download_mode != DownloadModes.FULL:
            trace(f'{BR}\n\n(Emulation Mode)')
        trace(f'\n{BR}\n{APP_NAME} core ver {APP_VERSION}')
        trace(f'Starting {self._get_module_abbr().upper()} downloader', timestamp=True)
        trace(f'\n{len(self.neg_and_groups):d} \'excluded tags combination\' custom filter(s) parsed')
        trace(f'{self._tasks_count():d} task(s) scheduled:\n{NEWLINE.join(self.tags_str_arr)}\n\n{BR}')
        self.current_task_num = 0
        while self.current_task_num < self._tasks_count():  # tasks count may increase during this loop
            self.current_task_num += 1
            cur_task_tags = self.tags_str_arr[self.current_task_num - 1]
            extra_task_num = self.current_task_num - self.orig_tasks_count
            extra_task_str = f'[extra {extra_task_num:d}] ' if extra_task_num > 0 else ''
            trace(f'\n{extra_task_str}task {self.current_task_num:d} / {self._tasks_count():d} in progress...\n{cur_task_tags}\n')
            try:
                self._process_tags(cur_task_tags)
            except ThreadInterruptException:
                trace(f'task {self.current_task_num:d} aborted...')
                raise
            except Exception:
                trace(f'task {self.current_task_num:d} failed...')
                raise
        try:
            self._download_all()
        except ThreadInterruptException:
            trace('download aborted...')
            raise
        except Exception:
            trace('download failed...')
            raise
        self._dump_all_info()
        total_files = min(self.success_count + self.fail_count, self.total_count_all)
        success_files = min(self.success_count, self.total_count_all - self.fail_count)
        trace(f'\n{self._tasks_count():d} task(s) completed, {success_files:d} / {total_files:d} item(s) succeded', False, True)
        if len(self.failed_items) > 0:
            trace(f'{len(self.failed_items):d} failed item(s):')
            trace('\n'.join(self.failed_items))

    def _check_tags(self) -> None:
        if self._tasks_count() != 1:
            trace('Cannot check tags: more than 1 task was formed')
            raise ThreadInterruptException
        cur_tags = self._consume_custom_module_tags(self.tags_str_arr[0])
        self.url = self._form_tags_search_address(cur_tags)
        total_count_or_html = self._get_items_query_size_or_html(self.url, tries=1)
        self.total_count = total_count_or_html if isinstance(total_count_or_html, int) else 1

    def _get_max_id(self) -> None:
        self.include_parchi = False
        self.url = self._form_tags_search_address('', 1)
        count_or_html = self._get_items_query_size_or_html(self.url)
        if isinstance(count_or_html, int):
            self.total_count = count_or_html
            self._get_page_items(0, 1, self.maxpage)
            self.items_raw_per_task = self.items_raw_per_page.get(0)[:1]
        else:
            self.total_count = 1
            self.items_raw_per_task = [self._form_item_string_manually(count_or_html)]
        trace(f'{self._get_module_abbr().upper()}: {self._extract_id(self.items_raw_per_task[0])}')

    @abstractmethod
    def _form_tags_search_address(self, tags: str, maxlim: int = None) -> str:
        ...

    def _launch(self, args: Namespace, thiscall: Callable[[], None], enable_preprocessing=True) -> None:
        self.current_state = DownloaderStates.LAUNCHING
        self.reset_root_thread(current_process())
        self._start_exception_checker()
        try:
            self._parse_args(args, enable_preprocessing)
            self._at_launch()
            thiscall()
        except (KeyboardInterrupt, ThreadInterruptException):
            trace(f'\nInterrupted by \'{sys.exc_info()[0].__name__}\'!\n', True)
        except Exception:
            import traceback
            trace(f'Unhandled exception: {str(sys.exc_info()[0])}!\n{traceback.format_exc()}', True)
        finally:
            self.current_state = DownloaderStates.IDLE
        if self._thread_exceptions and self.maxthreads_items > 1:
            n = '\n'
            trace(f'Catched thread exception(s):\n{n.join(n.join(self._thread_exceptions[exck]) for exck in self._thread_exceptions)}')

    def launch_download(self, args: Namespace) -> None:
        """Public, needed by core"""
        self._launch(args, self._process_all_tags)

    def launch_check_tags(self, args: Namespace) -> None:
        """Public, needed by core"""
        self.check_tags = True
        self._launch(args, self._check_tags, False)

    def launch_get_max_id(self, args: Namespace) -> None:
        """Public, needed by core"""
        self.get_max_id = True
        self._launch(args, self._get_max_id, False)

    def _parse_args(self, args: Namespace, enable_preprocessing=True) -> None:
        assert hasattr(args, 'tags') and type(args.tags) is list
        ThreadedHtmlWorker._parse_args(self, args)
        self.add_filename_prefix = args.prefix or self.add_filename_prefix
        self.dump_tags = args.dump_tags or self.dump_tags
        self.dump_sources = args.dump_sources or self.dump_sources
        self.dump_comments = args.dump_comments or self.dump_comments
        self.dump_per_item = args.dump_per_item or self.dump_per_item
        self.merge_lists = args.merge_lists or self.merge_lists
        self.append_info = args.append_info or self.append_info
        self.download_mode = args.dmode or self.download_mode
        self.download_limit = args.dlimit or self.download_limit
        self.reverse_download_order = args.reverse or self.reverse_download_order
        self.maxthreads_items = args.threads or self.maxthreads_items
        self.include_parchi = args.include_parchi or self.include_parchi
        self.skip_images = args.skip_img or self.skip_images
        self.skip_videos = args.skip_vid or self.skip_videos
        self.prefer_webm = args.webm or self.prefer_webm
        self.prefer_mp4 = args.mp4 or self.prefer_mp4
        self.low_res = args.lowres or self.low_res
        self.date_min = args.mindate or self.date_min
        self.date_max = args.maxdate or self.date_max
        self.dest_base = normalize_path(args.path) if args.path else self.dest_base
        self.warn_nonempty = args.warn_nonempty or self.warn_nonempty
        self.tags_str_arr[0:] = [] if self.get_max_id else convert_taglist(args.tags)
        self._extract_negative_and_groups()
        self._extract_custom_argument_tags()
        if enable_preprocessing:
            self._try_preprocess_favorites()
            self._try_preprocess_pool()
        self._parse_tags()
        if self._solve_argument_conflicts():
            thread_sleep(2.0)

    def _solve_argument_conflicts(self) -> bool:
        ret = False
        if not ProcModule.is_rs():
            if self.prefer_webm:
                trace(f'Warning (W1): \'-webm\' option is not available for \'{ProcModule.name().upper()}\' module. Ignored!')
                ret = True
            if self.prefer_mp4:
                trace(f'Warning (W1): \'-mp4\' option is not available for \'{ProcModule.name().upper()}\' module. Ignored!')
                ret = True
        if not ProcModule.is_rx() and not ProcModule.is_en():
            if self.include_parchi:
                trace('Warning (W1): only RX and EN modules are able to collect parent posts. Disabled!')
                self.include_parchi = False
                ret = True
        if ProcModule.is_rs():
            if self.dump_sources:
                trace('Warning (W1): RS module is unable to collect sources. Disabled!')
                self.dump_sources = False
                ret = True
            if self.date_min != DATE_MIN_DEFAULT or self.date_max != DATE_MAX_DEFAULT:
                trace('Warning (W1): RS module is unable to filter by date. Disabled!')
                self.date_min, self.date_max = DATE_MIN_DEFAULT, DATE_MAX_DEFAULT
                ret = True
        if ProcModule.is_rz():
            if self.dump_comments:
                trace('Warning (W1): RZ module is unable to collect comments. Disabled!')
                self.dump_comments = False
                ret = True
        if ProcModule.is_en():
            if self.dump_comments and self.maxthreads_items > 2 and not self.check_tags and not self.get_max_id:
                trace('Warning (W1): EN module can\'t fetch comments faster than 2/sec due to API limitation. Forcing 2 download threads!')
                self.maxthreads_items = 2
                ret = True
        return ret

    def _extract_cur_task_infos(self, parents: MutableSet[str]) -> None:
        def put_info(item_info: ItemInfo) -> None:
            if self.include_parchi is True:
                if item_info.has_children == 'true':
                    self._register_parent_post(parents, item_info.id)
                if item_info.parent_id.isnumeric():
                    self._register_parent_post(parents, item_info.parent_id)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_info.id}'
            self.item_info_dict_per_task[idstring] = item_info
            if len(item_info.source) < 2:
                item_info.source = SOURCE_DEFAULT
            if __RUXX_DEBUG__ and not self.favorites_search_user and not self.pool_search_str:
                for key in item_info.__slots__:
                    if key in ItemInfo.optional_slots:
                        continue
                    if getattr(item_info, key) == '':
                        trace(f'Info: extract info {abbrp}{item_info.id}: uninitialized field \'{key}\'!')

        abbrp = self._get_module_abbr_p()
        if self._can_extract_item_info_without_fetch() or self.maxthreads_items < 2 or len(self.items_raw_per_task) < 2:
            for item in self.items_raw_per_task:
                self.catch_cancel_or_ctrl_c()
                res = self._extract_item_info(item)
                put_info(res)
        else:  # RS
            active_pool: ThreadPool
            with Pool(self.maxthreads_items) as active_pool:
                ress = list()
                for larr in [(elem,) for elem in self.items_raw_per_task]:
                    ress.append(active_pool.apply_async(self._extract_item_info, args=larr))
                active_pool.close()
                while len(ress) > 0:
                    self.catch_cancel_or_ctrl_c()
                    while len(ress) > 0 and ress[0].ready():
                        res = ress.pop(0).get()
                        put_info(res)
                    thread_sleep(0.2)

    def _dump_all_info(self) -> None:
        if len(self.item_info_dict_all) == 0 or True not in (self.dump_tags, self.dump_sources, self.dump_comments):
            return

        if not path.isdir(self.dest_base):
            try:
                makedirs(self.dest_base)
            except Exception:
                thread_exit(f'ERROR: Unable to create folder {self.dest_base}!')

        orig_ids: set[str] = {self.item_info_dict_all[k].id for k in self.item_info_dict_all}
        merged_files = self._try_merge_info_files()
        saved_files = list()
        item_info_list = sorted(self.item_info_dict_all.values())
        id_begin = item_info_list[0].id
        id_end = item_info_list[-1].id
        abbrp = self._get_module_abbr_p()

        def proc_tags(item_info: ItemInfo) -> str:
            if iteminfo.id not in orig_ids and not iteminfo.tags:
                return ''
            return f'{abbrp}{item_info.id}: {format_score(item_info.score)} {item_info.tags.strip()}\n'

        def proc_sources(item_info: ItemInfo) -> str:
            if iteminfo.id not in orig_ids and not iteminfo.source:
                return ''
            return f'{abbrp}{item_info.id}: {item_info.source.strip()}\n'

        def proc_comments(item_info: ItemInfo) -> str:
            if iteminfo.id not in orig_ids and not iteminfo.comments:
                return ''
            comments = f'\n{NEWLINE_X2.join(str(c) for c in item_info.comments)}\n' if item_info.comments else ''
            return f'{abbrp}{item_info.id}:{comments}\n'

        name: str
        proc: Callable[[ItemInfo], str]
        conf: bool
        for name, proc, conf in (
            ('tags', proc_tags, self.dump_tags),
            ('sources', proc_sources, self.dump_sources),
            ('comments', proc_comments, self.dump_comments)
        ):
            if conf is False:
                continue
            trace(f'\nSaving {name}...')
            if self.dump_per_item:
                for iinfo in item_info_list:
                    ifilename = f'{self.dest_base}{abbrp}!{name}{UNDERSCORE}{iinfo.id}.txt'
                    saved_files.append(ifilename)
                    if self._has_gui() and path.isfile(ifilename):
                        if not confirm_yes_no(title=f'Save {name}', msg=f'File \'{ifilename}\' already exists. Overwrite?'):
                            trace('Skipped.')
                            continue
                    with open(ifilename, 'wt', encoding=UTF8) as idump:
                        idump.write(proc(iinfo))
            else:
                filename = f'{self.dest_base}{abbrp}!{name}{UNDERSCORE}{id_begin}-{id_end}.txt'
                saved_files.append(filename)
                if self._has_gui() and path.isfile(filename):
                    if not confirm_yes_no(title=f'Save {name}', msg=f'File \'{filename}\' already exists. Overwrite?'):
                        trace('Skipped.')
                        continue
                with open(filename, 'wt', encoding=UTF8) as dump:
                    for iteminfo in item_info_list:
                        dump_string = proc(iteminfo)
                        if dump_string or (iteminfo.id in orig_ids):
                            dump.write(dump_string)
            trace('Done.')
        [remove(merged_file) for merged_file in merged_files if merged_file not in saved_files]
        trace(BR)

    def _try_merge_info_files(self) -> list[str]:
        parsed_files = list()
        if not self.merge_lists:
            return parsed_files
        dir_fullpath = normalize_path(f'{self.dest_base}')
        if not path.isdir(dir_fullpath):
            return parsed_files
        abbrp = self._get_module_abbr_p()
        info_lists: list[Match[str]] = sorted(filter(
            lambda x: not not x, [re_infolist_filename.fullmatch(f) for f in listdir(dir_fullpath)
                                  if path.isfile(f'{dir_fullpath}{f}') and f.startswith(f'{abbrp}!')]
        ), key=lambda m: m.string)
        if not info_lists:
            return parsed_files
        parsed_dict: dict[str, ItemInfo] = dict()
        for fmatch in info_lists:
            fmname = fmatch.string
            list_type = fmatch.group(1)
            list_fullpath = f'{dir_fullpath}{fmname}'
            try:
                with open(list_fullpath, 'rt') as listfile:
                    last_idstring = ''
                    lines = listfile.readlines()
                    for i, line in enumerate(lines):
                        line = line.strip('\ufeff')
                        if line in ('', '\n'):
                            continue
                        if line.startswith(abbrp):
                            delim_idx = line.find(':')
                            idi = line[len(abbrp):delim_idx]
                            last_id = int(idi)
                            last_idstring = f'{(abbrp if self.add_filename_prefix else "")}{last_id:d}'
                            if last_idstring not in parsed_dict:
                                ii = ItemInfo()
                                ii.id = idi
                                parsed_dict[last_idstring] = ii
                            ii = parsed_dict[last_idstring]
                            if len(line) > delim_idx + 2:
                                if list_type == 'tags':
                                    tags_idx = line.find(' ', delim_idx + 2) + 1
                                    score_str = line[delim_idx + 2:tags_idx - 1][1:-1]
                                    tags_str = line[tags_idx:]
                                    ii.score = score_str
                                    ii.tags = tags_str.strip()
                                else:
                                    source_str = line[delim_idx + 2:]
                                    ii.source = source_str.strip()
                                last_idstring = ''
                        else:
                            assert last_idstring
                            lii = parsed_dict[last_idstring]
                            new_comment = line.strip().endswith(':') and (lines[i - 1].startswith(abbrp) or lines[i - 1] in ('', '\n'))
                            if not lii.comments or new_comment:
                                lii.comments.append(Comment('', ''))
                            comment = lii.comments[-1]
                            if new_comment:
                                comment_author = line.strip()[:-1]
                                comment.author = comment_author
                            else:
                                comment.body += line
                    parsed_files.append(list_fullpath)
            except Exception:
                trace(f'Error reading from {fmname}. Skipped')
                continue
        for k in parsed_dict:
            if k not in self.item_info_dict_all:
                self.item_info_dict_all[k] = parsed_dict[k]
        return parsed_files

    def _has_gui(self) -> bool:
        return hasattr(self.my_root_thread, 'gui')

#
#
#########################################
