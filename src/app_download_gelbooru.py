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
from datetime import datetime
from multiprocessing.dummy import current_process
from re import Pattern

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import DownloadModes, ItemInfo, FILE_NAME_FULL_MAX_LEN, FMT_DATE
from app_download import Downloader
from app_logger import trace
from app_module import ProcModule
from app_network import thread_exit
from app_re import re_sample_file_link, re_orig_file_link, re_item_info_part_xml

__all__ = ('DownloaderGelbooru',)

item_info_fields = {'file_url': 'ext'}


class DownloaderGelbooru(Downloader):
    """
    DownloaderGelbooru !Abstract!
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def _get_re_post_page(self) -> Pattern:
        raise NotImplementedError

    def _get_module_specific_default_headers(self) -> dict[str, str]:
        return {}

    def _get_module_specific_default_cookies(self) -> dict[str, str]:
        return {}

    def _is_pool_search_conversion_required(self) -> bool:
        return True

    def _is_fav_search_conversion_required(self) -> bool:
        return True

    def _is_fav_search_single_step(self) -> bool:
        return False

    def _supports_native_id_filter(self) -> bool:
        return True

    def _is_search_overload_page(self, raw_html_page: BeautifulSoup) -> bool:
        # <h1>Search is overloaded! Try again later...</h1>
        search_err = raw_html_page.find_all('h1', string='Search is overloaded! Try again later...')
        return len(search_err) > 0

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}&pid={n * (self._get_items_per_page() if self.favorites_search_user or self.pool_search_str else 1):d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        if self.favorites_search_user or self.pool_search_str:
            divs = raw_html_page.find_all('span', class_='thumb')
            for div in divs:
                tag_a = div.find('a')
                tag_a['href'] = f"{self._get_sitename()}{tag_a['href']}"
            return divs
        else:
            return raw_html_page.find_all('post')

    def _local_addr_from_string(self, h: str) -> str:
        return h

    def _extract_id(self, addr: str) -> str:
        id_idx = addr.find(' id="') + len(' id="')
        return addr[id_idx:addr.find('"', id_idx + 1)]

    def _is_video(self, h: str) -> bool:
        # tags are not 100% accurate so use a more direct approach
        _, file_ext = self.extract_file_url(h)
        return file_ext in {'mp4', 'webm'}

    def _get_item_html(self, h: str) -> str:
        return h

    def _extract_post_date(self, raw: str) -> str:
        try:
            # 'Mon Jan 06 21:51:58 +0000 2020' -> '06-01-2020'
            date_idx = raw.find('created_at="') + len('created_at="')
            d = datetime.strptime(raw[date_idx:raw.find('"', date_idx + 1)], '%a %b %d %X %z %Y')
            return d.strftime(FMT_DATE)
        except Exception:
            thread_exit(f'Unable to extract post date from raw: {raw}', -446)

    def _get_items_query_size_or_html(self, url: str, tries: int = None) -> int:
        if self.favorites_search_user:
            raw_html = self.fetch_html(f'{url}&pid=0', tries, do_cache=True)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
            last = 1
            last_page_buttons = raw_html.find_all('a', onclick=self._get_re_post_page())
            for but in last_page_buttons:
                href = str(but.get('onclick', '=0'))
                begin_idx = href.rfind('=') + 1
                end_idx = href.find('\'', begin_idx + 1)
                last = max(last, 1 + int(href[begin_idx:end_idx]))

            if last > self._get_max_search_depth() // self._get_items_per_page():
                if not self.get_max_id:
                    trace('Error: items count got past search depth!')
                return last * self._get_items_per_page()
            elif last > 1:
                raw_html = self.fetch_html(f'{url}&pid={last - 1:d}', do_cache=True)
                if raw_html is None:
                    thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-448)

            # items count on all full pages plus items count on last page
            last_thumbs = len(self._get_all_post_tags(raw_html))
            count: int | BeautifulSoup = (last - 1) + last_thumbs
            return count
        elif self.pool_search_str:
            raw_html = self.fetch_html(f'{url}&pid=0', tries, do_cache=True)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
            last = 1
            last_page_buttons = raw_html.find_all('a', href=self._get_re_post_page())
            for but in last_page_buttons:
                but_str = str(but.text)
                if but_str.isnumeric():
                    last = max(last, int(but_str))

            if last > self._get_max_search_depth() // self._get_items_per_page():
                if not self.get_max_id:
                    trace('Error: items count got past search depth!')
                return last * self._get_items_per_page()
            elif last > 1:
                raw_html = self.fetch_html(f'{url}&pid={(last - 1) * self._get_items_per_page():d}', do_cache=True)
                if raw_html is None:
                    thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-448)

            # items count on all full pages plus items count on last page
            last_thumbs = len(self._get_all_post_tags(raw_html))
            count: int | BeautifulSoup = (last - 1) * self._get_items_per_page() + last_thumbs
            return count
        else:
            raw_html = self.fetch_html(f'{url}&pid=0', tries)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)

            try:
                count_ = int(raw_html.find('posts').get('count'))
                return count_
            except Exception:
                if ProcModule.is_rx() and 'Missing authentication' in str(raw_html):
                    thread_exit('FATAL: Invalid RX API key!', code=-478)

    def _get_image_address(self, h: str) -> tuple[str, str]:
        def hi_res_addr() -> tuple[str, str]:
            addr, ext = self.extract_file_url(h)
            return addr, ext

        def low_res_addr() -> tuple[str, str]:
            addr, ext = self.extract_sample_url(h)
            return addr, ext

        if self.low_res:
            address, fmt = low_res_addr()
            if len(address) == 0:
                trace('Warning (W1): GetPicAddr can\'t not find low res image, trying alternative...', True)
                address, fmt = hi_res_addr()
        else:
            address, fmt = hi_res_addr()
            if len(address) == 0:
                trace('Warning (W1): GetPicAddr can\'t find high res image, trying alternative...', True)
                address, fmt = low_res_addr()

        if len(address) == 0:
            trace('FATAL: GetPicAddr could not find anything!', True)
            trace(f'\nstring:\n\n{h}', True)
            assert False

        return address, fmt

    def _get_video_address(self, h: str) -> tuple[str, str]:
        addr, ext = self.extract_file_url(h)
        if len(addr) == 0:
            addr, ext = self.extract_sample_url(h)

        if len(addr) == 0:
            trace('FATAL: GetVidAddr could not find anything!', True)
            trace(f'\nstring:\n\n{h}', True)
            assert False

        return addr, ext

    def _extract_item_info(self, item: str) -> ItemInfo:
        try:
            item_info = ItemInfo()
            if self.is_killed():
                return item_info
            for part in re_item_info_part_xml.findall(item):
                name, value = tuple(str(part).split('=', 1))
                name = item_info_fields.get(name, name)
                if name == 'ext':  # special case: file_url -> ext -> extract ext
                    value = value[value.rfind('.') + 1:]
                if name in item_info.__slots__:
                    while name == 'id' and not value[0].isnumeric():  # id=p1234567
                        value = value[1:]
                    item_info.__setattr__(name, value.replace('\n', ' ').replace('"', '').strip())
            return item_info
        except Exception:
            self._on_thread_exception(current_process().name)
            raise

    def _split_or_group_into_tasks_always(self) -> bool:
        return False

    def _can_extract_item_info_without_fetch(self) -> bool:
        return True

    def _consume_custom_module_tags(self, tags: str) -> str:
        return tags

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base_s) + len(item_id) + 1 + len(fmt))
        self._download(address, item_id, f'{self.dest_base_s}{self._try_append_extra_info(item_id, hint_maxlen)}.{fmt}')

    def _form_tags_search_address(self, tags: str, maxlim: int = None) -> str:
        return (f'{self._get_sitename()}index.php?page=favorites&s=view&id={self.favorites_search_user}' if self.favorites_search_user else
                f'{self._get_sitename()}index.php?page=pool&s=show&id={self.pool_search_str}' if self.pool_search_str else
                f'{self._get_sitename()}index.php?page=dapi&s=post&q=index{self._get_api_key()}&tags={tags}{self._maxlim_str(maxlim)}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        try:
            h = raw
            item_id = self._extract_id(h)

            if self.dump_comments is True and self.has_comments(h):
                self._extract_comments(item_id)

            if self.download_mode == DownloadModes.SKIP:
                self._inc_proc_count()
                return

            orig_item = re_orig_file_link.search(h)

            if self.add_filename_prefix is True:
                item_id = f'{self._get_module_abbr_p()}{item_id}'

            if orig_item:
                if len(orig_item.groupdict()) > 1:
                    trace(f'Warning (W1): ProcItem: {len(orig_item.groupdict()):d} items for {item_id}', True)

                is_vid = self._is_video(h)
                if is_vid:
                    self._process_video(h, item_id)
                else:
                    self._process_image(h, item_id)
            else:
                trace(f'Warning (W2): unable to extract file url from {h}, deleted?', True)

            self._inc_proc_count()
        except Exception:
            self._on_thread_exception(current_process().name)
            raise

    @abstractmethod
    def _extract_comments(self, item_id: str) -> None:
        raise NotImplementedError

    @staticmethod
    def extract_file_url(h: str) -> tuple[str, str]:
        file_re_res = re_sample_file_link.search(h)
        if file_re_res is None:
            return '', ''
        file_url = file_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    @staticmethod
    def has_comments(h: str) -> bool:
        id_idx = h.find(' has_comments="') + len(' has_comments="')
        value = h[id_idx:h.find('"', id_idx + 1)]
        return value == 'true'

    @staticmethod
    def extract_sample_url(h: str) -> tuple[str, str]:
        sample_re_res = re_sample_file_link.search(h)
        if sample_re_res is None:
            return '', ''
        file_url = sample_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    def _maxlim_str(self, maxlim: int) -> str:
        return f'&limit={maxlim or self._get_items_per_page():d}'

    def _form_comments_search_address(self, post_id: str) -> str:
        return f'{self._get_sitename()}index.php?page=dapi&s=comment&q=index&post_id={post_id}'

#
#
#########################################
