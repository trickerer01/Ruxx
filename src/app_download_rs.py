# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import base64
import re
from multiprocessing.dummy import current_process
from typing import final

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import (
    DATE_MIN_DEFAULT,
    FILE_NAME_FULL_MAX_LEN,
    FILE_NAME_PREFIX_RS,
    ID_VALUE_SEPARATOR_CHAR_RS,
    ITEMS_PER_PAGE_RS,
    MODULE_ABBR_RS,
    SITENAME_B_RS,
    TAGS_CONCAT_CHAR_RS,
    Comment,
    DownloadModes,
    ItemInfo,
)
from app_download import Downloader
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_comment_a_rs,
    re_comment_page_rs,
    re_post_dims_rs,
    re_post_page_rs,
    re_post_style_rs,
    re_tag_video_rs,
    re_tags_exclude_rs,
    re_tags_to_process_rs,
)

__all__ = ('DownloaderRs',)

SITENAME = base64.b64decode(SITENAME_B_RS).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RS
ITEMS_PER_PAGE_F = 30
MAX_SEARCH_DEPTH = 240 * ITEMS_PER_PAGE - 1  # set by site devs


@final
class DownloaderRs(Downloader):
    """
    DownloaderRs
    """
    def __init__(self) -> None:
        super().__init__()

    def _get_api_key(self) -> str:
        return ''

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

    def _get_id_bounds(self) -> tuple[int, int]:
        raise NotImplementedError

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RS

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RS

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE_F if self.favorites_search_user else ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def _form_item_string_manually(self, *ignored) -> str:
        raise NotImplementedError

    def _is_search_overload_page(self, raw_html_page: BeautifulSoup) -> bool:
        # <h1>Search is overloaded! Try again later...</h1>
        search_err = raw_html_page.find_all('h1', string='Search is overloaded! Try again later...')
        return len(search_err) > 0

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}&page={n:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        if self.favorites_search_user:
            divs = raw_html_page.find_all('div', class_='thumbnail-preview')
            for div in divs:
                tag_a = div.find('a')
                tag_a['href'] = f"{self._get_sitename()}{tag_a['href']}"
            return divs
        else:
            return raw_html_page.find_all('div', style=re_post_style_rs)

    def _local_addr_from_string(self, h: str) -> str:
        return self.extract_local_addr(h)

    def _extract_id(self, addr: str) -> str:
        idx1 = addr.find('id=') + len('id=')
        idx2 = addr.find('"', idx1 + 1)
        return addr[idx1:idx2 if idx2 > idx1 else None]

    def _is_video(self, h: str) -> bool:
        # relying on tags for now TODO
        idx1 = h.find('title=') + len('title=') + 1
        taglist = h[idx1:h.find('/>', idx1 + 1) - 1].strip(', ').split(', ')
        return any(re_tag_video_rs.fullmatch(tag) for tag in taglist)

    def _get_item_html(self, h: str) -> BeautifulSoup | None:
        return self.fetch_html(h, do_cache=True)

    def _extract_post_date(self, raw: str) -> str:
        return DATE_MIN_DEFAULT

    def _get_items_query_size_or_html(self, url: str, tries: int | None = None) -> int:
        raw_html = self.fetch_html(f'{url}&page=0', tries, do_cache=True)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
        last = 1
        last_page_buttons = raw_html.find_all('a', href=re_post_page_rs)
        for but in last_page_buttons:
            href = str(but.get('href', '=0'))
            last = max(last, 1 + int(href[href.rfind('=') + 1:]))

        if last > self._get_max_search_depth() // self._get_items_per_page():
            if not self.get_max_id:
                trace('Error: items count got past search depth!')
            return last * self._get_items_per_page()
        elif last > 1:
            raw_html = self.fetch_html(f'{url}&page={last - 1:d}', do_cache=True)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-445)

        # items count on all full pages plus items count on last page
        last_thumbs = len(self._get_all_post_tags(raw_html))
        return (last - 1) * self._get_items_per_page() + last_thumbs

    def _get_image_address(self, h: str) -> tuple[str, str]:
        try:
            return h, h[h.rfind('.'):]
        except Exception:
            trace(f'FATAL: GetPicAddr could not find anything!\n\nTag:\n\n{h}', True)
            assert False

    def _get_video_address(self, h: str) -> tuple[str, str]:
        try:
            return h, h[h.rfind('.'):]
        except Exception:
            trace(f'FATAL: GetVidAddr could not find anything!\n\nTag:\n\n{h}', True)
            assert False

    def _extract_item_info(self, item: str) -> ItemInfo:
        try:
            item_info = ItemInfo()
            if self.is_killed():
                return item_info
            addr = self.extract_local_addr(item)
            item_id = self._extract_id(addr)
            item_info.id = item_id
            raw_html = self.fetch_html(addr, do_cache=True)
            if raw_html is None:
                trace(f'Warning (W2): Item info was not extracted for {item_id}')
                return item_info
            if keywords_meta := raw_html.find('meta', attrs={'name': 'keywords'}):
                tags_list = str(keywords_meta.get('content')).strip(', ').split(', ')
                item_info.tags = ' '.join(tag.replace(' ', '_') for tag in tags_list)
            orig_href = self._extract_orig_link(raw_html)
            ext = orig_href[orig_href.rfind('.'):] if orig_href else ''
            item_info.ext = ext[1:]
            lis = raw_html.find_all('li', class_='general-tag', style='display: block; padding: 5px;')
            for li in lis:
                li_str: str = li.text
                if li_str.startswith('Size:'):
                    if dims := re_post_dims_rs.search(li_str):
                        w, h = tuple(dims.groups())
                        item_info.height = h
                        item_info.width = w
                elif li_str.startswith('Score:'):
                    if score_span := li.find('span'):
                        item_info.score = score_span.text
            return item_info
        except Exception:
            self._on_thread_exception(current_process().name)
            raise

    def get_re_tags_to_process(self) -> re.Pattern:
        return re_tags_to_process_rs

    def get_re_tags_to_exclude(self) -> re.Pattern:
        return re_tags_exclude_rs

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RS

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RS

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_extract_item_info_without_fetch(self) -> bool:
        return False

    def _consume_custom_module_tags(self, tags: str) -> str:
        return tags

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base_s) + len(item_id) + len(fmt))
        self._download(address, item_id, f'{self.dest_base_s}{self._try_append_extra_info(item_id, hint_maxlen)}{fmt}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        try:
            h = self.extract_local_addr(raw)
            item_id = self._extract_id(h)

            raw_html = BeautifulSoup()
            if self.download_mode != DownloadModes.SKIP or self.dump_comments is True:
                raw_html = self.fetch_html(h)
                if raw_html is None:
                    trace(f'ERROR: ProcItem: unable to retreive html for {item_id}!', True)
                    self._inc_proc_count()
                    return
                else:
                    self._extract_comments(raw_html, item_id)

            if self.download_mode == DownloadModes.SKIP:
                self._inc_proc_count()
                return

            if self.add_filename_prefix is True:
                item_id = f'{self._get_module_abbr_p()}{item_id}'

            is_vid = self._is_video(raw)
            href = self._extract_sample_link(raw_html) if (self.low_res and not is_vid) else self._extract_orig_link(raw_html)

            if href:
                if is_vid:
                    self._process_video(href, item_id)
                else:
                    self._process_image(href, item_id)
            else:
                trace(f'Warning (W2): ProcItem: no content for {item_id}, seems like post was deleted', True)

            self._inc_proc_count()
        except Exception:
            self._on_thread_exception(current_process().name)
            raise

    def _form_tags_search_address(self, tags: str, *_) -> str:
        return (f'{self._get_sitename()}index.php?r=favorites/view&id={self.favorites_search_user}' if self.favorites_search_user else
                f'{self._get_sitename()}index.php?r=posts/index&q={tags}')

    def _extract_comments(self, raw_html: BeautifulSoup, item_id: str) -> None:
        # find pagination first
        full_item_id = f'{self._get_module_abbr_p() if self.add_filename_prefix else ""}{item_id}'
        comment_page_as = raw_html.find_all('a', href=re_comment_page_rs)
        cpages = max(int(a.text) for a in comment_page_as) if comment_page_as else 1
        for cpage in range(cpages):
            if cpage > 0:
                raw_html = self.fetch_html(self._form_comments_search_address(item_id, cpage))
            comment_divs = raw_html.find_all('div', class_='commentBox')
            for comment_div in comment_divs:
                author_a = comment_div.find('a', href=re_comment_a_rs)
                author: str = author_a.text
                body: str = comment_div.text.strip()
                if '  ' in body:
                    body = body[body.find('  ') + 2:]
                self.item_info_dict_per_task[full_item_id].comments.append(Comment(author, body))

    @staticmethod
    def extract_local_addr(raw: str) -> str:
        idx1 = raw.find('href="') + len('href="')
        h = raw[idx1:raw.find('"', idx1 + 1)]
        return h.replace('&amp;', '&')

    def _extract_orig_link(self, raw_html: BeautifulSoup) -> str:
        content_div = raw_html.find('div', class_='content_push')
        link_img = content_div.find('img') if content_div else None
        link_mp4 = content_div.find('source', type='video/mp4') if content_div else None
        link_wbm = content_div.find('source', type='video/webm') if content_div else None
        link_ori = raw_html.find('a', string='Original')
        link = ((link_wbm or link_mp4) if self.prefer_webm else (link_mp4 or link_wbm) if self.prefer_mp4 else link_ori) or link_img
        return str(link.get('src') or link.get('href')) if link else ''

    def _extract_sample_link(self, raw_html: BeautifulSoup) -> str:
        orig_link = self._extract_orig_link(raw_html)
        link = orig_link.replace('/images/', '/thumbnails/')
        lsd_index = link.rfind('.')
        link = link[:lsd_index] + '.jpg'
        lsl_index = link.rfind('/')
        return link[:lsl_index] + '/thumbnail_' + link[lsl_index + 1:]

    def _form_comments_search_address(self, post_id: str, page_num: int) -> str:
        return f'{self._get_sitename()}index.php?r=posts/view&id={post_id}&page={page_num:d}'

#
#
#########################################
