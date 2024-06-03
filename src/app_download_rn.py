# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from base64 import b64decode
from datetime import datetime
from typing import Tuple, Optional, Pattern, Union

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import (
    DownloadModes, ItemInfo, Comment, SITENAME_B_RN, FILE_NAME_PREFIX_RN, MODULE_ABBR_RN, FILE_NAME_FULL_MAX_LEN, ITEMS_PER_PAGE_RN,
    TAGS_CONCAT_CHAR_RN, ID_VALUE_SEPARATOR_CHAR_RN, FMT_DATE,
)
from app_download import Downloader
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_tags_to_process_rn, re_tags_exclude_rn, re_item_info_part_rn, re_shimmie_image_href, re_shimmie_thumb, re_shimmie_orig_source,
    re_shimmie_image_href_full
)

__all__ = ('DownloaderRn',)

SITENAME = b64decode(SITENAME_B_RN).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RN

MAX_SEARCH_DEPTH = 0

item_info_fields = {'data-post-id': 'id', 'data-tags': 'tags', 'title': 'ext'}


class DownloaderRn(Downloader):
    """
    DownloaderRn
    """
    def __init__(self) -> None:
        super().__init__()

    def _is_fav_search_conversion_required(self) -> bool:
        return False

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RN

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RN

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def _form_item_string_manually(self, raw_html_page: BeautifulSoup) -> str:
        assert isinstance(raw_html_page, BeautifulSoup)
        # extract id
        iid_url = str(raw_html_page.find('a', attrs={'download': '', 'href': re_shimmie_image_href_full}))
        try:
            iall = re_shimmie_image_href_full.search(iid_url)
            iid = iall.group(1)
            itagsext = iall.group(2)
            itags = ' '.join(itagsext[:itagsext.rfind('.')].split('%20'))
            iext = itagsext[itagsext.rfind('.') + 1:]
        except Exception:
            trace('ERROR: re fails while forming item id string')
            raise ValueError
        # form string
        return f'<a data-post-id="{iid}" href="/post/view/{iid}" data-tags="{itags.lower()}" title="{itags} {iext}"> '

    def _is_search_overload_page(self, *ignored) -> bool:
        return False

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}{n + 1:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        return raw_html_page.find_all('a', class_=re_shimmie_thumb)

    def _local_addr_from_string(self, h: str) -> str:
        return self.extract_local_addr(h)

    def _extract_id(self, addr: str) -> str:
        idx1 = addr.find('view/') + len('view/')
        idx2 = addr.find('"', idx1 + 1)
        h = addr[idx1:idx2 if idx2 > idx1 else None]
        return h

    def _is_video(self, h: str) -> bool:
        # tags are not 100% accurate so use a more direct approach
        return 'mp4' in h or 'webm' in h or 'swf' in h

    def _get_item_html(self, h: str) -> Optional[BeautifulSoup]:
        return self.fetch_html(f'{self._get_sitename()}{h}')

    def _extract_post_date(self, raw_html: BeautifulSoup) -> str:
        try:
            # '2017-04-19T11:55:45+00:00' -> '19-04-2017'
            d_raw = raw_html.find('time').get('datetime')
            d = datetime.fromisoformat(d_raw)
            return d.strftime(FMT_DATE)
        except Exception:
            thread_exit(f'Unable to extract post date from raw: {str(raw_html)}', -446)

    def _get_items_query_size_or_html(self, url: str, tries=0) -> Union[int, BeautifulSoup]:
        raw_html = self.fetch_html(f'{url}{1:d}', tries, do_cache=True)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
        last = 1
        for but in raw_html.find_all('a', string='Last'):
            b = str(but)
            b = b[:b.rfind('">')]
            last = int(b[b.rfind('/') + 1:])

        if last > 1:
            raw_html = self.fetch_html(f'{url}{last:d}', do_cache=True)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-445)

        # items count on all full pages plus items count on last page
        last_thumbs = len(self._get_all_post_tags(raw_html))
        count: Union[int, BeautifulSoup] = (last - 1) * self._get_items_per_page() + last_thumbs
        if count == 0 and len(raw_html.find_all('a', attrs={'download': '', 'href': re_shimmie_image_href})) > 0:
            count = raw_html

        return count

    def _get_image_address(self, h: str) -> Tuple[str, str]:
        try:
            addr = h[h.find('_images/'):]
            addr = addr[:addr.find('"')]
            fmt = addr[addr.rfind('.'):]
            addr = f'{self._get_sitename()}{addr}'
            return addr, fmt
        except Exception:
            trace(f'FATAL: GetPicAddr could not find anything!\n\nHTML:\n\n{h}', True)
            assert False

    def _get_video_address(self, h: str) -> Tuple[str, str]:
        try:
            addr = h[h.find('_images/'):]
            addr = addr[:addr.find('"')]
            fmt = addr[addr.rfind('.'):]
            addr = f'{self._get_sitename()}{addr}'
            return addr, fmt
        except Exception:
            trace(f'FATAL: GetVidAddr could not find anything!\n\nTag:\n\n{h}', True)
            assert False

    def _extract_item_info(self, item: str) -> ItemInfo:
        item_info = ItemInfo()
        for part in re_item_info_part_rn.findall(item):
            name, value = tuple(str(part).split('=', 1))
            if name == 'id':  # special case id (thumb_...): skip
                continue
            name = item_info_fields.get(name, name)
            if name == 'ext':  # special case: title -> ext -> extract ext
                value = value[value.rfind(' ') + 1:]
            if name in item_info.__slots__:
                item_info.__setattr__(name, value.replace('\n', ' ').replace('"', '').strip())

        return item_info

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_rn

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_rn

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RN

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RN

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_extract_item_info_without_fetch(self) -> bool:
        return True

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

        raw_html = BeautifulSoup()
        if self.download_mode != DownloadModes.SKIP or self.dump_sources is True or self.dump_comments is True:
            raw_html = self.fetch_html(f'{self._get_sitename()}{h}')
            if raw_html is None:
                trace(f'ERROR: ProcItem: unable to retreive html for {item_id}!', True)
                self._inc_proc_count()
                return
            else:
                self._extract_comments(raw_html, item_id)
                full_item_id = f'{self._get_module_abbr_p()}{item_id}'
                orig_source_div = raw_html.find('div', style=re_shimmie_orig_source)
                if orig_source_div:
                    self.item_info_dict_per_task[full_item_id].source = orig_source_div.text
                # we can't extract actual score without account credentials AND cf_clearance, but favorites will do just fine
                favorited_by_div = raw_html.find('h3', string='Favorited By')
                if favorited_by_div:
                    fav_sib = favorited_by_div.findNextSibling()
                    score_text = fav_sib.text[:max(fav_sib.text.find(' '), 0)]
                    self.item_info_dict_per_task[full_item_id].score = score_text

        if self.download_mode == DownloadModes.SKIP:
            self._inc_proc_count()
            return

        img_items = raw_html.find_all('img', id='main_image')
        mp4_items = raw_html.find_all('source', type='video/mp4')
        webm_items = raw_html.find_all('source', type='video/webm')
        swf_items = raw_html.find_all('embed', type='application/x-shockwave-flash')

        imgs = len(img_items) != 0
        mp4s = len(mp4_items) != 0
        wbms = len(webm_items) != 0
        swfs = len(swf_items) != 0

        if self.add_filename_prefix is True:
            item_id = f'{self._get_module_abbr_p()}{item_id}'

        if imgs or mp4s or wbms or swfs:
            if len(img_items) > 1:
                trace(f'Warning (W1): ProcItem: more than 1 pic for {item_id}', True)
            if len(mp4_items) > 1 or len(webm_items) > 1:
                trace(f'Warning (W1): ProcItem: more than 1 vid for {item_id}', True)

            if imgs:
                self._process_image(str(img_items[0]), item_id)
            else:
                vsrc = swf_items if not (wbms or mp4s) else webm_items if (self.prefer_webm and wbms) or not mp4s else mp4_items
                self._process_video(str(vsrc[0]), item_id)
        else:
            trace(f'Warning (W2): ProcItem: no content for {item_id}, seems like post was deleted', True)

        self._inc_proc_count()

    def _form_tags_search_address(self, tags: str, *ignored) -> str:
        return f'{self._get_sitename()}post/list/{tags}{self._get_tags_concat_char()}order%253Did_desc/'

    def _extract_comments(self, raw_html: BeautifulSoup, item_id: str) -> None:
        # no pagination
        full_item_id = f'{self._get_module_abbr_p()}{item_id}'
        comment_divs = raw_html.select('div[class="comment"]')
        for comment_div in comment_divs:
            author_a = comment_div.find('a', class_='username')
            author: str = author_a.text
            body: str = comment_div.text.strip()
            body = body[body.find(f'{author}: ') + len(f'{author}: '):]
            self.item_info_dict_per_task[full_item_id].comments.append(Comment(author, body))

    @staticmethod
    def extract_local_addr(raw: str) -> str:
        h = raw[raw.find('href="') + len('href="') + 1:]
        h = h[:h.find('"')]
        return h

#
#
#########################################
