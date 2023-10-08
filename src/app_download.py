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
from datetime import datetime
from multiprocessing.dummy import current_process, Pool
from multiprocessing.pool import ThreadPool
from os import makedirs, listdir, path, curdir
from re import compile as re_compile
from time import sleep as thread_sleep
from typing import Optional, Dict, Tuple, Union, List, Callable, Pattern, Iterable, Set, MutableSet

# requirements
from bs4 import BeautifulSoup
from iteration_utilities import unique_everseen

# internal
from app_defines import (
    ThreadInterruptException, DownloaderStates, DownloadModes, PageCheck, ItemInfo, Mem, DATE_MIN_DEFAULT, FMT_DATE, CONNECT_TIMEOUT_BASE,
    DEFAULT_ENCODING, SOURCE_DEFAULT, PLATFORM_WINDOWS,
)
from app_gui_defines import UNDERSCORE, NEWLINE, NEWLINE_X2
from app_module import ProcModule
from app_network import ThreadedHtmlWorker, thread_exit, DownloadInterruptException
from app_logger import trace
from app_revision import __RUXX_DEBUG__, APP_NAME, APP_VERSION
from app_tagger import append_filtered_tags
from app_task import extract_neg_and_groups, split_tags_into_tasks
from app_utils import as_date, confirm_yes_no, normalize_path, trim_undersores, format_score

__all__ = ('DownloaderBase',)


LINE_BREAKS_AT = 99 if sys.platform == PLATFORM_WINDOWS else 90
BR = "=" * LINE_BREAKS_AT
"""line breaker"""


class DownloaderBase(ThreadedHtmlWorker):
    """
    DownloaderBase !Abstract!
    """
    @abstractmethod
    def ___this_class_has_virtual_methods___(self) -> ...:
        ...

    def __init__(self) -> None:
        super().__init__()

        # config
        self.add_filename_prefix = False
        self.dump_tags = False
        self.dump_sources = False
        self.dump_comments = False
        self.append_info = False
        self.download_mode = DownloadModes.DOWNLOAD_FULL
        self.download_limit = 0
        self.maxthreads_items = 1
        self.include_parchi = False
        self.skip_images = False
        self.skip_videos = False
        self.prefer_webm = False
        self.low_res = False
        self.date_min = DATE_MIN_DEFAULT
        self.date_max = datetime.today().strftime(FMT_DATE)
        self.dest_base = normalize_path(path.abspath(curdir))
        self.warn_nonempty = False
        self.tags_str_arr = list()  # type: List[str]
        # extra
        self.cmdline = list()  # type: List[str]
        self.get_max_id = False

        # results
        self.url = ''
        self.minpage = 0
        self.maxpage = 0
        self.success_count = 0
        self.fail_count = 0
        self.failed_items = list()  # type: List[str]
        self.total_count = 0
        self.total_count_old = 0
        self.total_count_all = 0
        self.processed_count = 0
        self.total_pages = 0
        self.current_task_num = 0
        self.orig_tasks_count = 0
        self.current_state = DownloaderStates.STATE_IDLE
        self.items_raw_per_task = list()  # type: List[str]
        self.items_raw_per_page = dict()  # type: Dict[int, List[str]]
        self.items_raw_all = list()  # type: List[str]
        self.item_info_dict_per_task = dict()  # type: Dict[str, ItemInfo]
        self.item_info_dict_all = dict()  # type: Dict[str, ItemInfo]
        self.neg_and_groups = list()  # type: List[List[Pattern[str]]]
        self.known_parents = set()  # type: Set[str]
        # extra
        self._max_id = 0

    def __del__(self) -> None:
        self.__cleanup()

    def __enter__(self) -> DownloaderBase:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__cleanup()

    def __cleanup(self) -> None:
        # self.current_state = DownloaderStates.STATE_IDLE
        self.raw_html_cache.clear()
        if self.session:
            self.session.close()
            self.session = None

    # threaded
    def _inc_proc_count(self) -> None:
        if self.maxthreads_items > 1:
            with self.item_lock:
                self.processed_count += 1
        else:
            self.processed_count += 1

    def _num_pages(self) -> int:
        return (self.maxpage - self.minpage) + 1

    def _tasks_count(self) -> int:
        return len(self.tags_str_arr)

    @abstractmethod
    def _get_module_abbr(self) -> str:
        ...

    @abstractmethod
    def _get_module_abbr_p(self) -> str:
        ...

    @abstractmethod
    def _get_items_per_page(self) -> int:
        ...

    @abstractmethod
    def _get_max_search_depth(self) -> int:
        ...

    @abstractmethod
    def _form_item_string_manually(self, raw_html_page: BeautifulSoup) -> None:
        ...

    @abstractmethod
    def _is_search_overload_page(self, raw_html_page: BeautifulSoup) -> bool:
        ...

    @abstractmethod
    def _form_page_num_address(self, n: int) -> str:
        ...

    @abstractmethod
    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        ...

    @abstractmethod
    def _local_addr_from_string(self, h: str) -> str:
        ...

    @abstractmethod
    def _extract_id(self, h: str) -> str:
        ...

    @abstractmethod
    def _is_video(self, h: str) -> bool:
        ...

    @abstractmethod
    def _get_item_html(self, h: str) -> Union[None, BeautifulSoup, str]:
        ...

    @abstractmethod
    def _extract_post_date(self, raw_or_html: Union[BeautifulSoup, str]) -> str:
        ...

    @abstractmethod
    def get_items_query_size_or_html(self, url: str, tries: int = None) -> Union[int, BeautifulSoup]:
        """Public, needed by tagging tests"""
        ...

    @abstractmethod
    def _get_image_address(self, h: str) -> Tuple[str, str]:
        ...

    @abstractmethod
    def _get_video_address(self, h: str) -> Tuple[str, str]:
        ...

    @abstractmethod
    def _extract_item_info(self, item: str) -> ItemInfo:
        ...

    @abstractmethod
    def get_re_tags_to_process(self) -> Pattern:
        """Public, needed by tagging tools"""
        ...

    @abstractmethod
    def get_re_tags_to_exclude(self) -> Pattern:
        """Public, needed by tagging tools"""
        ...

    @abstractmethod
    def _get_tags_concat_char(self) -> str:
        ...

    @abstractmethod
    def _get_idval_equal_seaparator(self) -> str:
        ...

    @abstractmethod
    def _split_or_group_into_tasks_always(self) -> bool:
        ...

    @abstractmethod
    def _can_extract_item_info_without_fetch(self) -> bool:
        ...

    def save_cmdline(self, cmdline: List[str]):
        self.cmdline = cmdline

    def _at_launch(self) -> None:
        trace(f'Python {sys.version}\nBase args: {" ".join(sys.argv)}\nMy args: {" ".join(self.cmdline)}')

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
        if self.download_mode != DownloadModes.DOWNLOAD_SKIP:
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

        if self.download_mode == DownloadModes.DOWNLOAD_TOUCH or result.file_size > 0:
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

    def _get_page_boundary_by_date(self, minpage: bool) -> int:
        if 1 <= self._num_pages() <= 2:
            trace('Only a page or two! Skipping')
            pnum = self.minpage if minpage else self.maxpage
        elif minpage is True and as_date(self.date_max) >= datetime.today().date():
            trace('Min page: max date irrelevant! Skipping')
            pnum = self.minpage
        elif minpage is False and as_date(self.date_min) <= as_date(DATE_MIN_DEFAULT):
            trace('Max page: min date irrelevant! Skipping')
            pnum = self.maxpage
        else:
            p_chks = list()
            for i in range(self.maxpage + 3):
                p_chks.append(PageCheck())

            lim_backw = self.minpage - 1
            lim_forw = self.maxpage + 1

            dofinal = False
            cur_step = 0
            pdivider = 1
            step_dir = 1  # forward
            pnum = self.minpage

            while True:
                self.catch_cancel_or_ctrl_c()

                if dofinal is True:
                    trace(f'{"min" if minpage else "max"} page reached: {pnum + 1:d}')
                    break

                cur_step += 1
                trace(f'step {cur_step:d}')

                pdivider = min(pdivider * 2, self._num_pages())
                pnum += (self._num_pages() // pdivider) * step_dir
                trace(f'page {pnum + 1:d} (div {pdivider:d}, step {step_dir:d})')

                half_div = pdivider > self._num_pages() // 2

                if pnum < self.minpage:
                    trace('Page < minpage, returning minpage!')
                    pnum = self.minpage
                    break
                if pnum > self.maxpage:
                    trace('Page > maxpage, returning maxpage!')
                    pnum = self.maxpage
                    break

                items_per_page = self._get_items_per_page()

                prev = pnum * items_per_page
                curmax = min((pnum + 1) * items_per_page, self.total_count)
                i_count = curmax - prev

                raw_html_page = self.fetch_html(self._form_page_num_address(pnum), do_cache=True)
                if raw_html_page is None:
                    thread_exit(f'ERROR: ProcPage: unable to retreive html for page {pnum + 1:d}!', -16)

                items_raw = self._get_all_post_tags(raw_html_page)
                if len(items_raw) == 0:
                    thread_exit(f'ERROR: ProcPage: cannot find picture or video on page {pnum + 1:d}', -17)

                # check first item if moving forward and last item if backwards
                h = self._local_addr_from_string(str(items_raw[0 if step_dir == 1 else i_count - 1]))
                item_id = self._extract_id(h)

                # trace(f'checking id {item_id}')

                def forward() -> Tuple[int, int]:
                    return pnum, 1

                def backward() -> Tuple[int, int]:
                    return pnum, -1

                cur_step_dir = step_dir

                raw_html_item = self._get_item_html(h)
                if raw_html_item is None:
                    thread_exit(f'ERROR: TagProc: unable to retreive html for {item_id}! Stopping search', -18)

                if minpage is True:
                    if as_date(self._extract_post_date(raw_html_item)) > as_date(self.date_max):
                        if half_div and (p_chks[lim_forw + 1].first or p_chks[pnum + 1].last):
                            dofinal = True
                        else:
                            trace(f'Info: TagProc: > maxdate at {item_id} - stepping forward...')
                            lim_backw, step_dir = forward()
                    else:
                        if half_div and (p_chks[lim_backw + 1].last or p_chks[pnum + 1].first):
                            dofinal = True
                        else:
                            trace(f'Info: TagProc: <= maxdate at {item_id} - stepping backwards...')
                            lim_forw, step_dir = backward()
                else:
                    if as_date(self._extract_post_date(raw_html_item)) < as_date(self.date_min):
                        if half_div and (p_chks[lim_backw + 1].last or p_chks[pnum + 1].first):
                            dofinal = True
                        else:
                            trace(f'Info: TagProc: < mindate at {item_id} - stepping backwards...')
                            lim_forw, step_dir = backward()
                    else:
                        if half_div and (p_chks[lim_forw + 1].first or p_chks[pnum + 1].last):
                            dofinal = True
                        else:
                            trace(f'Info: TagProc: >= mindate at {item_id} - stepping forward...')
                            lim_backw, step_dir = forward()

                if cur_step_dir == 1:
                    p_chks[pnum + 1].first = True
                else:
                    p_chks[pnum + 1].last = True

        return pnum

    # threaded
    def _get_page_items(self, n: int, c_page: int, page_max: int) -> None:
        items_per_page = self._get_items_per_page()
        pnum = n + 1
        prev_c = (c_page - 1) * items_per_page
        curmax_c = min(c_page * items_per_page, self.total_count_old)

        if not self.get_max_id:
            trace(f'page: {pnum:d} / {page_max + 1:d}\t({prev_c + 1:d}-{curmax_c:d} / {self.total_count_old:d})', True)

        while True:
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

    def _filter_last_items(self) -> None:
        # Filter out all trailing items if needed (last page)
        trace('Filtering trailing back items...')

        if as_date(self.date_min) <= as_date(DATE_MIN_DEFAULT):
            trace('last items filter is irrelevant! Skipping')
            return

        if len(self.items_raw_per_task) < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'mindate at {self.date_min}, filtering')
        items_tofilter = self.items_raw_per_task[-(min(len(self.items_raw_per_task), self._get_items_per_page() * 2)):]
        self.items_raw_per_task = self.items_raw_per_task[:-len(items_tofilter)]  # type: List[str]
        trace(f'Items to potentially remove: {len(items_tofilter):d}')

        divider = 1
        dofinal = False
        cur_index = 0
        step_direction = 1
        cur_step = 0
        f_total = len(items_tofilter)
        forward_lim = f_total
        backward_lim = -1
        while True and f_total > 0:  # while True
            cur_step += 1
            trace(f'step {cur_step:d}')

            self.catch_cancel_or_ctrl_c()

            divider = min(divider * 2, f_total)
            cur_index += (f_total // divider) * step_direction
            trace(f'index {cur_index:d} (div {divider:d}, step {step_direction:d})')

            if cur_index < backward_lim:
                trace('Error: cur_index < backward_lim, aborting filter!')
                self.items_raw_per_task += items_tofilter
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
                self.items_raw_per_task += items_tofilter
                break

            # last steps
            if cur_index == backward_lim:
                cur_index = backward_lim + 1
                trace(f'End: reached back lim at {backward_lim:d}!')
                dofinal = True
            elif cur_index == forward_lim:
                cur_index = forward_lim
                trace(f'End: reached forw lim at {forward_lim:d}!')
                dofinal = True

            if dofinal is True:
                items_tofilter = items_tofilter[:cur_index]
                trace(f'Items after filter: {len(items_tofilter):d}')
                self.items_raw_per_task += items_tofilter
                break

            h = self._local_addr_from_string(str(items_tofilter[cur_index]))
            item_id = self._extract_id(h)

            def forward() -> Tuple[int, int]:
                return cur_index, 1

            def backward() -> Tuple[int, int]:
                return cur_index, -1

            raw_html_item = self._get_item_html(h) if as_date(self.date_min) > as_date(DATE_MIN_DEFAULT) else None
            post_date = self._extract_post_date(raw_html_item) if raw_html_item is not None else None
            exceed_date = (as_date(post_date) < as_date(self.date_min)) if post_date is not None else False

            if exceed_date:
                trace(f'Info: TagProc_filter: {item_id} exceeds min date ({post_date} < {self.date_min}), shuffling backwards...')
                forward_lim, step_direction = backward()
            else:
                trace(f'Info: TagProc_filter: {item_id} does not exceed min date - stepping forward...')
                backward_lim, step_direction = forward()

    def _filter_first_items(self) -> None:
        # Filter out all trailing items if needed (front page)
        trace('Filtering trailing front items...')

        if as_date(self.date_max) >= datetime.today().date():
            trace('first items filter is irrelevant! Skipping')
            return

        if len(self.items_raw_per_task) < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'maxdate at {self.date_max}, filtering')
        items_tofilter = self.items_raw_per_task[:(min(len(self.items_raw_per_task), self._get_items_per_page() * 2))]
        self.items_raw_per_task = self.items_raw_per_task[len(items_tofilter):]  # type: List[str]

        trace(f'Items to potentially remove: {len(items_tofilter):d}')

        divider = 1
        dofinal = False
        cur_index = 0
        step_direction = 1
        cur_step = 0
        f_total = len(items_tofilter)
        forward_lim = f_total
        backward_lim = -1
        while True and f_total > 0:  # while True
            cur_step += 1
            trace(f'step {cur_step:d}')

            self.catch_cancel_or_ctrl_c()

            divider = min(divider * 2, f_total)
            cur_index += (f_total // divider) * step_direction
            trace(f'index {cur_index:d} (div {divider:d}, step {step_direction:d})')

            if cur_index < backward_lim:
                trace('Error: cur_index < backward_lim, aborting filter!')
                self.items_raw_per_task = items_tofilter + self.items_raw_per_task
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
                self.items_raw_per_task = items_tofilter + self.items_raw_per_task
                break

            # last steps
            if cur_index == backward_lim:
                cur_index = backward_lim + 1
                trace(f'End: reached back lim at {backward_lim:d}!')
                dofinal = True
            elif cur_index == forward_lim:
                cur_index = forward_lim
                trace(f'End: reached forw lim at {forward_lim:d}!')
                dofinal = True

            if dofinal is True:
                items_tofilter = items_tofilter[cur_index:]
                trace(f'Items after filter: {len(items_tofilter):d}')
                self.items_raw_per_task = items_tofilter + self.items_raw_per_task  # type: List[str]
                break

            h = self._local_addr_from_string(str(items_tofilter[cur_index]))
            item_id = self._extract_id(h)

            def forward() -> Tuple[int, int]:
                return cur_index, 1

            def backward() -> Tuple[int, int]:
                return cur_index, -1

            raw_html_item = self._get_item_html(h) if as_date(self.date_max) < datetime.today().date() else None
            post_date = self._extract_post_date(raw_html_item) if raw_html_item is not None else None
            exceed_date = (as_date(post_date) > as_date(self.date_max)) if post_date is not None else False

            if exceed_date:
                trace(f'Info: TagProc_filter: {item_id} exceeds max date ({post_date} > {self.date_max}), stepping forward...')
                backward_lim, step_direction = forward()
            else:
                trace(f'Info: TagProc_filter: {item_id} does not exceed max date - stepping backwards...')
                forward_lim, step_direction = backward()

    def _filter_items_by_type(self) -> None:
        trace('Filtering items by type...')

        if self.skip_images is False and self.skip_videos is False:
            trace('Both types are enabled! Skipping')
            return

        total_count_temp = self.total_count

        for idx in reversed(range(len(self.items_raw_per_task))):  # type: int
            self.catch_cancel_or_ctrl_c()
            h = str(self.items_raw_per_task[idx])
            is_vid = self._is_video(h)
            if self.skip_videos if is_vid else self.skip_images:
                del self.items_raw_per_task[idx]
                self.total_count -= 1

        if total_count_temp != self.total_count:
            trace(f'Filtered out {total_count_temp - self.total_count:d} / {total_count_temp:d} items!')

    def _filter_items_by_previous_tasks(self) -> None:
        trace('Filtering items by previous tasks...')

        if self.current_task_num <= 1:
            return

        total_count_temp = self.total_count

        for idx in reversed(range(len(self.items_raw_per_task))):  # type: int
            self.catch_cancel_or_ctrl_c()
            full_itemid = f'{self._get_module_abbr_p()}{self._extract_id(self.items_raw_per_task[idx])}'
            if full_itemid in self.item_info_dict_all:
                del self.items_raw_per_task[idx]
                self.total_count -= 1

        if total_count_temp != self.total_count:
            trace(f'Filtered out {total_count_temp - self.total_count:d} / {total_count_temp:d} items!')

    def _filter_existing_items(self) -> None:
        trace('Filtering out existing items...')

        if not path.isdir(self.dest_base):
            return

        total_count_temp = self.total_count

        curdirfiles = [curfile for curfile in listdir(self.dest_base) if path.isfile(f'{self.dest_base}{curfile}')]
        if len(curdirfiles) == 0:
            return

        abbrp = self._get_module_abbr_p()
        for idx in reversed(range(len(self.items_raw_per_task))):  # type: int
            self.catch_cancel_or_ctrl_c()
            h = self._local_addr_from_string(str(self.items_raw_per_task[idx]))
            item_id = self._extract_id(h)
            rex_cdfile = re_compile(fr'^(?:{abbrp})?{item_id}[._].*?$')
            for f_idx in reversed(range(len(curdirfiles))):
                if rex_cdfile.fullmatch(curdirfiles[f_idx]) is not None:
                    del curdirfiles[f_idx]
                    del self.items_raw_per_task[idx]
                    self.total_count -= 1
                    break

        if total_count_temp != self.total_count:
            trace(f'Filtered out {total_count_temp - self.total_count:d} / {total_count_temp:d} items!')

    def _filter_items_matching_negative_and_groups(self, parents: MutableSet[str]) -> None:
        trace('Filtering out items using custom filters...')

        if len(self.neg_and_groups) == 0:
            return

        abbrp = self._get_module_abbr_p()
        total_count_old = len(self.items_raw_per_task)
        removed_count = 0
        for idx in reversed(range(total_count_old)):  # type: int
            h = self._local_addr_from_string(str(self.items_raw_per_task[idx]))
            item_id = self._extract_id(h)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_id}'
            item_info = self.item_info_dict_per_task.get(idstring)
            tags_list = item_info.tags.split(' ')
            if any(all(any(p.fullmatch(tag) is not None for tag in tags_list) for p in plist) for plist in self.neg_and_groups):
                if item_id in parents:
                    parents.remove(item_id)
                if item_info.parent_id in parents:
                    parents.remove(item_info.parent_id)
                del self.item_info_dict_per_task[idstring]
                del self.items_raw_per_task[idx]
                removed_count += 1

        if removed_count > 0:
            trace(f'Filtered out {removed_count:d} / {total_count_old:d} items!')

    def _process_tags(self, tag_str: str) -> None:
        self.current_state = DownloaderStates.STATE_SEARCHING
        self.url = self.form_tags_search_address(tag_str)

        page_size = self._get_items_per_page()
        total_count_or_html = self.get_items_query_size_or_html(self.url)

        if isinstance(total_count_or_html, int):
            self.total_count = total_count_or_html
            self.minpage = 0
            self.maxpage = (self.total_count - 1) // page_size  # (self.total_count + page_size - 1) // page_size - 1

            if self.total_count <= 0:
                trace('Nothing to process: query result is empty')
                return

            trace(f'Total {self.total_count:d} items found across {self._num_pages():d} pages')

            if 0 < self._get_max_search_depth() < self.total_count:
                trace('\nFATAL: too many possible matches, won\'t be able to fetch html for all the pages!\nTry adding an ID filter.')
                return

            self.total_pages = self._num_pages()

            pageargs = ((DownloaderStates.STATE_SCANNING_PAGES1, True), (DownloaderStates.STATE_SCANNING_PAGES2, False))

            def page_filter(st: DownloaderStates, di: bool) -> int:
                self.current_state = st
                trace(f'Looking for {"min" if di else "max"} page by date...')
                return self._get_page_boundary_by_date(di)

            for fstate, direction in pageargs:  # type: DownloaderStates, bool
                if direction is True:
                    self.minpage = page_filter(fstate, direction)
                else:
                    self.maxpage = page_filter(fstate, direction)
                self.total_pages = self._num_pages()

            self.total_count = min(self._num_pages() * page_size, self.total_count)
            trace(f'new totalcount: {self.total_count:d}')
            trace(f'Scanning pages {self.minpage + 1:d} - {self.maxpage + 1:d}')

            self.total_count_old = self.total_count
            self.total_count = 0  # type: Union[int, BeautifulSoup]

            if self.maxthreads_items > 1 and self._num_pages() > 1:
                trace(f'  ...using {self.maxthreads_items:d} threads...')
                c_page = 0
                arr_temp = list()
                for n in range(self.minpage, self.maxpage + 1):
                    c_page += 1
                    arr_temp.append((n, c_page, self.maxpage))

                with Pool(max(2, self.maxthreads_items // 2)) as active_pool:  # type: ThreadPool
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
                cur_l = self.items_raw_per_page.get(k)
                assert cur_l is not None
                for i in range(len(cur_l)):
                    self.items_raw_per_task[cur_idx] = cur_l[i]
                    cur_idx += 1

            self.items_raw_per_page.clear()

            self.items_raw_per_task = list(unique_everseen(self.items_raw_per_task))  # type: List[str]
        else:
            # we have been redirected to a page with our single result! compose item string manually
            if __RUXX_DEBUG__:
                trace('Warning (W1): A single match redirect was hit, forming item string manually')

            self._form_item_string_manually(total_count_or_html)

        def after_filter(sleep_time: float) -> None:
            self.total_count = len(self.items_raw_per_task)
            trace(f'new totalcount: {self.total_count:d}')
            thread_sleep(sleep_time)

        def apply_filter(state: DownloaderStates, func: Callable[..., None], *args, sleep_time: float = 0.025) -> None:
            self.current_state = state
            func(*args)
            after_filter(sleep_time)

        after_filter(0.1)

        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS1, self._filter_last_items)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS2, self._filter_first_items)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS3, self._filter_items_by_type)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS4, self._filter_items_by_previous_tasks)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS4, self._filter_existing_items)

        # store items info for future processing
        # custom filters may exclude certain items from the infos dict
        task_parents = set()  # type: Set[str]
        self._extract_cur_task_infos(task_parents)

        if self.current_task_num <= self.orig_tasks_count:
            apply_filter(DownloaderStates.STATE_FILTERING_ITEMS4, self._filter_items_matching_negative_and_groups, task_parents)

        self.items_raw_all = list(unique_everseen(self.items_raw_all + self.items_raw_per_task))  # type: List[str]
        self.total_count_all = len(self.items_raw_all)
        self.item_info_dict_all.update(self.item_info_dict_per_task)
        if self.current_task_num > 1:
            trace(f'overall totalcount: {self.total_count_all:d}')

        if len(task_parents) > 0:
            trace(f'\nParent post(s) detected! Scheduling {len(task_parents):d} extra task(s)!')
            for parent in sorted(task_parents):
                new_task_str = f'parent{self._get_idval_equal_seaparator()}{parent}'
                trace(f' {new_task_str}')
                self.tags_str_arr.append(new_task_str)
            self.known_parents.update(task_parents)

    def _download_all(self) -> None:
        if self.total_count_all <= 0:
            trace('\nNothing to download: queue is empty')
            return

        self.items_raw_all = sorted(self.items_raw_all, key=lambda x: int(self._extract_id(x)), reverse=True)  # type: List[str]

        if self.download_limit > 0:
            if len(self.items_raw_all) > self.download_limit:
                trace(f'\nShrinking queue down to {self.download_limit:d} items...')
                self.items_raw_all = self.items_raw_all[self.download_limit * -1:]
                self.total_count_all = len(self.items_raw_all)
            else:
                trace('\nShrinking queue down is not required!')

        item_front = self._extract_item_info(self.items_raw_all[0]).id
        item_end = self._extract_item_info(self.items_raw_all[-1]).id
        # front item is always >= end item
        trace(f'\nProcessing {self.total_count_all:d} items, bound {item_end} to {item_front}')

        self.items_raw_all.reverse()
        self.current_state = DownloaderStates.STATE_DOWNLOADING
        trace(f'{self.total_count_all:d} item(s) scheduled, {self.maxthreads_items:d} thread(s) max\nWorking...\n')

        if self.maxthreads_items > 1 and len(self.items_raw_all) > 1:
            with Pool(self.maxthreads_items) as active_pool:  # type: ThreadPool
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
                self._process_item(self.items_raw_all[i])

        skip_all = self.download_mode == DownloadModes.DOWNLOAD_SKIP
        trace(f'\nAll {"skipped" if skip_all else "processed"} ({self.total_count_all:d} items)...')

    def _parse_tags(self, tags_base_arr: Iterable[str]) -> None:
        cc = self._get_tags_concat_char()
        sc = self._get_idval_equal_seaparator()
        split_always = self._split_or_group_into_tasks_always()
        # join by ' ' is required by tests, although normally len(args.tags) == 1
        tags_list, self.neg_and_groups = extract_neg_and_groups(' '.join(tags_base_arr))
        for t in tags_list:
            if len(t) > 2 and f'{t[0]}{t[-1]}' == '()' and f'{t[:2]}{t[-2:]}' != f'({cc}{cc})':
                thread_exit(f'Invalid tag \'{t}\'! Looks like \'or\' group but not fully contatenated with \'{cc}\'.')
        self.tags_str_arr = split_tags_into_tasks(tags_list, cc, sc, split_always)
        self.orig_tasks_count = self._tasks_count()

    def _process_all_tags(self) -> None:
        if self.warn_nonempty:
            if self._has_gui():
                if path.isdir(self.dest_base) and len(listdir(self.dest_base)) > 0:
                    if not confirm_yes_no(title='Download', msg=f'Destination folder \'{self.dest_base}\' is not empty. Continue anyway?'):
                        return
            else:
                trace('Warning (W1): argument \'-warn_nonempty\' is ignored in non-GUI mode')

        if self.download_mode != DownloadModes.DOWNLOAD_FULL:
            trace(f'{BR}\n\n(Emulation Mode)')
        trace(f'\n{BR}\n{APP_NAME} core ver {APP_VERSION}')
        trace(f'Starting {self._get_module_abbr()}_manual', False, True)
        trace(f'\n{len(self.neg_and_groups):d} \'excluded tags combination\' custom filter(s) parsed')
        trace(f'{self._tasks_count():d} task(s) scheduled:\n{NEWLINE.join(self.tags_str_arr)}\n\n{BR}')
        self.current_task_num = 0
        while self.current_task_num < self._tasks_count():  # tasks count may increase during this loop
            self.current_task_num += 1
            cur_task_tags = self.tags_str_arr[self.current_task_num - 1]
            extra_task_num = self.current_task_num - self.orig_tasks_count
            is_extra = extra_task_num > 0
            trace(f'\n{f"[extra {extra_task_num:d}] " if is_extra else ""}task {self.current_task_num:d} in progress...\n{cur_task_tags}\n')
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
            trace(f'{len(self.failed_items):d} failed items:')
            trace('\n'.join(self.failed_items))

    def _check_tags(self) -> None:
        if self._tasks_count() != 1:
            raise ThreadInterruptException('Cannot check tags: more than 1 task was formed')
        cur_tags = self.tags_str_arr[0]
        self.url = self.form_tags_search_address(cur_tags)
        total_count_or_html = self.get_items_query_size_or_html(self.url, tries=1)
        self.total_count = total_count_or_html if isinstance(total_count_or_html, int) else 1

    def _get_max_id(self) -> None:
        self.get_max_id = True
        self.include_parchi = False
        self.url = self.form_tags_search_address('', 1)
        count_or_html = self.get_items_query_size_or_html(self.url)
        if isinstance(count_or_html, int):
            self.total_count = count_or_html
            self._get_page_items(0, 1, self.maxpage)
            self.items_raw_per_task = self.items_raw_per_page.get(0)[:1]
        else:
            self.total_count = 1
            self._form_item_string_manually(count_or_html)
        self._max_id = self._extract_id(self.items_raw_per_task[0])
        trace(f'{self._get_module_abbr().upper()}: {self._max_id}')

    @abstractmethod
    def form_tags_search_address(self, tags: str, maxlim: Optional[int] = None) -> str:
        """Public, needed by tests"""
        ...

    def _launch(self, args: Namespace, thiscall: Callable[[], None]) -> None:
        self._at_launch()
        self.reset_root_thread(current_process())
        try:
            self.parse_args(args)
            thiscall()
        except (KeyboardInterrupt, ThreadInterruptException):
            trace(f'\nInterrupted by {str(sys.exc_info()[0])}!\n', True)
            self.my_root_thread.killed = True
        except Exception:
            import traceback
            trace(f'Unhandled exception: {str(sys.exc_info()[0])}!\n{traceback.format_exc()}', True)
        finally:
            self.current_state = DownloaderStates.STATE_IDLE

    def launch_download(self, args: Namespace) -> None:
        """Public, needed by core"""
        self._launch(args, self._process_all_tags)

    def launch_check_tags(self, args: Namespace) -> None:
        """Public, needed by core"""
        self._launch(args, self._check_tags)

    def launch_get_max_id(self, args: Namespace) -> None:
        """Public, needed by core"""
        self._launch(args, self._get_max_id)

    def parse_args(self, args: Namespace) -> None:
        """Public, needed by tests"""
        assert hasattr(args, 'tags') and type(args.tags) == list
        ThreadedHtmlWorker.parse_args(self, args)
        self.add_filename_prefix = args.prefix or self.add_filename_prefix
        self.dump_tags = args.dump_tags or self.dump_tags
        self.dump_sources = args.dump_sources or self.dump_sources
        self.dump_comments = args.dump_comments or self.dump_comments
        self.append_info = args.append_info or self.append_info
        self.download_mode = args.dmode or self.download_mode
        self.download_limit = args.dlimit or self.download_limit
        self.maxthreads_items = args.threads or self.maxthreads_items
        self.include_parchi = args.include_parchi or self.include_parchi
        self.skip_images = args.skip_img or self.skip_images
        self.skip_videos = args.skip_vid or self.skip_videos
        self.prefer_webm = args.webm or self.prefer_webm
        self.low_res = args.lowres or self.low_res
        self.date_min = args.mindate or self.date_min
        self.date_max = args.maxdate or self.date_max
        self.dest_base = normalize_path(args.path) if args.path else self.dest_base
        self.warn_nonempty = args.warn_nonempty or self.warn_nonempty
        self._parse_tags(args.tags)
        if self._solve_argument_conflicts():
            thread_sleep(2.0)

    def _solve_argument_conflicts(self) -> bool:
        ret = False
        if self.prefer_webm:
            trace('Warning (W1): \'-webm\' option is deprecated and will be removed in near future')
            ret = True
        if ProcModule.is_rn() or ProcModule.is_rs():
            if self.include_parchi:
                trace('Warning (W1): RN module is unable to collect parent posts. Disabled!')
                self.include_parchi = False
                ret = True
        if ProcModule.is_rs():
            if self.dump_sources:
                trace('Warning (W1): RS module is unable to collect sources. Disabled!')
                self.dump_sources = False
                ret = True
            if self.date_min != DATE_MIN_DEFAULT or self.date_max != datetime.today().strftime(FMT_DATE):
                trace('Warning (W1): RS module is unable to filter by date. Disabled')
                self.date_min, self.date_max = DATE_MIN_DEFAULT, datetime.today().strftime(FMT_DATE)
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
            if __RUXX_DEBUG__:
                for key in item_info.__slots__:
                    if key in ItemInfo.optional_slots:
                        continue
                    if item_info.__getattribute__(key) == '':
                        trace(f'Info: extract info {abbrp}{item_info.id}: uninitialized field \'{key}\'!')

        abbrp = self._get_module_abbr_p()
        if self._can_extract_item_info_without_fetch() or self.maxthreads_items < 2 or len(self.items_raw_per_task) < 2:
            for item in self.items_raw_per_task:
                self.catch_cancel_or_ctrl_c()
                res = self._extract_item_info(item)
                put_info(res)
        else:  # RS
            with Pool(self.maxthreads_items) as active_pool:  # type: ThreadPool
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

        self.item_info_dict_all = {
            k: v for k, v in sorted(sorted(self.item_info_dict_all.items(), key=lambda item: item[0]), key=lambda item: int(item[1].id))
        }  # type: Dict[str, ItemInfo]
        item_info_list = sorted(list(self.item_info_dict_all.values()), key=lambda x: x.id)  # type: List[ItemInfo]
        id_begin = item_info_list[0].id
        id_end = item_info_list[-1].id
        abbrp = self._get_module_abbr_p()

        def proc_tags(item_info: ItemInfo) -> str:
            return f'{abbrp}{item_info.id}: {format_score(item_info.score)} {item_info.tags.strip()}\n'

        def proc_sources(item_info: ItemInfo) -> str:
            return f'{abbrp}{item_info.id}: {item_info.source.strip()}\n'

        def proc_comments(item_info: ItemInfo) -> str:
            comments = f'\n{NEWLINE_X2.join(str(c) for c in item_info.comments)}\n' if item_info.comments else ''
            return f'{abbrp}{item_info.id}:{comments}\n'

        for name, proc, conf in (
            ('tags', proc_tags, self.dump_tags),
            ('sources', proc_sources, self.dump_sources),
            ('comments', proc_comments, self.dump_comments)
        ):  # type: str, Callable[[ItemInfo], str], bool
            if conf is False:
                continue
            trace(f'\nSaving {name}...')
            filename = f'{self.dest_base}{abbrp}!{name}{UNDERSCORE}{id_begin}-{id_end}.txt'
            if self._has_gui() and path.isfile(filename):
                if not confirm_yes_no(title=f'Save {name}', msg=f'File \'{filename}\' already exists. Overwrite?'):
                    trace('Skipped.')
                    continue
            with open(filename, 'wt', encoding=DEFAULT_ENCODING) as dump:
                for iteminfo in item_info_list:
                    dump.write(proc(iteminfo))
            trace('Done.')
        trace(BR)

    def _has_gui(self) -> bool:
        return hasattr(self.my_root_thread, 'gui')

#
#
#########################################
