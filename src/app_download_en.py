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
from json import loads
from multiprocessing.dummy import current_process
from collections.abc import MutableSet
from re import Pattern
from time import sleep as thread_sleep

# requirements
from bs4 import BeautifulSoup

# internal
from app_debug import __RUXX_DEBUG__
from app_defines import (
    DownloadModes, ItemInfo, Comment, SITENAME_B_EN, FILE_NAME_PREFIX_EN, MODULE_ABBR_EN, FILE_NAME_FULL_MAX_LEN, ITEMS_PER_PAGE_EN,
    TAGS_CONCAT_CHAR_EN, ID_VALUE_SEPARATOR_CHAR_EN, FMT_DATE,
)
from app_download import Downloader
from app_help import APP_ADDRESS
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_tags_to_process_en, re_tags_exclude_en, re_item_info_part_xml, re_orig_file_link, re_sample_file_link, re_favorited_by_tag,

)
from app_revision import APP_VERSION
from app_utils import format_score

__all__ = ('DownloaderEn',)

SITENAME = b64decode(SITENAME_B_EN).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_EN
MAX_SEARCH_DEPTH_PAGES = 750
MAX_SEARCH_DEPTH = MAX_SEARCH_DEPTH_PAGES * ITEMS_PER_PAGE  # set by site devs

item_info_fields = {'file_url': 'ext', 'post_id': 'id'}
tag_blacklisted_always = 'en_always_blacklisted'


class DownloaderEn(Downloader):
    """
    DownloaderEn
    """
    def __init__(self) -> None:
        super().__init__()
        self._base_headers = {'User-Agent': f'Ruxx/{APP_VERSION} <{APP_ADDRESS}>'}
        self._base_cookies = dict()

    def _get_module_specific_default_headers(self) -> dict[str, str]:
        return self._base_headers

    def _get_module_specific_default_cookies(self) -> dict[str, str]:
        return self._base_cookies

    def _is_pool_search_conversion_required(self) -> bool:
        return False

    def _is_fav_search_conversion_required(self) -> bool:
        return False

    def _is_fav_search_single_step(self) -> bool:
        return True

    def _supports_native_id_filter(self) -> bool:
        return True

    def _get_id_bounds(self) -> tuple[int, int]:
        raise NotImplementedError

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_EN

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_EN

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def _form_item_string_manually(self, *ignored) -> str:
        raise NotImplementedError

    def _is_search_overload_page(self, raw_html_page: BeautifulSoup) -> bool:
        # <h1>Search is overloaded! Try again later...</h1>
        search_err = raw_html_page.find_all('h1', string='Search is overloaded! Try again later...')
        return len(search_err) > 0

    def _form_page_num_address(self, n: int) -> str:
        return f'{self.url}&page={n + 1:d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        base_json = loads(raw_html_page.text)
        posts = list()
        for p in base_json['posts']:
            post_tags_list = list()
            post_id = str(p['id'])
            pfile = p['file'] or p['sample']['alternates'].get('original')
            assert pfile
            try:
                post_furl = (pfile['url'] if 'url' in pfile else
                             str((next(filter(None, pfile['urls'])) or p['file']['url']) if 'urls' in pfile else None))
                assert post_furl
            except (StopIteration, AssertionError):
                post_tags_list.append(tag_blacklisted_always)
                post_furl = f'{SITENAME}help/blacklist#default'
            post_surl = str(p['sample']['url'] or post_furl)
            post_fheight = str(pfile['height'])
            post_fwidth = str(pfile['width'])
            [post_tags_list.extend(li) for li in p['tags'].values()]
            post_tags = ' '.join(post_tags_list).replace('"', '\'')
            post_source = ' '.join(p['sources'])
            post_score = str(p['score']['total'])
            post_haschildren = str(p['relationships']['has_children']).lower()
            post_parent_id = str(p['relationships']['parent_id'] or '')
            post_fdate = str(p['created_at'] or '2024-01-01T09:28:22.753-04:00')
            post_comment_count = str(p['comment_count'] or 0)
            post_str = (
                f'<post_id="{post_id}" height="{post_fheight}" width="{post_fwidth}" file_url="{post_furl}" sample_url="{post_surl}" '
                f'created_at="{post_fdate}" score="{post_score}" has_children="{post_haschildren}" parent_id="{post_parent_id}" '
                f'comment_count="{post_comment_count}" source="{post_source}" tags="{post_tags}">'
            )
            posts.append(post_str)
        return posts

    def _local_addr_from_string(self, h: str) -> str:
        return h

    def _extract_id(self, addr: str) -> str:
        id_idx = addr.find('post_id="') + len('post_id="')
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
            d = datetime.fromisoformat(raw[date_idx:raw.find('"', date_idx + 1)])
            return d.strftime(FMT_DATE)
        except Exception:
            thread_exit(f'Unable to extract post date from raw: {raw}', -446)

    def _get_items_query_size_or_html(self, url: str, tries: int = None) -> int:
        page = 0
        raw_html = self.fetch_html(self._form_page_num_address(page), tries, do_cache=True)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)
        last_count = len(loads(raw_html.text)['posts'])
        if last_count >= self._get_items_per_page() and not self.get_max_id:
            trace(f'[{self._get_module_abbr().upper()}] Looking for max page...')
            divider = 1
            direction = 1
            while last_count == 0 or last_count >= self._get_items_per_page():
                if (page == MAX_SEARCH_DEPTH_PAGES - 1 and last_count == self._get_items_per_page()) or (page == 0 and last_count == 0):
                    break
                thread_sleep(1.0)
                page += min(MAX_SEARCH_DEPTH_PAGES - 1, max(MAX_SEARCH_DEPTH_PAGES // divider, 1)) * direction
                if __RUXX_DEBUG__:
                    trace(f'page {page + 1:d}...')
                raw_html = self.fetch_html(self._form_page_num_address(page), do_cache=True)
                if raw_html is None:
                    thread_exit(f'ERROR: GetItemsQueSize: unable to retreive html (page {page:d})', code=-445)
                last_count = len(loads(raw_html.text)['posts'])
                divider *= 2
                direction = -1 if last_count == 0 else 1
        return page * self._get_items_per_page() + last_count

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
            self._on_thread_exception(current_process().getName())
            raise

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_en

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_en

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_EN

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_EN

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_extract_item_info_without_fetch(self) -> bool:
        return True

    def _consume_custom_module_tags(self, tags: str) -> str:
        if not tags:
            return tags
        taglist = tags.split(TAGS_CONCAT_CHAR_EN)
        if len(taglist) > 40:
            thread_exit('Fatal: [EN] maximum tags limit exceeded, search results will be undefined!', -706)
        for tidx, tag in enumerate(taglist):
            if re_favorited_by_tag.fullmatch(tag):
                taglist[tidx] = tag.replace('favorited_by', 'favoritedby')
        return TAGS_CONCAT_CHAR_EN.join(taglist)

    def _send_to_download(self, raw: str, item_id: str, is_video: bool) -> None:
        address, fmt = self._get_video_address(raw) if is_video else self._get_image_address(raw)
        hint_maxlen = FILE_NAME_FULL_MAX_LEN - (len(self.dest_base) + len(item_id) + 1 + len(fmt))
        self._download(address, item_id, f'{self.dest_base}{self._try_append_extra_info(item_id, hint_maxlen)}.{fmt}')

    # threaded
    def _process_item(self, raw: str) -> None:
        if self.is_killed():
            return

        try:
            h = raw
            item_id = self._extract_id(h)

            if self.dump_comments is True and self.extract_comment_count(h) > 0:
                raw_html = self.fetch_html(self._form_comments_search_address(item_id))
                if raw_html is None:
                    trace(f'Warning (W3): ProcItem: unable to retreive comments for {item_id}!', True)
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
            self._on_thread_exception(current_process().getName())
            raise

    def _form_tags_search_address(self, tags: str, maxlim: int = None) -> str:
        return f'{self._get_sitename()}posts.json?tags={tags}{self._maxlim_str(maxlim)}'

    def _extract_comments(self, raw_html: BeautifulSoup, item_id: str) -> None:
        full_item_id = f'{self._get_module_abbr_p() if self.add_filename_prefix else ""}{item_id}'
        comments_json = loads(raw_html.text)
        if not isinstance(comments_json, list):
            return
        for comment in comments_json:
            author = comment['creator_name']
            body = f'{comment["body"]}\n{format_score(str(comment["score"]))}'
            self.item_info_dict_per_task[full_item_id].comments.append(Comment(author, body))

    @staticmethod
    def extract_comment_count(h: str) -> int:
        c_idx = h.find(' comment_count="') + len(' comment_count="')
        count_str = h[c_idx:h.find('"', c_idx + 1)]
        assert count_str.isnumeric()
        return int(count_str)

    @staticmethod
    def extract_file_url(h: str) -> tuple[str, str]:
        file_re_res = re_orig_file_link.search(h)
        if file_re_res is None:
            return '', ''
        file_url = file_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    @staticmethod
    def extract_sample_url(h: str) -> tuple[str, str]:
        sample_re_res = re_sample_file_link.search(h)
        if sample_re_res is None:
            return '', ''
        file_url = sample_re_res.group(1)
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    def _maxlim_str(self, maxlim: int) -> str:
        return f'+limit:{maxlim or self._get_items_per_page():d}'

    def _form_comments_search_address(self, post_id: str) -> str:
        return (f'{self._get_sitename()}comments.json?commit=Search&group_by=comment&search[order]=id_asc'
                f'&search[post_tags_match]=id:{post_id}&limit={self._get_items_per_page():d}')

    def _execute_module_filters(self, parents: MutableSet[str]) -> None:
        abbrp = self._get_module_abbr_p()
        total_count_old = len(self.items_raw_per_task)
        removed_count = 0
        removed_messages: list[str] = list()
        idx: int
        for idx in reversed(range(total_count_old)):
            self.catch_cancel_or_ctrl_c()
            h = self.items_raw_per_task[idx]
            item_id = self._extract_id(h)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_id}'
            item_info = self.item_info_dict_per_task.get(idstring)
            if tag_blacklisted_always in item_info.tags:
                removed_messages.append(f'{abbrp}{item_id} is \'young -rating:s\' and is always blacklisted unless you log in, skipped!')
                if item_id in parents:
                    parents.remove(item_id)
                if item_info.parent_id in parents:
                    parents.remove(item_info.parent_id)
                del self.item_info_dict_per_task[idstring]
                del self.items_raw_per_task[idx]
                self.filtered_out_ids_cache.add(idstring)
                removed_count += 1
        if removed_count > 0:
            trace('\n'.join(removed_messages))
            trace(f'Filtered out {removed_count:d} / {total_count_old:d} items!')

#
#
#########################################
