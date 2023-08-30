# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from base64 import b64decode
from typing import Tuple, Optional, Pattern, Union

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import (
    SITENAME_B_RS, FILE_NAME_PREFIX_RS, MODULE_ABBR_RS, FILE_NAME_FULL_MAX_LEN, ITEMS_PER_PAGE_RS, DownloadModes, ItemInfo,
    TAGS_CONCAT_CHAR_RS, ID_VALUE_SEPARATOR_CHAR_RS, DATE_MIN_DEFAULT
)
from app_download import DownloaderBase
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_tags_to_process_rs, re_tags_exclude_rs, re_post_style_rs, re_post_dims_rs, re_tag_video_rs

)

__all__ = ('DownloaderRs',)

SITENAME = b64decode(SITENAME_B_RS).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RS
MAX_SEARCH_DEPTH = 240 * ITEMS_PER_PAGE - 1  # set by site devs


class DownloaderRs(DownloaderBase):
    """
    DownloaderRs
    """
    def __init__(self) -> None:
        super().__init__()

    def ___this_class_has_virtual_methods___(self) -> None:
        return

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RS

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RS

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
        return f'{self.url}&page={n:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        return raw_html_page.find_all('div', style=re_post_style_rs)

    def _local_addr_from_string(self, h: str) -> str:
        return self.extract_local_addr(h)

    def _extract_id(self, addr: str) -> str:
        h = addr[addr.find('id=') + len('id='):]
        return h

    def _is_video(self, h: str) -> bool:
        # relying on tags for now
        idx1 = h.find('title=') + len('title=') + 1
        taglist = h[idx1:h.find('/>', idx1 + 1) - 1].strip(', ').split(', ')
        for tag in taglist:
            if re_tag_video_rs.fullmatch(tag):
                return True

    def _get_item_html(self, h: str) -> Optional[BeautifulSoup]:
        return self.fetch_html(h, do_cache=True)

    def _extract_post_date(self, raw: str) -> str:
        return DATE_MIN_DEFAULT

    def get_items_query_size_or_html(self, url: str, tries: int = None) -> Union[int, BeautifulSoup]:
        raw_html = self.fetch_html(f'{url}&page=0', tries, do_cache=True)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
        last = 1
        from re import compile as re_compile
        last_page_buttons = raw_html.find_all('a', href=re_compile(r'^\?r=posts/index&.+?$'))
        for but in last_page_buttons:
            href = str(but.get('href', '=0'))
            last = max(last, 1 + int(href[href.rfind('=') + 1:]))

        if last > self._get_max_search_depth() // self._get_items_per_page():
            trace('Error: items count got past search depth!')
            return last * self._get_items_per_page()
        elif last > 1:
            raw_html = self.fetch_html(f'{url}&page={last - 1:d}', do_cache=True)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-445)

        # items count on all full pages plus items count on last page
        last_thumbs = len(self._get_all_post_tags(raw_html))
        count = (last - 1) * self._get_items_per_page() + last_thumbs  # type: Union[int, BeautifulSoup]
        return count

    def _get_image_address(self, h: str) -> Tuple[str, str]:
        try:
            return h, h[h.rfind('.'):]
        except Exception:
            trace(f'FATAL: GetPicAddr could not find anything!\n\nTag:\n\n{h}', True)
            assert False

    def _get_video_address(self, h: str) -> Tuple[str, str]:
        try:
            return h, h[h.rfind('.'):]
        except Exception:
            trace(f'FATAL: GetVidAddr could not find anything!\n\nTag:\n\n{h}', True)
            assert False

    # __slots__ = ('id', 'height', 'width', 'tags', 'ext', 'source', 'score', 'has_children', 'parent_id')
    def _extract_item_info(self, item: str) -> ItemInfo:
        item_info = ItemInfo()
        addr = self.extract_local_addr(item)
        item_id = self._extract_id(addr)
        raw_html = self.fetch_html(addr, do_cache=True)
        if raw_html is None:
            trace(f'Warning (W2): Item info was not extracted for {item_id}')
            return item_info
        item_info.id = item_id
        keywords_meta = raw_html.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            tags_list = str(keywords_meta.get('content')).strip(', ').split(', ')
            item_info.tags = ' '.join(tag.replace(' ', '_') for tag in tags_list)
        orig_href = self._extract_orig_link(raw_html)
        ext = orig_href[orig_href.rfind('.'):] if orig_href else ''
        item_info.ext = ext[1:]
        lis = raw_html.find_all('li', class_='general-tag', style='display: block; padding: 5px;')
        for li in lis:
            li_str = li.text  # type: str
            if li_str.startswith('Size:'):
                dims = re_post_dims_rs.search(li_str)
                if dims:
                    w, h = tuple(dims.groups())
                    item_info.height = h
                    item_info.width = w
            elif li_str.startswith('Score:'):
                # score_span = raw_html.find('span', id=f'psc{item_id}')
                score_span = li.find('span')
                if score_span:
                    item_info.score = score_span.text

        return item_info

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_rs

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_rs

    def get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RS

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RS

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_etract_item_info_without_fetch(self) -> bool:
        return False

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base) + len(item_id) + len(fmt))
        self._download(address, item_id, f'{self.dest_base}{self._try_append_extra_info(item_id, hint_maxlen)}{fmt}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        h = self.extract_local_addr(raw)
        item_id = self._extract_id(h)

        if self.download_mode == DownloadModes.DOWNLOAD_SKIP:
            self._inc_proc_count()
            return

        raw_html = self.fetch_html(h)
        if raw_html is None:
            trace(f'ERROR: ProcItem: unable to retreive html for {item_id}!', True)
            self._inc_proc_count()
            return

        if self.add_filename_prefix is True:
            item_id = f'{self._get_module_abbr_p()}{item_id}'

        orig_href = self._extract_orig_link(raw_html)

        if orig_href:
            if self._is_video(raw):
                self._process_image(orig_href, item_id)
            else:
                self._process_video(orig_href, item_id)
        else:
            trace(f'Warning (W2): ProcItem: no content for {item_id}, seems like post was deleted', True)

        self._inc_proc_count()

    def form_tags_search_address(self, tags: str, *ignored) -> str:
        return f'{self._get_sitename()}index.php?r=posts/index&q={tags}'

    @staticmethod
    def extract_local_addr(raw: str) -> str:
        idx1 = raw.find('href="') + len('href="')
        h = raw[idx1:raw.find('"', idx1 + 1)]
        return h.replace('&amp;', '&')

    @staticmethod
    def _extract_orig_link(raw_html: BeautifulSoup) -> str:
        content_div = raw_html.find('div', class_='content_push')
        link_img = content_div.find('img') if content_div else None
        link_mp4 = content_div.find('source', type='video/mp4') if content_div else None
        link_wbm = content_div.find('source', type='video/webm') if content_div else None
        link = link_mp4 or link_wbm or link_img
        orig_href = str(link.get('src')) if link else ''
        return orig_href

#
#
#########################################
