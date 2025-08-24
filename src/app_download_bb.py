# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
from base64 import b64decode
from re import Pattern

# internal
from app_defines import (
    Comment, SITENAME_B_BB, FILE_NAME_PREFIX_BB, MODULE_ABBR_BB, ITEMS_PER_PAGE_BB,
    TAGS_CONCAT_CHAR_BB, ID_VALUE_SEPARATOR_CHAR_BB,
)
from app_download_gelbooru import DownloaderGelbooru
from app_logger import trace
from app_re import (
    re_tags_to_process_bb, re_tags_exclude_bb, re_post_page_bb,
)

__all__ = ('DownloaderBb',)

SITENAME = b64decode(SITENAME_B_BB).decode()
ITEMS_PER_PAGE = ITEMS_PER_PAGE_BB
ITEMS_PER_PAGE_F = 50
ITEMS_PER_PAGE_P = 20000  # unknown, all posts are on a single page always
MAX_SEARCH_DEPTH = 200000 + ITEMS_PER_PAGE - 1  # set by site devs


class DownloaderBb(DownloaderGelbooru):
    """
    DownloaderBb
    """
    def __init__(self) -> None:
        super().__init__()

    def _get_api_key(self) -> str:
        return ''

    def _get_id_bounds(self) -> tuple[int, int]:
        raise NotImplementedError

    def _form_item_string_manually(self, *ignored) -> str:
        raise NotImplementedError

    def _get_re_post_page(self) -> Pattern:
        return re_post_page_bb

    def _get_sitename(self) -> str:
        return SITENAME

    def _get_module_abbr(self) -> str:
        return MODULE_ABBR_BB

    def _get_module_abbr_p(self) -> str:
        return FILE_NAME_PREFIX_BB

    def _get_items_per_page(self) -> int:
        return ITEMS_PER_PAGE_F if self.favorites_search_user else ITEMS_PER_PAGE_P if self.pool_search_str else ITEMS_PER_PAGE

    def _get_max_search_depth(self) -> int:
        return MAX_SEARCH_DEPTH

    def get_re_tags_to_process(self) -> Pattern:
        return re_tags_to_process_bb

    def get_re_tags_to_exclude(self) -> Pattern:
        return re_tags_exclude_bb

    def _get_tags_concat_char(self) -> str:
        return TAGS_CONCAT_CHAR_BB

    def _get_idval_equal_seaparator(self) -> str:
        return ID_VALUE_SEPARATOR_CHAR_BB

    def _extract_comments(self, item_id: str) -> None:
        raw_html = self.fetch_html(self._form_comments_search_address(item_id))
        if raw_html is None:
            trace(f'Warning (W3): ProcItem: unable to retreive comments for {item_id}!', True)
        else:
            full_item_id = f'{self._get_module_abbr_p() if self.add_filename_prefix else ""}{item_id}'
            comment_divs = raw_html.find_all('comment')
            for comment_div in comment_divs:
                author = comment_div.get('creator')
                body = comment_div.get('body')
                self.item_info_dict_per_task[full_item_id].comments.append(Comment(author, body))

#
#
#########################################
