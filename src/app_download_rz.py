# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from base64 import b64decode
from collections.abc import Iterable, MutableSet, Callable
from datetime import datetime
from json import load, loads
from multiprocessing.dummy import current_process
from re import Pattern

# requirements
from bs4 import BeautifulSoup

# internal
from app_defines import (
    DownloadModes, ItemInfo, UTF8, SITENAME_B_RZ, FILE_NAME_PREFIX_RZ, MODULE_ABBR_RZ, FILE_NAME_FULL_MAX_LEN, ITEMS_PER_PAGE_RZ,
    TAGS_CONCAT_CHAR_RZ, ID_VALUE_SEPARATOR_CHAR_RZ, FILE_LOC_TAGS_RZ, FMT_DATE, SOURCE_DEFAULT, INT_BOUNDS_DEFAULT,
)
from app_download import Downloader
from app_logger import trace
from app_network import thread_exit
from app_re import (
    re_tags_to_process_rz, re_tags_exclude_rz, prepare_regex_fullmatch, re_id_tag_rz, re_score_tag_rz,

)
from app_tagger import is_wtag, normalize_wtag, no_validation_tag
from app_utils import assert_nonempty

__all__ = ('DownloaderRz',)

TAG_NAMES: set[str] = set()
FILE_LOC_TAGS = FILE_LOC_TAGS_RZ

SITENAME = b64decode(SITENAME_B_RZ).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_RZ
MAX_SEARCH_DEPTH = 12000  # 200 pages

item_info_fields = {'likes': 'score', 'comments': 'comments_'}


class DownloaderRz(Downloader):
    """
    DownloaderRz
    """
    def __init__(self) -> None:
        super().__init__()
        self.id_bounds = INT_BOUNDS_DEFAULT
        self.score_bounds = INT_BOUNDS_DEFAULT
        self.positive_tags: list[str] = list()
        self.negative_tags: list[str] = list()
        self.expand_cache: dict[str, list[str]] = dict()

    def _get_module_specific_default_headers(self) -> dict[str, str]:
        return {}

    def _get_module_specific_default_cookies(self) -> dict[str, str]:
        return {}

    def _is_pool_search_conversion_required(self) -> bool:
        return True

    def _is_fav_search_conversion_required(self) -> bool:
        return True

    def _is_fav_search_single_step(self) -> bool:
        return True

    def _supports_native_id_filter(self) -> bool:
        return False

    def _get_id_bounds(self) -> tuple[int, int]:
        return self.id_bounds

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_RZ

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_RZ

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
        return f'{self.url}&Skip={n * self._get_items_per_page():d}'

    def _get_all_post_tags(self, raw_html_page: BeautifulSoup) -> list:
        return self.parse_json(raw_html_page.text)['items']

    def _local_addr_from_string(self, h: str) -> str:
        return h

    def _extract_id(self, addr: str) -> str:
        raw = str(addr)  # not a mistake
        id_idx = raw.find('\'id\': ') + len('\'id\': ')
        return raw[id_idx:raw.find(',', id_idx + 1)]

    def _is_video(self, h: str) -> bool:
        item_json = self.parse_json(h)
        return item_json['type'] == 1

    def _get_item_html(self, h: str) -> str:
        return h

    def _extract_post_date(self, raw: str) -> str:
        try:
            # '2022-09-05T07:03:35.378988' -> '05-09-2022'
            date_idx = raw.find('\'posted\': \'') + len('\'posted\': \'')
            date_raw = raw[date_idx:raw.find('\'', date_idx + 1)]
            while len(date_raw.rsplit('.')[-1]) < 6:
                date_raw += '0'
            d = datetime.fromisoformat(date_raw)
            return d.strftime(FMT_DATE)
        except Exception:
            thread_exit(f'Unable to extract post date from raw: {raw}', -446)

    def _get_items_query_size_or_html(self, url: str, tries: int = None) -> int:
        if self.favorites_search_user and not self.favorites_search_user.isnumeric():  # get to api
            raw_html = self.fetch_html(self.url, tries)
            if raw_html is None:
                thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-447)
            h = str(raw_html)
            user_id_prefix = f'api/user/{self.favorites_search_user}&q;:&q;{{\\&q;id\\&q;:'
            user_id_pos = h.find(user_id_prefix)
            if user_id_pos == -1:
                thread_exit(f'ERROR: GetItemsQueSize: Invalid user name \'{self.favorites_search_user}\'!', code=-449)
            user_id_idx = user_id_pos + len(user_id_prefix)
            user_id = h[user_id_idx:h.find(',', user_id_idx + 1)]
            self.favorites_search_user = user_id
            self.url = self._form_tags_search_address('')
        raw_html = self.fetch_html(self._form_page_num_address(0), tries)
        if raw_html is None:
            thread_exit('ERROR: GetItemsQueSize: unable to retreive html', code=-444)

        return int(self.parse_json(raw_html.text)['totalCount'])

    def _get_image_address(self, h: str) -> tuple[str, str]:
        item_json = self.parse_json(h)
        img_links = sorted(filter(None, [link for link in item_json['imageLinks'] if link['type'] in (3, )]),
                           key=lambda link: link['type'])
        addr, ext = self._extract_file_url(img_links[0])

        def hi_res_addr() -> tuple[str, str]:
            if not addr.endswith(f'pic.{ext}'):
                return addr[:addr.rfind('pic') + len('pic')] + f'.{ext}', ext
            return addr, ext

        def low_res_addr() -> tuple[str, str]:
            if not addr.endswith(f'picsmall.{ext}'):
                return addr[:addr.rfind('pic') + len('pic')] + f'small.{ext}', ext
            return addr, ext

        if self.low_res:
            address, fmt = low_res_addr()
        else:
            address, fmt = hi_res_addr()

        startsym = address[0]
        address = address if startsym == 'h' else f'{self._get_sitename()}{address[1 if startsym == "/" else 0:]}'
        return address, fmt

    def _get_video_address(self, h: str) -> tuple[str, str]:
        item_json = self.parse_json(h)
        video_links = list(filter(None, [link for link in item_json['imageLinks'] if link['type'] in (11,)]))
        addr, ext = self._extract_file_url(video_links[0])
        if not addr.endswith(f'mov.{ext}') and not addr.endswith(f'mov720.{ext}'):
            addr = addr[:addr.rfind('mov') + len('mov')] + f'.{ext}'
        startsym = addr[0]
        addr = addr if startsym == 'h' else f'{self._get_sitename()}{addr[1 if startsym == "/" else 0:]}'
        return addr, ext

    def _extract_item_info(self, item: str) -> ItemInfo:
        try:
            item_info = ItemInfo()
            if self.is_killed():
                return item_info
            item_info.height, item_info.width = '?', '?'
            item_json = self.parse_json(item)
            for name in item_json:
                value = item_json[name]
                name = item_info_fields.get(name, name)
                if name == 'tags':
                    item_info.tags = ' '.join(sorted(t.replace(' ', '_') for t in value))
                elif name == 'sources':
                    if value and len(value) > 0 and value[0]:
                        item_info.source = value[0]
                elif name == 'imageLinks':
                    try:
                        item_info.ext = next(filter(
                            None, [link['url'][link['url'].rfind('.') + 1:] for link in value if link['type'] == 11]))
                    except Exception:
                        item_info.ext = 'mp4' if item_json.get('type', 0) == 1 else 'jpg'
                elif name in item_info.__slots__:
                    item_info.__setattr__(name, str(value).replace('\n', ' ').replace('"', '').strip())
            return item_info
        except Exception:
            self._on_thread_exception(current_process().getName())
            raise

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_rz

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_rz

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_RZ

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_RZ

    def _split_or_group_into_tasks_always(self) -> bool:
        return True

    def _can_extract_item_info_without_fetch(self) -> bool:
        return True

    def _consume_custom_module_tags(self, tags: str) -> str:
        self.negative_tags.clear()
        self.positive_tags.clear()
        self.id_bounds = INT_BOUNDS_DEFAULT
        self.score_bounds = INT_BOUNDS_DEFAULT
        if not tags:
            return tags
        taglist = tags.split(TAGS_CONCAT_CHAR_RZ)
        id_lb = sc_lb = INT_BOUNDS_DEFAULT[0]
        id_ub = sc_ub = INT_BOUNDS_DEFAULT[1]
        idx: int
        for idx in reversed(range(len(taglist))):
            ctag = taglist[idx]
            # ctag = ctag.replace('%2b', '+')
            if ctag.startswith('-'):
                if len(ctag) > 1:
                    self.negative_tags.append(ctag[1:])
                    del taglist[idx]
            else:
                id_match = re_id_tag_rz.fullmatch(ctag)
                score_match = re_score_tag_rz.fullmatch(ctag)
                if id_match:
                    sign = id_match.group(1) or '='  # could be 'id:123', '=' is assumed
                    id_ = int(id_match.group(2))
                    if sign == '=':
                        id_lb = id_ub = id_
                    elif sign == '>':
                        id_lb = id_ + 1
                    elif sign == '>=':
                        id_lb = id_
                    elif sign == '<':
                        id_ub = id_ - 1
                    elif sign == '<=':
                        id_ub = id_
                elif score_match:
                    sign = score_match.group(1) or '='  # could be 'score:123', '=' is assumed
                    score_ = int(score_match.group(2))
                    if sign == '=':
                        sc_lb = sc_ub = score_
                    elif sign == '>':
                        sc_lb = score_ + 1
                    elif sign == '>=':
                        sc_lb = score_
                    elif sign == '<':
                        sc_ub = score_ - 1
                    elif sign == '<=':
                        sc_ub = score_
                else:
                    self.positive_tags.append(ctag)
                del taglist[idx]
        self.score_bounds = (sc_lb, sc_ub)
        self.id_bounds = (id_lb, id_ub)
        if not self.positive_tags and not self.favorites_search_user:
            thread_exit('Fatal: [RZ] no positive non-meta tags found!', -703)
        self._validate_tags(self.positive_tags)
        if len(self.positive_tags) > 3:
            thread_exit('Fatal: [RZ] maximum positive tags limit exceeded, search results will be undefined!', -704)
        self._validate_tags(self.negative_tags, True)
        if len(self.negative_tags) > 3:
            thread_exit('Fatal: [RZ] maximum negative tags limit exceeded, search results will be undefined!', -705)
        for tlist in (self.positive_tags, self.negative_tags):
            for tidx in range(len(tlist)):
                tlist[tidx] = tlist[tidx].replace('_', '%20')
        return TAGS_CONCAT_CHAR_RZ.join(taglist)

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

            if self.dump_comments is True:
                pass

            if self.dump_sources:
                full_item_id = f'{self._get_module_abbr_p() if self.add_filename_prefix else ""}{item_id}'
                if full_item_id not in self.item_info_dict_per_task or self.item_info_dict_per_task[full_item_id].source == SOURCE_DEFAULT:
                    raw_html = self.fetch_html(f'{self._get_sitename()}post/{item_id}')
                    if raw_html is None:
                        trace(f'ERROR: ProcItem: unable to retreive html for {item_id}!', True)
                        self._inc_proc_count()
                        return
                    else:
                        orig_source_div = raw_html.find('div', class_='source')
                        if orig_source_div and orig_source_div.parent:
                            self.item_info_dict_per_task[full_item_id].source = (
                                orig_source_div.parent.find('a', class_='link').get('href', ''))

            if self.download_mode == DownloadModes.SKIP:
                self._inc_proc_count()
                return

            item_json = self.parse_json(raw)
            is_vid = self._is_video(h)
            orig_items = list(filter(None, [link for link in item_json['imageLinks']
                                            if link['type'] in ((10, 11, 12, 40, 41) if is_vid else (2, 3, 4, 5))]))

            if self.add_filename_prefix is True:
                item_id = f'{self._get_module_abbr_p()}{item_id}'

            if orig_items:
                if len(orig_items) > 1:
                    # trace(f'Warning (W1): ProcItem: {len(orig_items):d} items for {item_id}', True)
                    del orig_items[1:]

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
        assert not tags
        maxlimi = self._maxlim_str(maxlim)
        if self.favorites_search_user:
            return (
                f'{self._get_sitename()}api/post/GetUserBookmarks?userId={self.favorites_search_user}{maxlimi}'
                if self.favorites_search_user.isnumeric() else
                f'{self._get_sitename()}u/{self.favorites_search_user}/bookmarks'
            )
        return f'{self._get_sitename()}api/post/search-light?IncludeLinks=true{self._tags_str()}{self._blocked_str()}{maxlimi}'

    @staticmethod
    def parse_json(raw: str) -> dict:
        item_json_base = (
            raw.replace('{"', '{\'').replace('"}', '\'}').replace('["', '[\'').replace('"]', '\']')
               .replace('": ', '\': ').replace(': "', ': \'').replace('", ', '\', ').replace(', "', ', \'')
               .replace('":', '\':').replace(':"', ':\'').replace('",', '\',').replace(',"', ',\'')
               .replace('\\', '/').replace('"', '\'')
               .replace('{\'', '{"').replace('\'}', '"}').replace('[\'', '["').replace('\']', '"]')
               .replace('\': ', '": ').replace(': \'', ': "').replace('\', ', '", ').replace(', \'', ', "')
               .replace('\':', '":').replace(':\'', ':"').replace('\',', '",').replace(',\'', ',"')
               .replace(': None,', ': "None",').replace(', ":"', ', ":\'').replace(',":"', ',":\'')
        )
        try:
            parsed_json = loads(item_json_base)
        except Exception:
            import traceback
            trace(traceback.format_exc())
            thread_exit(f'Unable to parse json:\nraw:\n{raw}\nbase:\n{item_json_base}')
            assert False
        return parsed_json

    @staticmethod
    def _extract_file_url(h: dict) -> tuple[str, str]:
        file_url = h['url'][1:] if h['url'].startswith('/') else h['url']
        file_ext = file_url[file_url.rfind('.') + 1:]
        return file_url, file_ext

    @staticmethod
    def _extract_score(addr: str) -> str:
        raw = str(addr)  # not a mistake
        id_idx = raw.find('\'likes\': ') + len('\'likes\': ')
        return raw[id_idx:raw.find(',', id_idx + 1)]

    def _maxlim_str(self, maxlim: int) -> str:
        return f'&Take={maxlim or self._get_items_per_page():d}'

    def _tags_str(self) -> str:
        return f'&Tag={"|".join(self.positive_tags)}' if self.positive_tags else ''

    def _blocked_str(self) -> str:
        return f'&ExcludeTag={"|".join(self.negative_tags)}' if self.negative_tags else ''

    def _expand_tags(self, pwtag: str, explode: bool) -> Iterable[str]:
        if not TAG_NAMES:
            self._load_tag_names()
        expanded_tags = set()
        is_w = is_wtag(pwtag)
        if not is_w or not explode:
            nvtag = no_validation_tag(pwtag) if not is_w else ''
            if nvtag:
                expanded_tags.add(nvtag)
            else:
                pwntag = pwtag.replace('%2b', '+')
                if pwntag in TAG_NAMES:
                    expanded_tags.add(pwtag)
        else:
            trace(f'Expanding tags from wtag \'{pwtag}\'...')
            if pwtag in self.expand_cache:
                expanded_tags.update(set(self.expand_cache[pwtag]))
            else:
                self.expand_cache[pwtag] = list()
                pat = prepare_regex_fullmatch(normalize_wtag(pwtag))
                for tag in TAG_NAMES:
                    if pat.fullmatch(tag):
                        expanded_tags.add(tag)
                        self.expand_cache[pwtag].append(tag)
                if self.expand_cache[pwtag]:
                    n = '\n - '
                    trace(f'{n[1:]}{n.join(self.expand_cache[pwtag])}')
        return expanded_tags

    def _validate_tags(self, taglist: list[str], explode=False) -> None:
        inavlid_tags = set()
        tidx: int
        for tidx in reversed(range(len(taglist))):
            tag = taglist[tidx]
            try:
                extags = list(assert_nonempty(self._expand_tags(tag, explode)))
                if len(extags) > 1 or extags[0] != tag:
                    taglist_temp = taglist[tidx + 1:]
                    del taglist[tidx:]
                    taglist.extend(extags)
                    taglist.extend(taglist_temp)
            except Exception:
                trace(f'Error: invalid RZ tag: \'{tag}\'!')
                inavlid_tags.add(tag)
                continue
        if inavlid_tags:
            n = '\n - '
            thread_exit(f'Fatal: Invalid RZ tags found:\n - {n.join(sorted(inavlid_tags))}', -702)

    def _run_compare_filters(self, parents: MutableSet[str], filter_type: str, compare_bounds: tuple[int, int],
                             extact_func: Callable[[str], str]) -> None:
        if compare_bounds == INT_BOUNDS_DEFAULT:
            return
        abbrp = self._get_module_abbr_p()
        total_count_old = len(self.items_raw_per_task)
        removed_count = 0
        removed_messages: list[str] = list()
        idx: int
        for idx in reversed(range(total_count_old)):
            self.catch_cancel_or_ctrl_c()
            h = self.items_raw_per_task[idx]
            item_id = self._extract_id(h)
            comp_v_s = extact_func(h)
            comp_v_i = int(comp_v_s)
            idstring = f'{(abbrp if self.add_filename_prefix else "")}{item_id}'
            item_info = self.item_info_dict_per_task.get(idstring)
            lb, ub = compare_bounds
            unmatch = not (lb <= comp_v_i <= ub)
            if unmatch:
                if self.verbose and self._supports_native_id_filter():
                    removed_messages.append(f'{abbrp}{item_id} {filter_type} unmatch by not ({lb:d} <= {comp_v_i:d} <= {ub:d})!')
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

    def _id_filters(self, parents: MutableSet[str]) -> None:
        self._run_compare_filters(parents, 'id', self.id_bounds, self._extract_id)

    def _score_filters(self, parents: MutableSet[str]) -> None:
        self._run_compare_filters(parents, 'score', self.score_bounds, self._extract_score)

    def _execute_module_filters(self, parents: MutableSet[str]) -> None:
        self._id_filters(parents)
        self._score_filters(parents)

    def _load_tag_names(self) -> None:
        try:
            trace(f'Loading {self._get_module_abbr().upper()} tag names...')
            with open(FILE_LOC_TAGS, 'r', encoding=UTF8) as tags_json_file:
                TAG_NAMES.update(load(tags_json_file).keys())
        except Exception:
            trace(f'Error: Failed to load {self._get_module_abbr().upper()} tag names from {FILE_LOC_TAGS}')
            TAG_NAMES.add('')

#
#
#########################################
