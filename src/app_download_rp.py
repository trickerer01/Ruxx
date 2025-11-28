# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import base64
import datetime
import re
from multiprocessing.dummy import current_process
from typing import NoReturn, final

from bs4 import BeautifulSoup

from app_defines import (
    FILE_NAME_FULL_MAX_LEN,
    FILE_NAME_PREFIX_RP,
    FMT_DATE,
    ID_VALUE_SEPARATOR_CHAR_RP,
    ITEMS_PER_PAGE_RP,
    MODULE_ABBR_RP,
    SITENAME_B_RP,
    TAGS_CONCAT_CHAR_RP,
    Comment,
    DownloadModes,
    ItemInfo,
)
from app_download import Downloader
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_favorited_by_tag,
    re_item_filename,
    re_item_info_part_xml,
    re_orig_file_link,
    re_sample_file_link,
    re_tags_exclude_rp,
    re_tags_to_process_rp,
)

__all__ = ('DownloaderRp',)

SITENAME = base64.b64decode(SITENAME_B_RP).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RP

MAX_SEARCH_DEPTH = 0

ITEM_INFO_FIELDS = {'file_name': 'ext', 'score': 'score_'}

VALID_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'}
EXT_PET_CONTENT_TYPE = {
    'application/mp4': 'mp4',
    'image/gif': 'gif',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'video/h263': 'mp4',
    'video/h264': 'mp4',
    'video/h265': 'mp4',
    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'video/vp8': 'webm',
    'video/vp9': 'webm',
}


@final
class DownloaderRp(Downloader):
    """
    DownloaderRp
    """
    def __init__(self) -> None:
        super().__init__()
        self._base_cookies = {'ui-tnc-agreed': 'true', 'ui-image-zoom': 'both'}

    def _get_module_specific_default_headers(self) -> dict[str, str]:
        return {}

    def _get_module_specific_default_cookies(self) -> dict[str, str]:
        return self._base_cookies

    def _is_pool_search_conversion_required(self) -> bool:
        return True

    def _is_fav_search_conversion_required(self) -> bool:
        return False

    def _is_fav_search_single_step(self) -> bool:
        return False

    def _supports_native_id_filter(self) -> bool:
        return True

    def _get_id_bounds(self) -> NoReturn:
        raise NotImplementedError

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RP

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RP

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def _form_item_string_manually(self, *ignored) -> NoReturn:
        raise NotImplementedError

    def _is_search_overload_page(self, *ignored) -> bool:
        return False

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}&page={n + 1:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        return raw_html_page.find_all('tag')

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
            # '2017-04-19 16:15:13.053663' -> '19-04-2017'
            date_idx = raw.find(' date="') + len(' date="')
            d = datetime.datetime.strptime(raw[date_idx:raw.find(' ', date_idx + 1)], '%Y-%m-%d')
            return d.strftime(FMT_DATE)
        except Exception:
            thread_exit(f'Unable to extract post date from raw: {raw}', -446)

    def _get_items_query_size_or_html(self, url: str, tries=0) -> int:
        raw_html = self.fetch_html(f'{url}&page=1', tries, do_cache=True)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
        return int(raw_html.find('posts').get('count'))

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
            while '=\'' in item:
                qidx = item.find('=\'') + 1
                qend_idx = item.find('\'', qidx + 1)
                if qend_idx < qidx or (qend_idx < len(item) and item[qend_idx + 1] not in ' >'):
                    break
                oq, dq = "'", '"'
                item = f'{item[:qidx]}"{item[qidx + 1:qend_idx].replace(dq, oq)}"{item[qend_idx + 1:]}'
            for part in re_item_info_part_xml.findall(item):
                name, value = tuple(str(part).split('=', 1))
                name = ITEM_INFO_FIELDS.get(name, name)
                if name == 'ext':  # special case: file_url -> ext -> extract ext
                    value = self.extract_file_url(item)[1]
                if name in item_info.__slots__:
                    while name == 'id' and not value[0].isnumeric():  # id=p1234567
                        value = value[1:]
                    setattr(item_info, name, value.replace('\n', ' ').replace('"', '').strip())
            return item_info
        except Exception:
            self._on_thread_exception(current_process().name)
            raise

    def get_re_tags_to_process(self) -> re.Pattern:
        return re_tags_to_process_rp

    def get_re_tags_to_exclude(self) -> re.Pattern:
        return re_tags_exclude_rp

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RP

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RP

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_extract_item_info_without_fetch(self) -> bool:
        return True

    def _consume_custom_module_tags(self, tags: str) -> str:
        if not tags:
            return tags
        taglist = tags.split(TAGS_CONCAT_CHAR_RP)
        if len(taglist) > 3:
            thread_exit('Fatal: [RP] maximum tags limit exceeded, search results will be undefined!', -706)
        for tidx, tag in enumerate(taglist):
            if re_favorited_by_tag.fullmatch(tag):
                taglist[tidx] = tag.replace('favorited_by', 'upvoted_by')
        return TAGS_CONCAT_CHAR_RP.join(taglist)

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base_s) + len(item_id) + 1 + len(fmt))
        self._download(address, item_id, f'{self.dest_base_s}{self._try_append_extra_info(item_id, hint_maxlen)}.{fmt}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        try:
            h = raw
            item_id = self._extract_id(h)

            if self.dump_comments is True:
                raw_html = self.fetch_html(f'{self._get_sitename()}post/view/{item_id}')
                if raw_html is None:
                    trace(f'ERROR: ProcItem: unable to retreive html for {item_id}!', True)
                    self._inc_proc_count()
                    return
                else:
                    self._extract_comments(raw_html, item_id)

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

    def _form_tags_search_address(self, tags: str, maxlim: int | None = None) -> str:
        return f'{self._get_sitename()}api/danbooru/find_posts?tags={tags}{self._maxlim_str(maxlim)}'

    def _extract_comments(self, raw_html: BeautifulSoup, item_id: str) -> None:
        # no pagination
        full_item_id = f'{self._get_module_abbr_p() if self.add_filename_prefix else ""}{item_id}'
        comment_divs = raw_html.select('div[class="comment"]')
        for comment_div in comment_divs:
            author_a = comment_div.find(class_='username')
            author: str = author_a.text
            body: str = comment_div.find('span', class_='bbcode').text.strip()
            self.item_info_dict_per_task[full_item_id].comments.append(Comment(author, body))

    def extract_file_url(self, h: str) -> tuple[str, str]:
        fullid = f'{self._get_module_abbr_p()}{self._extract_id(h)}'
        if fullid in self._file_name_ext_cache:
            return self._file_name_ext_cache[fullid]
        if file_re_res := re_orig_file_link.search(h):
            file_url = file_re_res.group(1)
            filename_re_res = re_item_filename.search(h)
            filename = filename_re_res.group(1)
            value = filename
            if '.' in value:
                value = value[value.rfind('.') + 1:].strip('."\'\n\\/')
                value = value if value in VALID_EXTENSIONS else ''
            if not 3 <= len(value) <= 4:
                for formatname in VALID_EXTENSIONS:
                    if formatname in value:
                        value = formatname
                        break
            if not 3 <= len(value) <= 4:
                trace(f'Warning (W2): can\'t extract format for {fullid} from filename, fetching content type...', True)
                r = self.wrap_request(file_url, tries=self.retries, method='HEAD')
                if r is not None:
                    content_type = r.headers.get('Content-Type', '')
                    value = EXT_PET_CONTENT_TYPE.get(content_type, value)
                    if len(value) not in (3, 4) and '/' in content_type:
                        value = content_type[content_type.find('/') + 1:]
            if len(value) not in (3, 4):
                trace(f'Warning (W3): unable to retrieve format for {fullid} from url, setting to default...', True)
                value = 'jpg'
            file_ext = value
            self._file_name_ext_cache[fullid] = (file_url, file_ext)
        else:
            file_url = file_ext = ''
        return file_url, file_ext

    @staticmethod
    def extract_sample_url(h: str) -> tuple[str, str]:
        if sample_re_res := re_sample_file_link.search(h):
            file_url = sample_re_res.group(1)
            filename_re_res = re_item_filename.search(h)
            filename = filename_re_res.group(1)
            file_ext = filename[filename.rfind('.') + 1:]
        else:
            file_url = file_ext = ''
        return file_url, file_ext

    def _maxlim_str(self, maxlim: int) -> str:
        return f'&limit={maxlim or self._get_items_per_page():d}'

#
#
#########################################
