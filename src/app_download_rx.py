# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from base64 import b64decode
from re import compile as re_compile
from typing import Tuple, Optional, Pattern

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import (
    SITENAME_B_RX, FILE_NAME_PREFIX_RX, MODULE_ABBR_RX, FILE_NAME_FULL_MAX_LEN, ITEMS_PER_PAGE_RX, DownloadModes, ItemInfo,
    TAGS_CONCAT_CHAR_RX, ID_VALUE_SEPARATOR_CHAR_RX
)
from app_download import DownloaderBase
from app_logger import trace
from app_network import thread_exit
from app_re import re_tags_to_process_rx, re_tags_exclude_rx

__all__ = ('DownloaderRx',)

SITENAME = b64decode(SITENAME_B_RX).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RX
MAX_SEARCH_DEPTH = 200000 + ITEMS_PER_PAGE - 1  # set by site devs

re_item_info_part_rx = re_compile(r'([\w5_]+=\"[^"]+\")[> ]')
re_post_date_rx = re_compile(r'^\w{3} (\w{3}) (\d\d) \d{2}:\d{2}:\d{2} \+\d{4} (\d{4})$')
re_orig_file_link = re_compile(r'file_url=\"([^"]+)\"')
re_sample_file_link = re_compile(r'file_url=\"([^"]+)\"')


class DownloaderRx(DownloaderBase):
    """
    DownloaderRx
    """
    def __init__(self) -> None:
        super().__init__()

    def ___this_class_has_virtual_methods___(self) -> None:
        return

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RX

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RX

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def _form_item_string_manually(self, *ignored) -> None:
        raise NotImplementedError

    def _is_search_overload_page(self, raw_html_page: BeautifulSoup) -> bool:
        # <h1>Search is overloaded! Try again later...</h1>
        search_err = raw_html_page.find_all('h1', string='Search is overloaded! Try again later...')
        return len(search_err) > 0

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}&pid={n:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        return raw_html_page.find_all('post')

    def _local_addr_from_string(self, h: str) -> str:
        return h

    def _extract_id(self, addr: str) -> str:
        h = addr[addr.find(' id="') + len(' id="'):]
        h = h[:h.find('"')]
        return h

    def _is_video(self, h: str) -> bool:
        # tags are not 100% accurate so use a more direct approach
        _, file_ext = self.extract_file_url(h)
        return file_ext in ['mp4', 'webm']

    def _get_item_html(self, h: str) -> str:
        return h

    def _extract_post_date(self, raw: str) -> str:
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
            'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }

        d_raw = raw[raw.find('created_at="') + len('created_at="'):]
        d_raw = d_raw[:d_raw.find('"')]
        # Mon Jan 06 21:51:58 +0000 2020
        d_re_res = re_post_date_rx.search(d_raw)
        if not d_re_res:
            thread_exit(f'Unable to extract post date from raw: {raw}', -446)

        # '2020-01-06'
        d = f'{d_re_res.group(3)}-{months.get(d_re_res.group(1))}-{d_re_res.group(2)}'
        return d

    def get_items_query_size_or_html(self, url: str, tries: Optional[int] = None) -> int:
        raw_html = self.fetch_html(f'{url}&pid=0', tries)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)

        last = 0
        posts_tags = raw_html.find_all('posts')
        if len(posts_tags) != 0:
            b = str(posts_tags[0])
            b = b[b.find('count="') + len('count="'):]
            b = b[:b.find('"')]
            last = int(b)

        return last

    def _get_image_address(self, h: str) -> Tuple[str, str]:
        def hi_res_addr() -> Tuple[str, str]:
            addr, ext = self.extract_file_url(h)
            return addr, ext

        def low_res_addr() -> Tuple[str, str]:
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

    def _get_video_address(self, h: str) -> Tuple[str, str]:
        addr, ext = self.extract_file_url(h)
        if len(addr) == 0:
            addr, ext = self.extract_sample_url(h)

        if len(addr) == 0:
            trace('FATAL: GetVidAddr could not find anything!', True)
            trace(f'\nstring:\n\n{h}', True)
            assert False

        return addr, ext

    def _extract_item_info(self, item: str) -> ItemInfo:
        item_info = ItemInfo()
        all_parts = re_item_info_part_rx.findall(item)
        for part in all_parts:
            name, value = tuple(str(part).split('=', 1))
            # special case: file_url -> extract ext
            if name == 'file_url':
                name = 'ext'
                value = value[value.rfind('.') + 1:]
            # special case: source -> omit unknowns
            # if name == 'source' and len(value) < 2:
            #     value = 'Unknown'
            if name in item_info.__slots__:
                item_info.__setattr__(name, value.replace('\n', ' ').replace('"', '').strip())

        return item_info

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_rx

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_rx

    def get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RX

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RX

    def _split_or_group_into_tasks_always(self) -> bool:
        return False

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base) + len(item_id) + 1 + len(fmt))
        self._download(address, item_id, f'{self.dest_base}{self._try_append_extra_info(item_id, hint_maxlen)}.{fmt}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        h = raw
        item_id = self._extract_id(h)

        if self.download_mode == DownloadModes.DOWNLOAD_SKIP:
            self._inc_proc_count()
            return

        orig_item = re_orig_file_link.search(h)

        if self.add_filename_prefix is True:
            item_id = f'{FILE_NAME_PREFIX_RX}{item_id}'

        if orig_item:
            if len(orig_item.groupdict()) > 1:
                trace(f'Warning (W1): ProcItem: more than 1 items for {item_id}', True)

            is_vid = self._is_video(h)
            if is_vid:
                self._process_video(h, item_id)
            else:
                self._process_image(h, item_id)
        else:
            trace(f'Warning (W2): unable to extract file url from {h}, deleted?', True)

        self._inc_proc_count()

    def form_tags_search_address(self, tags: str, maxlim: Optional[int] = None) -> str:
        return f'{self._get_sitename()}index.php?page=dapi&s=post&q=index&tags={tags}{self.maxlim_str(maxlim)}'

    @staticmethod
    def extract_file_url(h: str) -> Tuple[str, str]:
        file_re_res = re_orig_file_link.search(h)
        if file_re_res is None:
            return '', ''
        file_url = file_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    @staticmethod
    def extract_sample_url(h: str) -> Tuple[str, str]:
        sample_re_res = re_sample_file_link.search(h)
        if sample_re_res is None:
            return '', ''
        file_url = sample_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    def maxlim_str(self, maxlim: int) -> str:
        return f'&limit={maxlim or self._get_items_per_page():d}'


DownloaderType = DownloaderRx

#
#
#########################################
