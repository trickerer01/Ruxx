# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
from abc import abstractmethod
from argparse import Namespace
from datetime import datetime
from multiprocessing.dummy import current_process, Pool
from multiprocessing.pool import ThreadPool
from os import makedirs, listdir, path, curdir
from re import fullmatch as re_fullmatch, compile as re_compile
from sys import exc_info
from time import sleep as thread_sleep
from typing import Optional, Dict, Tuple, Union, List, Callable, Pattern, Iterable

# requirements
from bs4 import BeautifulSoup
from iteration_utilities import unique_everseen

# internal
from app_defines import (
    ThreadInterruptException, DownloaderStates, DownloadModes, PageCheck, PageFilterType, ItemInfo, DATE_MIN_DEFAULT,
    CONNECT_DELAY_PAGE, CONNECT_RETRIES_ITEM, LINE_BREAKS_AT, DEFAULT_ENCODING, SOURCE_DEFAULT, FMT_DATE_DEFAULT,
)
from app_gui_defines import UNDERSCORE, NEWLINE
from app_network import ThreadedHtmlWorker, thread_exit, DownloadInterruptException
from app_logger import trace
from app_revision import __RUXX_DEBUG__, APP_NAME, APP_VERSION
from app_tagger import append_filtered_tags
from app_task import extract_neg_and_groups, split_tags_into_tasks
from app_utils import as_date, confirm_yes_no, normalize_path, trim_undersores, format_score


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
        self.reverse_order = False
        self.dump_tags = False
        self.dump_source = False
        self.append_info = False
        self.download_mode = DownloadModes.DOWNLOAD_FULL
        self.download_limit = 0
        self.lower_bound = 0
        self.upper_bound = 0
        self.maxthreads_items = 1
        self.skip_images = False
        self.skip_videos = False
        self.prefer_webm = False
        self.low_res = False
        self.date_min = DATE_MIN_DEFAULT
        self.date_max = datetime.today().strftime(FMT_DATE_DEFAULT)
        self.dest_base = normalize_path(path.abspath(curdir))
        self.warn_nonempty = False
        self.tags_str_arr = []  # type: List[str]

        # results
        self.url = ''
        self.minpage = 0
        self.maxpage = 0
        self.success_count = 0
        self.fail_count = 0
        self.failed_items = []  # type: List[str]
        self.total_count = 0  # type: Union[int, BeautifulSoup]
        self.total_count_old = 0
        self.processed_count = 0
        self.total_pages = 0
        self.current_state = DownloaderStates.STATE_IDLE
        self.items_raw_all = []  # type: List[Optional[str]]
        self.items_raw_all_dict = {}  # type: Dict[int, List[str]]
        self.item_info_dict = {}  # type: Dict[str, ItemInfo]
        self.neg_and_groups = []  # type: List[List[Pattern[str]]]
        # resilts_all
        self.total_count_all = 0
        self.success_count_all = 0
        self.fail_count_all = 0

    def __del__(self) -> None:
        self.__cleanup()

    def __enter__(self) -> DownloaderBase:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__cleanup()

    def __cleanup(self) -> None:
        # self.current_state = DownloaderStates.STATE_IDLE
        self.raw_html_cache.clear()
        if self.active_pool:
            self.active_pool.terminate()
            self.active_pool = None  # type: Optional[ThreadPool]
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
    def _form_item_string_manually(self) -> None:
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
    def _extract_id(self, h) -> str:
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
    def get_items_query_size(self, url: str, tries: Optional[int] = None) -> Union[int, BeautifulSoup]:
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
        ...

    @abstractmethod
    def get_re_tags_to_exclude(self) -> Pattern:
        ...

    @abstractmethod
    def _get_tags_concat_char(self) -> str:
        ...

    @abstractmethod
    def _can_have_or_groups(self) -> bool:
        ...

    @abstractmethod
    def _get_idval_equal_seaparator(self) -> str:
        ...

    @abstractmethod
    def _split_or_group_into_tasks_always(self) -> bool:
        ...

    def get_tags_count(self, offset=0) -> int:
        return len(self.tags_str_arr[offset].split(self._get_tags_concat_char()))

    def _try_append_extra_info(self, item_abbrname: str, maxlen: int) -> str:
        if not self.append_info:
            return item_abbrname

        if maxlen <= 0:
            return item_abbrname

        info = self.item_info_dict.get(item_abbrname)
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
            result.result_str = f'{result.result_str}done ({result.file_size / (1024.0 * 1024.0):.2f} Mb)'
            with self.item_lock:
                self.success_count += 1
        else:
            result.result_str = f'{result.result_str}failed'
            if result.retries >= CONNECT_RETRIES_ITEM:
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

    def _get_page_boundary(self, minpage: bool, mode: PageFilterType) -> int:
        if 1 <= self._num_pages() <= 2:
            trace('Only a page or two! Skipping')
            pnum = self.minpage if minpage else self.maxpage
        elif mode == PageFilterType.MODE_DATE and minpage is True and as_date(self.date_max) >= datetime.today().date():
            trace('Min page: max date irrelevant! Skipping')
            pnum = self.minpage
        elif mode == PageFilterType.MODE_DATE and minpage is False and as_date(self.date_min) <= as_date(DATE_MIN_DEFAULT):
            trace('Max page: min date irrelevant! Skipping')
            pnum = self.maxpage
        elif mode == PageFilterType.MODE_ID and self.has_gui():  # handled in prepare_cmdline
            trace('Id filter is already handled! Skipping')
            pnum = self.minpage if minpage is True else self.maxpage
        elif mode == PageFilterType.MODE_ID and minpage is True and self.upper_bound == 0:
            trace('Min page: no Id limit! Skipping')
            pnum = self.minpage
        elif mode == PageFilterType.MODE_ID and minpage is False and self.lower_bound == 0:
            trace('Max page: no Id limit! Skipping')
            pnum = self.maxpage
        else:
            # p_chks = [None] * (self.maxpage + 2)
            # for i in range(self.maxpage + 2):
            #     p_chks[i] = PageCheck()

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

                if mode == PageFilterType.MODE_ID:
                    if minpage is True:
                        assert self.upper_bound > 0
                        if 0 < self.upper_bound < int(item_id):
                            if half_div and (p_chks[lim_forw + 1].first or p_chks[pnum + 1].last):
                                dofinal = True
                            else:
                                trace(f'Info: TagProc: id > upper bound at {item_id} - stepping forward...')
                                lim_backw, step_dir = forward()
                        else:
                            if half_div and (p_chks[lim_backw + 1].last or p_chks[pnum + 1].first):
                                dofinal = True
                            else:
                                trace(f'Info: TagProc: id <= upper bound at {item_id} - stepping backwards...')
                                lim_forw, step_dir = backward()
                    else:
                        assert self.lower_bound > 0
                        if 0 < int(item_id) < self.lower_bound:
                            if half_div and (p_chks[lim_backw + 1].last or p_chks[pnum + 1].first):
                                dofinal = True
                            else:
                                trace(f'Info: TagProc: id < lower bound at {item_id} - stepping backwards...')
                                lim_forw, step_dir = backward()
                        else:
                            if half_div and (p_chks[lim_forw + 1].first or p_chks[pnum + 1].last):
                                dofinal = True
                            else:
                                trace(f'Info: TagProc: id >= lower bound at {item_id} - stepping forward...')
                                lim_backw, step_dir = forward()

                elif mode == PageFilterType.MODE_DATE:
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
                else:
                    assert False

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
                items_raw_temp = []
                thread_sleep(CONNECT_DELAY_PAGE / 2)
                continue

        # convert to pure strings
        self.items_raw_all_dict[n] = [str(item) for item in items_raw_temp]
        with self.items_all_lock:
            total_count_temp = 0
            for k in self.items_raw_all_dict:
                total_count_temp += len(self.items_raw_all_dict[k])
            self.total_count = total_count_temp

    def _filter_last_items(self) -> None:
        # Filter out all trailing items if needed (last page)
        trace('Filtering trailing back items...')

        if (self.has_gui() or self.lower_bound == 0) and as_date(self.date_min) <= as_date(DATE_MIN_DEFAULT):
            trace('last items filter is irrelevant! Skipping')
            return

        if len(self.items_raw_all) < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'mindate at {self.date_min}, lower bound at {self.lower_bound:d}, filtering')
        items_tofilter = self.items_raw_all[-(min(len(self.items_raw_all), self._get_items_per_page() * 2)):]
        self.items_raw_all = self.items_raw_all[:-len(items_tofilter)]  # type: List[Optional[str]]
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
                self.items_raw_all += items_tofilter
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
                self.items_raw_all += items_tofilter
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
                self.items_raw_all += items_tofilter
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
            exceed_id = (0 < int(item_id) < self.lower_bound) if self.lower_bound > 0 else False

            if exceed_date:
                trace(f'Info: TagProc_filter: {item_id} exceeds min date ({post_date} < {self.date_min}), shuffling backwards...')
                forward_lim, step_direction = backward()
            elif exceed_id:
                trace(f'Info: TagProc_filter: id < lower bound at {item_id} - stepping backwards...')
                forward_lim, step_direction = backward()
            else:
                trace(f'Info: TagProc_filter: id >= lower bound at {item_id} and not exceed min date - stepping forward...')
                backward_lim, step_direction = forward()

    def _filter_first_items(self) -> None:
        # Filter out all trailing items if needed (front page)
        trace('Filtering trailing front items...')

        if (self.has_gui() or self.upper_bound == 0) and as_date(self.date_max) >= datetime.today().date():
            trace('first items filter is irrelevant! Skipping')
            return

        if len(self.items_raw_all) < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'maxdate at {self.date_max}, upper bound at {self.upper_bound:d}, filtering')
        items_tofilter = self.items_raw_all[:(min(len(self.items_raw_all), self._get_items_per_page() * 2))]
        self.items_raw_all = self.items_raw_all[len(items_tofilter):]  # type: List[Optional[str]]

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
                self.items_raw_all = items_tofilter + self.items_raw_all
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
                self.items_raw_all = items_tofilter + self.items_raw_all
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
                self.items_raw_all = items_tofilter + self.items_raw_all  # type: List[Optional[str]]
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
            exceed_id = (0 < self.upper_bound < int(item_id)) if self.upper_bound > 0 else False

            if exceed_date:
                trace(f'Info: TagProc_filter: {item_id} exceeds max date ({post_date} > {self.date_max}), stepping forward...')
                backward_lim, step_direction = forward()
            elif exceed_id:
                trace(f'Info: TagProc_filter: id > upper bound at {item_id} - stepping forward...')
                backward_lim, step_direction = forward()
            else:
                trace(f'Info: TagProc_filter: id <= upper bound at {item_id} and not exceed max date - stepping backwards...')
                forward_lim, step_direction = backward()

    def _filter_items_by_type(self) -> None:
        trace('Filtering items by type...')

        if self.skip_images is False and self.skip_videos is False:
            trace('Both types are enabled! skipped.')
            return

        total_count_temp = self.total_count

        idx = 0
        while idx < len(self.items_raw_all):
            self.catch_cancel_or_ctrl_c()

            h = str(self.items_raw_all[idx])
            is_vid = self._is_video(h)
            if self.skip_videos if is_vid else self.skip_images:
                # trace(f'Info: TagProc_filter: removing {"video" if _is_video else "image"} {_extract_id(extract_local_addr(h))}!')
                self.items_raw_all.pop(idx)
                self.total_count -= 1
                continue

            idx += 1

        if total_count_temp != self.total_count:
            trace(f'Filtered out {total_count_temp - self.total_count:d} / {total_count_temp:d} items!')

    def _filter_existing_items(self) -> None:
        trace('Filtering out existing items...')

        if not path.exists(self.dest_base):
            return

        curdirfiles = list(reversed(listdir(self.dest_base))) if self.reverse_order else listdir(self.dest_base)

        total_count_temp = self.total_count

        idx = 0
        while idx < len(self.items_raw_all):
            self.catch_cancel_or_ctrl_c()

            h = self._local_addr_from_string(str(self.items_raw_all[idx]))
            item_id = self._extract_id(h)

            rex_cdfile = re_compile(fr'^(?:{self._get_module_abbr_p()})?{item_id}[._].*?$')
            rem_idx = 0
            f_idx = 0
            f_len = len(curdirfiles)
            found = False
            while f_idx < f_len:
                cdfile = curdirfiles[f_idx]
                if re_fullmatch(rex_cdfile, cdfile) is not None:
                    rem_idx = f_idx
                    found = True
                    break
                f_idx += 1

            if found is True:
                # trace(f'Info: TagProc_filter: {item_id} already exists!')
                curdirfiles.pop(rem_idx)
                self.items_raw_all.pop(idx)
                self.total_count -= 1
                continue

            idx += 1

        if total_count_temp != self.total_count:
            trace(f'Filtered out {total_count_temp - self.total_count:d} / {total_count_temp:d} items!')

    def _filter_items_matching_negative_and_groups(self) -> None:
        trace('Filtering out items using custom filters...')

        if len(self.neg_and_groups) == 0:
            return

        abbrp = self._get_module_abbr_p()
        total_count_old = len(self.items_raw_all)
        removed_count = 0
        for idx in reversed(range(total_count_old)):
            h = self._local_addr_from_string(str(self.items_raw_all[idx]))
            item_id = self._extract_id(h)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_id}'
            item_info = self.item_info_dict.get(idstring)
            tags_list = item_info.tags.split(' ')
            if any(all(any(re_fullmatch(p, tag) is not None for tag in tags_list) for p in plist) for plist in self.neg_and_groups):
                del self.item_info_dict[idstring]
                del self.items_raw_all[idx]
                removed_count += 1

        if removed_count > 0:
            trace(f'Filtered out {removed_count:d} / {total_count_old:d} items!')

    def _process_tags(self, tag_str: str) -> None:
        self.url = self.form_tags_search_address(tag_str)
        self.current_state = DownloaderStates.STATE_SCANNING_PAGES1
        self.total_count = self.get_items_query_size(self.url)

        page_size = self._get_items_per_page()

        if isinstance(self.total_count, int):
            self.minpage = 0
            self.maxpage = (self.total_count // page_size + (1 if self.total_count % page_size != 0 else 0)) - 1

            if self.total_count <= 0:
                trace('Nothing to process: query result is empty')
                return

            trace(f'Total {self.total_count:d} items found across {self._num_pages():d} pages')

            if 0 < self._get_max_search_depth() < self.total_count:
                trace('\nFATAL: too many possible matches, won\'t be able to fetch html for all the pages!\nTry adding an ID filter.')
                return

            self.total_pages = self._num_pages()

            pageargs = [
                (DownloaderStates.STATE_SCANNING_PAGES2, True, PageFilterType.MODE_ID),
                (DownloaderStates.STATE_SCANNING_PAGES3, False, PageFilterType.MODE_ID),
                (DownloaderStates.STATE_SCANNING_PAGES4, True, PageFilterType.MODE_DATE),
                (DownloaderStates.STATE_SCANNING_PAGES5, False, PageFilterType.MODE_DATE)
            ]

            def page_filter(st: DownloaderStates, di: bool, ft: PageFilterType) -> int:
                self.current_state = st
                trace(f'Looking for {("min" if di else "max")} page by: {ft.value}...')
                return self._get_page_boundary(di, ft)

            for fstate, direction, ftype in pageargs:
                if fstate in (DownloaderStates.STATE_SCANNING_PAGES2, DownloaderStates.STATE_SCANNING_PAGES4):
                    self.minpage = page_filter(fstate, direction, ftype)
                elif fstate in (DownloaderStates.STATE_SCANNING_PAGES3, DownloaderStates.STATE_SCANNING_PAGES5):
                    self.maxpage = page_filter(fstate, direction, ftype)
                self.total_pages = self._num_pages()

            self.total_count = min((self._num_pages() * page_size), self.total_count)
            trace(f'new totalcount: {self.total_count:d}')

            # list all items on selected pages
            trace(f'Scanning pages {self.minpage + 1:d} - {self.maxpage + 1:d}')

            self.total_count_old = self.total_count
            self.total_count = 0  # type: Union[int, BeautifulSoup]
            self.current_state = DownloaderStates.STATE_SCANNING_PAGES6

            if self.maxthreads_items > 1 and self._num_pages() > 1:
                trace(f'  ...using {self.maxthreads_items:d} threads...')
                c_page = 0
                arr_temp = list()
                for n in range(self.minpage, self.maxpage + 1):
                    c_page += 1
                    arr_temp.append([n, c_page, self.maxpage])

                # BUG: pool.map_async from multiprocessing.dummy causes random
                # Runtime Error: dict changed size during iteration even though temp dict is only passed to it
                # So using this monstrosity
                ress = list()
                self.active_pool = Pool(min(10, max(2, max(self.maxthreads_items // 2, self._num_pages() // 100))))
                for larr in arr_temp:
                    ress.append(self.active_pool.apply_async(self._get_page_items, args=larr))
                self.active_pool.close()

                while len(ress) > 0:
                    self.catch_cancel_or_ctrl_c()
                    while len(ress) > 0 and ress[0].ready():
                        ress.pop(0)
                    thread_sleep(0.2)

                self.active_pool.terminate()
                self.active_pool = None  # type: Optional[ThreadPool]

                # pool = Pool(maxthreads_items)
                # res = pool.map_async(self.GetPageItems_L, arr_temp, 1)  # max(((page_max - page_min) + 1) / 20, 1)
                # pool.map_async(self.GetPageItems_L, arr_temp, max(((page_max - page_min) + 1) / 20, 1))
                # pool.close()
                # active_pool = pool
                # res.get(0x7FFFFFFF)
                # pool.join()
                # active_pool = None
            else:
                c_page = 0
                for n in range(self.minpage, self.maxpage + 1):
                    self.catch_cancel_or_ctrl_c()
                    c_page += 1
                    self._get_page_items(n, c_page, self.maxpage)

            # move out async result into a linear array
            self.items_raw_all = [None] * self.total_count  # type: List[Optional[str]]
            cur_idx = 0
            for k in range(self.minpage, self.maxpage + 1):
                cur_l = self.items_raw_all_dict[k]
                for i in range(len(cur_l)):
                    self.items_raw_all[cur_idx] = cur_l[i]
                    cur_idx += 1

            self.items_raw_all_dict = dict()  # type: Dict[int, List[str]]

            self.items_raw_all = list(unique_everseen(self.items_raw_all))  # type: List[Optional[str]]
        else:
            # we have been redirected to a page with our single result! compose item string manually
            if __RUXX_DEBUG__:
                trace('Warning (W1): A single match redirect was hit, forming item string manually')

            self._form_item_string_manually()

        def after_filter(sleep_time: float = 0.2) -> None:
            self.total_count = len(self.items_raw_all)
            trace(f'new totalcount: {self.total_count:d}')
            thread_sleep(sleep_time)

        def apply_filter(state: DownloaderStates, func: Callable[[], None], sleep_time: float = 0.1) -> None:
            self.current_state = state
            func()
            after_filter(sleep_time)

        after_filter()

        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS1, self._filter_last_items)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS2, self._filter_first_items)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS3, self._filter_items_by_type)
        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS4, self._filter_existing_items)

        # store items info for future processing
        # custom filters may exclude certain items from the infos dict
        self._extract_all_infos()

        apply_filter(DownloaderStates.STATE_FILTERING_ITEMS4, self._filter_items_matching_negative_and_groups)

        if self.total_count <= 0:
            trace('\nNothing to process: queue is empty')
            return

        if self.download_limit > 0:
            if len(self.items_raw_all) > self.download_limit:
                trace(f'\nShrinking queue down to {self.download_limit:d} items...')
                if self.reverse_order is True:
                    self.items_raw_all = self.items_raw_all[self.download_limit * -1:]
                else:
                    self.items_raw_all = self.items_raw_all[:self.download_limit]
                self.total_count = len(self.items_raw_all)
            else:
                trace('\nShrinking queue down is not required!')

        item_front = self._extract_item_info(self.items_raw_all[0]).id
        item_end = self._extract_item_info(self.items_raw_all[-1]).id
        # front item is always >= end item
        trace(f'\nProcessing {self.total_count:d} items, bound {item_end} to {item_front}')

        if self.reverse_order is True:
            self.items_raw_all.reverse()
        # default order is newest first
        orders = ['oldest', 'newest']
        trace(f'...{orders[1 - int(self.reverse_order)]} to {orders[self.reverse_order]}\n')

        self.current_state = DownloaderStates.STATE_DOWNLOADING

        trace(f'{self.total_count:d} item(s) scheduled, {self.maxthreads_items:d} thread(s) max\nWorking...\n')

        if self.maxthreads_items > 1 and len(self.items_raw_all) > 1:
            # pool = Pool(self.maxthreads_items)
            # pool.map_async(self._process_item, self.items_raw_all, max((len(self.items_raw_all) // self.maxthreads_items) // 100, 1))
            # pool.close()
            # self.active_pool = pool
            # pool.join()
            # pool.terminate()

            ress = list()
            self.active_pool = Pool(self.maxthreads_items)
            for iarr in self.items_raw_all:
                ress.append(self.active_pool.apply_async(self._process_item, args=[str(iarr)]))
            self.active_pool.close()

            while len(ress) > 0:
                self.catch_cancel_or_ctrl_c()
                while len(ress) > 0 and ress[0].ready():
                    ress.pop(0)
                thread_sleep(0.2)

            self.active_pool.terminate()
            self.active_pool = None  # type: Optional[ThreadPool]
        else:
            for i in range(self.total_count):
                self._process_item(self.items_raw_all[i])

        trace(f'\nAll {"skipped" if self.download_mode == DownloadModes.DOWNLOAD_SKIP else "processed"} ({self.total_count:d} items)...')

    def _parse_tags(self, tags_base_arr: Iterable[str]) -> None:
        cc = self._get_tags_concat_char()
        sc = self._get_idval_equal_seaparator()
        can_have_or_groups = self._can_have_or_groups()
        split_always = self._split_or_group_into_tasks_always()
        # join by ' ' is required by tests, although normally len(args.tags) == 1
        tags_list, self.neg_and_groups = extract_neg_and_groups(' '.join(tags_base_arr))
        self.tags_str_arr = split_tags_into_tasks(tags_list, cc, sc, can_have_or_groups, split_always)

    def _process_all_tags(self) -> None:
        if self.warn_nonempty:
            if self.has_gui():
                if path.isdir(self.dest_base) and len(listdir(self.dest_base)) > 0:
                    if not confirm_yes_no(title='Download', msg=f'Destination folder \'{self.dest_base}\' is not empty. Continue anyway?'):
                        return
            else:
                trace('Warning (W1): argument \'-warn_nonempty\' is ignored in non-GUI mode')

        if self.download_mode != DownloadModes.DOWNLOAD_FULL:
            trace(f'{"=" * LINE_BREAKS_AT}\n\n(Emulation Mode)')
        trace(f'\n{"=" * LINE_BREAKS_AT}\n{APP_NAME} core ver {APP_VERSION}')
        trace(f'Starting {self._get_module_abbr()}_manual', False, True)
        trace(f'\n{len(self.neg_and_groups):d} \'excluded tags combination\' custom filter(s) parsed')
        trace(f'{self._tasks_count():d} tasks scheduled:\n{NEWLINE.join(self.tags_str_arr)}\n\n{"=" * LINE_BREAKS_AT}')
        for i in range(self._tasks_count()):
            trace(f'\ntask {i + 1} in progress...\n')
            try:
                self._process_tags(self.tags_str_arr[i])
                trace(f'task {i + 1} completed...')
            except ThreadInterruptException:
                trace(f'task {i + 1} aborted...')
                raise
            except Exception:
                trace(f'task {i + 1} failed...')
            finally:
                if __RUXX_DEBUG__:
                    trace(f'\ntask {i + 1}:\n total: {self.total_count:d}\n succs: {self.success_count:d}\n fails: {self.fail_count:d}')
                trace('=' * LINE_BREAKS_AT)
                self.total_count_all += self.total_count
                self.success_count_all += self.success_count
                self.fail_count_all += self.fail_count
                if i + 1 < self._tasks_count():
                    self.processed_count = 0
                    self.total_count = 0
                    self.success_count = 0
                    self.fail_count = 0
        self.item_info_dict = {
            k: v for k, v in sorted(sorted(self.item_info_dict.items(), key=lambda item: item[0]), key=lambda item: int(item[1].id))
        }  # type: Dict[str, ItemInfo]
        if len(self.item_info_dict) > 0 and (self.dump_tags is True or self.dump_source is True):
            if self.dump_tags is True:
                self._dump_all_tags()
            if self.dump_source is True:
                self._dump_all_sources()
            trace('=' * LINE_BREAKS_AT)
        total_files = min(self.success_count_all + self.fail_count_all, self.total_count_all)
        trace(f'\n{self._tasks_count():d} tasks completed, {self.success_count_all:d} / {total_files:d} items succeded', False, True)
        if len(self.failed_items) > 0:
            trace(f'{len(self.failed_items):d} failed items:')
            trace('\n'.join(self.failed_items))

    @abstractmethod
    def form_tags_search_address(self, tags: str, maxlim: Optional[int] = None) -> str:
        ...

    def launch(self, args: Namespace) -> None:
        self.reset_root_thread(current_process())

        try:
            self.parse_args(args)
            self._process_all_tags()
        except (KeyboardInterrupt, ThreadInterruptException):
            trace(f'\nInterrupted by {str(exc_info()[0])}!\n', True)
            self.my_root_thread.killed = True
            if self.active_pool:
                self.active_pool.join()
                trace('\nExiting gracefully\n', True)
        except Exception:
            trace(f'Unhandled {str(exc_info()[0])}: {str(exc_info()[1])}', True)
        finally:
            self.current_state = DownloaderStates.STATE_IDLE

    def parse_args(self, args: Namespace) -> None:
        assert hasattr(args, 'tags') and type(args.tags) == list

        ThreadedHtmlWorker.parse_args(self, args)

        self.add_filename_prefix = args.prefix or self.add_filename_prefix
        self.reverse_order = args.rev or self.reverse_order
        self.dump_tags = args.dump_tags or self.dump_tags
        self.dump_source = args.dump_sources or self.dump_source
        self.append_info = args.append_info or self.append_info
        self.download_mode = args.dmode or self.download_mode
        self.download_limit = args.dlimit or self.download_limit
        self.lower_bound = args.low or self.lower_bound
        self.upper_bound = args.high or self.upper_bound
        self.maxthreads_items = args.threads or self.maxthreads_items
        self.skip_images = args.skip_img or self.skip_images
        self.skip_videos = args.skip_vid or self.skip_videos
        self.prefer_webm = args.webm or self.prefer_webm
        self.low_res = args.lowres or self.low_res
        self.date_min = args.mindate or self.date_min
        self.date_max = args.maxdate or self.date_max
        self.dest_base = normalize_path(args.path) if args.path else self.dest_base
        self.warn_nonempty = args.warn_nonempty or self.warn_nonempty
        self._parse_tags(args.tags)

    def _extract_all_infos(self) -> None:
        abbrp = self._get_module_abbr_p()
        for item in self.items_raw_all:
            item_info = self._extract_item_info(item)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_info.id}'
            self.item_info_dict[idstring] = item_info
            # debug
            for key in item_info.__slots__:
                if key in ItemInfo.optional_slots:  # fields set later
                    continue
                if item_info.__getattribute__(key) == '':
                    if __RUXX_DEBUG__:
                        trace(f'Info: extract info {abbrp}{item_info.id}: not initialized field {key}!')

    def _dump_all_tags(self) -> None:
        trace('\nSaving tags...')
        id_begin = self.item_info_dict[list(self.item_info_dict)[0]].id
        id_end = self.item_info_dict[list(self.item_info_dict)[-1]].id
        abbrp = self._get_module_abbr_p()

        # rx_!tags_00000-00000.txt
        filename = f'{self.dest_base}{abbrp}!tags{UNDERSCORE}{id_begin}-{id_end}.txt'

        if self.has_gui() and path.isfile(filename):
            if not confirm_yes_no(title='Save tags', msg=f'File \'{filename}\' already exists. Overwrite?'):
                trace('Error.\n')
                return

        if not path.exists(self.dest_base):
            try:
                makedirs(self.dest_base)
            except Exception:
                thread_exit('ERROR: Unable to create subfolder!')

        with open(filename, 'w', encoding=DEFAULT_ENCODING) as dump:
            for item_info in self.item_info_dict.values():
                item_line = f'{abbrp}{item_info.id}: {format_score(item_info.score)} {item_info.tags.strip()}\n'
                dump.write(item_line)

        trace('Done.')

    def _dump_all_sources(self) -> None:
        trace('\nSaving sources...')
        id_begin = self.item_info_dict[list(self.item_info_dict)[0]].id
        id_end = self.item_info_dict[list(self.item_info_dict)[-1]].id
        abbrp = self._get_module_abbr_p()

        # rx_!sources_00000-00000.txt
        filename = f'{self.dest_base}{abbrp}!sources{UNDERSCORE}{id_begin}-{id_end}.txt'

        if self.has_gui() and path.isfile(filename):
            if not confirm_yes_no(title='Save sources', msg=f'File \'{filename}\' already exists. Overwrite?'):
                trace('Error.\n')
                return

        if not path.exists(self.dest_base):
            try:
                makedirs(self.dest_base)
            except Exception:
                thread_exit('ERROR: Unable to create subfolder!')

        with open(filename, 'w', encoding=DEFAULT_ENCODING) as dump:
            for item_info in self.item_info_dict.values():
                if len(item_info.source) < 2:
                    item_info.source = SOURCE_DEFAULT
                item_line = f'{abbrp}{item_info.id}: {item_info.source.strip()}\n'
                dump.write(item_line)

        trace('Done.')

    def has_gui(self) -> bool:
        return hasattr(self.my_root_thread, 'gui')

#
#
#########################################
