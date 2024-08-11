# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from abc import abstractmethod
from datetime import datetime
from os import path, curdir, listdir
from typing import List, Dict, Set, Pattern, MutableSet, Tuple, Union, Optional, Match

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import DownloadModes, DownloaderStates, ItemInfo, PageCheck, DATE_MIN_DEFAULT, FMT_DATE
from app_logger import trace
from app_network import ThreadedHtmlWorker, thread_exit
from app_utils import normalize_path, as_date


class DownloaderBase(ThreadedHtmlWorker):
    """
    DownloaderBase !Abstract!
    """
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

        # config
        self.add_filename_prefix = False
        self.dump_tags = False
        self.dump_sources = False
        self.dump_comments = False
        self.dump_per_item = False
        self.merge_lists = False
        self.append_info = False
        self.download_mode = DownloadModes.FULL
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
        self.tags_str_arr: List[str] = list()
        # extra
        self.cmdline = ''
        self.get_max_id = False

        # results
        self.url = ''
        self.minpage = 0
        self.maxpage = 0
        self.success_count = 0
        self.fail_count = 0
        self.failed_items: List[str] = list()
        self.total_count = 0
        self.total_count_old = 0
        self.processed_count = 0
        self.total_pages = 0
        self.current_task_num = 0
        self.orig_tasks_count = 0
        self.current_state = DownloaderStates.IDLE
        self.items_raw_per_task: List[str] = list()
        self.items_raw_per_page: Dict[int, List[str]] = dict()
        self.items_raw_all: List[str] = list()
        self.item_info_dict_per_task: Dict[str, ItemInfo] = dict()
        self.item_info_dict_all: Dict[str, ItemInfo] = dict()
        self.neg_and_groups: List[List[Pattern[str]]] = list()
        self.known_parents: Set[str] = set()
        self.default_sort = True
        self.favorites_search_user = ''
        self.pool_search_id = 0

    @abstractmethod
    def _is_fav_search_conversion_required(self) -> bool:
        ...

    @abstractmethod
    def _is_fav_search_single_step(self) -> bool:
        ...

    @abstractmethod
    def _has_native_id_filter(self) -> bool:
        ...

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
    def _form_item_string_manually(self, raw_html_page: BeautifulSoup) -> str:
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
    def _get_items_query_size_or_html(self, url: str, tries: int = None) -> Union[int, BeautifulSoup]:
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

    @abstractmethod
    def _consume_custom_module_tags(self, tags: str) -> str:
        ...

    def _execute_module_filters(self, parents: MutableSet[str]) -> None:
        pass

    def _extract_favorite_user(self, fav_user_tags: List[Optional[Match]]) -> None:
        self.favorites_search_user = str(fav_user_tags[-1].group(1)) if fav_user_tags else 0

    def _clean_favorite_user(self) -> None:
        self.favorites_search_user = ''

    def _extract_pool_id(self, pool_tags: List[Optional[Match]]) -> None:
        self.pool_search_id = int(pool_tags[-1].group(1)) if pool_tags else 0

    def _clean_pool_id(self) -> None:
        self.pool_search_id = 0

    def _tasks_count(self) -> int:
        return len(self.tags_str_arr)

    def _num_pages(self) -> int:
        return (self.maxpage - self.minpage) + 1

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

    def _filter_last_items(self) -> None:
        # Filter out all trailing items if needed (last page)
        trace('Filtering trailing back items...')

        if as_date(self.date_min) <= as_date(DATE_MIN_DEFAULT):
            trace('last items filter is irrelevant! Skipping')
            return

        items_raw_list = self.items_raw_all if self.current_state == DownloaderStates.DOWNLOADING else self.items_raw_per_task
        orig_len = len(items_raw_list)
        if orig_len < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'mindate at {self.date_min}, filtering')
        boundary = orig_len - min(orig_len, self._get_items_per_page() * 2)

        divider = 1
        dofinal = False
        step_direction = 1
        cur_step = 0
        f_total = orig_len - boundary
        cur_index = boundary
        forward_lim = orig_len
        backward_lim = boundary - 1
        while True and f_total > 0:  # while True
            cur_step += 1
            trace(f'step {cur_step:d}')

            self.catch_cancel_or_ctrl_c()

            divider = min(divider * 2, f_total)
            cur_index += (f_total // divider) * step_direction
            trace(f'index {cur_index:d} (div {divider:d}, step {step_direction:d})')

            if cur_index < backward_lim:
                trace('Error: cur_index < backward_lim, aborting filter!')
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
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
                trace(f'Filtered out {orig_len - cur_index:d} / {orig_len:d} items')
                del items_raw_list[cur_index:]
                break

            h = self._local_addr_from_string(str(items_raw_list[cur_index]))
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

        items_raw_list = self.items_raw_all if self.current_state == DownloaderStates.DOWNLOADING else self.items_raw_per_task
        orig_len = len(items_raw_list)
        if orig_len < 2:
            trace('less than 2 items: skipping')
            return

        trace(f'maxdate at {self.date_max}, filtering')
        boundary = min(orig_len, self._get_items_per_page() * 2)

        divider = 1
        dofinal = False
        step_direction = 1
        cur_step = 0
        f_total = boundary
        cur_index = 0
        forward_lim = boundary
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
                break
            if cur_index > forward_lim:
                trace('Error: cur_index > forward_lim, aborting filter!')
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
                trace(f'Filtered out {cur_index:d} / {orig_len:d} items')
                del items_raw_list[:cur_index]
                break

            h = self._local_addr_from_string(str(items_raw_list[cur_index]))
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

        idx: int
        for idx in reversed(range(len(self.items_raw_per_task))):
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

        idx: int
        for idx in reversed(range(len(self.items_raw_per_task))):
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

        def file_matches(filename: str, iid: str) -> bool:
            return (filename.startswith(f'{iid}.') or filename.startswith(f'{iid}_')
                    or filename.startswith(f'{abbrp}{iid}.') or filename.startswith(f'{abbrp}{iid}_'))

        abbrp = self._get_module_abbr_p()
        idx: int
        for idx in reversed(range(len(self.items_raw_per_task))):
            self.catch_cancel_or_ctrl_c()
            h = self._local_addr_from_string(str(self.items_raw_per_task[idx]))
            item_id = self._extract_id(h)
            for f_idx in reversed(range(len(curdirfiles))):
                if file_matches(curdirfiles[f_idx], item_id):
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

        m_dict: Dict[str, List[str]] = dict()

        def match_neg_group(p: Pattern[str], t: str, pl: List[Pattern[str]]) -> bool:
            ngm = p.fullmatch(t)
            if ngm:
                pp_str = f'-({",".join(pp.pattern[1:-1] for pp in pl)})'
                if len(pp_str) > 50:
                    pp_str = f'{pp_str[:47]}...'
                if pp_str not in m_dict:
                    m_dict[pp_str] = list()
                m_dict[pp_str].append(t)
            return ngm is not None

        abbrp = self._get_module_abbr_p()
        total_count_old = len(self.items_raw_per_task)
        removed_count = 0
        removed_messages: List[str] = list()
        idx: int
        for idx in reversed(range(total_count_old)):
            h = self._local_addr_from_string(str(self.items_raw_per_task[idx]))
            item_id = self._extract_id(h)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_id}'
            item_info = self.item_info_dict_per_task.get(idstring)
            tags_list = item_info.tags.lower().split(' ')
            m_dict.clear()
            if any(all(any(match_neg_group(patt, tag, plist) for tag in tags_list) for patt in plist) for plist in self.neg_and_groups):
                # Note: above algorithm is minimal match, only first matching combination will be reported
                if self.verbose and self._has_native_id_filter():
                    removed_messages.append('\n'.join(f'{abbrp}{item_id} contains excluded tags combination \'{mk}\': '
                                            f'{",".join(m_dict[mk])}. Skipped!' for mk in m_dict if len(m_dict[mk]) > 1))
                if item_id in parents:
                    parents.remove(item_id)
                if item_info.parent_id in parents:
                    parents.remove(item_info.parent_id)
                del self.item_info_dict_per_task[idstring]
                del self.items_raw_per_task[idx]
                removed_count += 1

        if removed_count > 0:
            trace('\n'.join(removed_messages))
            trace(f'Filtered out {removed_count:d} / {total_count_old:d} items!')

    def _filter_items_by_module_filters(self, parents: MutableSet[str]) -> None:
        trace('Filtering out items using module filters...')
        self._execute_module_filters(parents)

#
#
#########################################
