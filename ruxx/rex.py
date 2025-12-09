# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import re

from .defines import MODULE_CHOICES, TAG_LENGTH_MAX_RN, TAG_LENGTH_MAX_RX, TAG_LENGTH_MIN
from .rex_1 import re_tags_exclude_rx_a_i
from .rex_2 import re_tags_exclude_rx_j_r
from .rex_3 import re_tags_exclude_rx_s_z_ex

re_space_mult = re.compile(r' {2,}')
re_uscore_mult = re.compile(r'_{2,}')

re_replace_symbols = re.compile(r'[^0-9a-zA-Z_+\-\[\]]+')
re_replace_symbols_sub = re.compile(r'[^0-9a-zA-Z_.\-]+')
re_numbered_or_counted_tag = re.compile(r'^(?!rule_?\d+)1?([^\d]+?)(?:_?\d+|s)?$')

re_tags_to_process_rx = re.compile(
    r'^(?:.+?_warc.+?|(?:[a-z]+?_)?elf|drae.{3}|tent[a-z]{3}es|(?:bell[a-z]|sto[a-z]{4})_bul[a-z]{2,3}|inf[a-z]{5}n|egg(?:_[a-z]{3,9}|s)?|'
    r'[a-z]{4}hral_i.+?|(?:\d{1,2}\+?)?(?:d|boys?|girls?|fu[a-z]{2}(?:[a-z]{4}|s)?|in[d-v]{2}cts?)|succ[a-z]{4}|'
    r'bbw|dog|eel|f(?:acesitting|ur)|hmv|pmv|tar|c(?:\.c\.|um)|d\.va|na\'vi|kai\'sa|'
    r'[^(]+\([^)]+\).*?|[a-z_\-]+\d+?|\d{2,4}[a-z_\-]+?|[a-z_]{2,15}sfm|[^_]+_pov|fu[a-z]{2}(?:/|_(?:on|with)_)[a-z]{4}(?:oy)?|'
    fr'[a-z][a-z_]{{{TAG_LENGTH_MIN - 1:d},{TAG_LENGTH_MAX_RX - 1:d}}}|[a-g]ea?st[a-z]{{6}}|[lapymg]{{3}}|ai_(?:gen|up|voi).+?)$',
)
re_tags_to_process_rn = re.compile(
    r'^(?:.+?_warc.+?|(?:[a-z]+?_)?elf|drae.{3}|tent[a-z]{3}es|(?:bell[a-z]|sto[a-z]{4})_bul[a-z]{2,3}|inf[a-z]{5}n|egg(?:_[a-z]{3,9}|s)?|'
    r'[a-z]{4}hral_i.+?|(?:\d{1,2}\+?)?(?:boys?|girls?|fu[a-z]{2}(?:[a-z]{4}|s)?|in[d-v]{2}cts?)|succ[a-z]{4}|'
    r'bbw|dog|eel|f(?:acesitting|ur)|hmv|pmv|tar|c(?:\.c\.|um)|d\.va|nyl|'
    r'[^(]+\([^)]+\).*?|[a-z_\-]+\d+?|\d{2,4}[a-z_\-]+?|[a-z_]{2,15}sfm|[^_]+_pov|fu[a-z]{2}_on_[a-z]{4}|'
    fr'[a-z][a-z_]{{{TAG_LENGTH_MIN - 1:d},{TAG_LENGTH_MAX_RN - 1:d}}}|[a-g]ea?st[a-z]{{6}}|[lapymg]{{3}})$',
)
re_tags_to_process_rs = re_tags_to_process_rx
re_tags_to_process_rp = re_tags_to_process_rn
re_tags_to_process_en = re_tags_to_process_rx
re_tags_to_process_xb = re_tags_to_process_rx
re_tags_to_process_bb = re_tags_to_process_rx

re_tags_exclude_major1 = re.compile(
    r'^(?:(?:digital|original|traditional)_(?:content|media|painting)|[234]d|h(?:d|ero_outfit)|level_up|p(?:ainting|rotagonist)|tagme|'
    r'war(?:rior|lock)|paladin|hunt(?:er|ress)|rogue|priest(?:ess)?|d(?:e(?:ath_?knight|mon_?hunt(?:er|ress))|ruid(?:ess)?)|'  # wow
    r'shaman|m(?:age|onk)|alliance|horde|'  # wow
    r'(?:human|d(?:warf)|undead|forsaken|t(?:roll)|g(?:nome|oblin)|worgen|pandaren|vulpera)(?:_.+?)?|'  # wow
    r'[a-z]pose|[\da-z_\-]{16,})_$',
)
re_tags_exclude_major2 = re.compile(
    r'^(?:(?:digital|original|traditional)_(?:content|media|painting)|a(?:natomy|rtwork)|c(?:lassic|o(?:dec|loring|mpany))|'
    r'd(?:isambiguation)|e(?:nlargement)|f(?:emale|ilmmaker)|genus|m(?:a(?:p|rkings?)|e(?:dium|tal))|p(?:rojectile|ublisher)|'
    r'r(?:elationship)|s(?:oftware|ymbol)|t(?:emperature|raditional)|we(?:apon|bsite)|'
    r'[\da-z_\-]{18,})$',
)

# noinspection RegExpDuplicateAlternationBranch
re_tags_exclude_rx = re.compile(fr'^(?:{re_tags_exclude_rx_a_i}|{re_tags_exclude_rx_j_r}|{re_tags_exclude_rx_s_z_ex})$')
re_tags_exclude_rn = re.compile(
    r'^(?:'
    r'a(?:nimated|u(?:d(?:io(?:dude|elk|gman|noob)?|r(?:arius|ix))|todesk(?:_.+?)?))|'  # a
    r'blender|'  # b
    r'c(?:apcom|elebrity|inema_\dd|rossover)|'  # c
    r'delalicious\d|'  # d
    r'evil(?:audio|zorak)|'  # e
    r'gif|'  # g
    r'hentaudio|'  # h
    r'jpe?g|'  # j
    r'leotard|'  # l
    r'm(?:arvel|p4)|'  # m
    r'neon_[wv].+?|'  # n
    r'o(?:ne?model|riginal_character)|'  # o
    r'p(?:ng|rotoss?)|'  # p
    r's(?:fm|lushe|ou(?:nd|rce_filmmaker)|wf)|'  # s
    r'v(?:irtual_youtuber|olkor)|'  # v
    r'webm|'  # w
    r'2d|3d|4d|'  # 0-9
    r'[^_]+_comi(?:cs?|x)|(?:[^_]+_){2,}[^w_][^_]*?'
    r')$',
)
re_tags_exclude_rs = re_tags_exclude_rx
re_tags_exclude_rp = re_tags_exclude_rn
re_tags_exclude_en = re_tags_exclude_rx
re_tags_exclude_xb = re_tags_exclude_rx
re_tags_exclude_bb = re_tags_exclude_rx

re_item_info_part_xml = re.compile(r'([\w5_]+=\"[^"]+\")[> ]')
re_orig_file_link = re.compile(r'file_url=\"([^"]+)\"')
re_sample_file_link = re.compile(r'file_url=\"([^"]+)\"')
re_item_filename = re.compile(r'file_name=\"([^"]+)\"')
re_post_page_rx = re.compile(r'^(?:\?page=post&(?:amp;)?s=list|document\.location=\'\?page=favorites|\?page=pool&(?:amp;)?s=show)&.+?$')

re_item_info_part_rn = re.compile(r'([\w\-]+=\"[^"]+\")[/> ]')
re_shimmie_image_href = re.compile(r'/_images/[^/]+/\d+?')
re_shimmie_thumb = re.compile(r'^thumb shm-thumb.+?$')
re_shimmie_orig_source = re.compile(r'^overflow:.+?$')
re_shimmie_image_href_full = re.compile(r'/_images/[^/]+/(\d+)%20-%20([^">]+)')

re_post_style_rs = re.compile(r'^border-radius: 3px;.+?$')
re_post_dims_rs = re.compile(r'^Size: (\d+)w x (\d+)h$')
re_post_page_rs = re.compile(r'^\?r=(?:posts/index|favorites/view&id=\d+)&.+?$')
re_tag_video_rs = re.compile(r'^\d+fps(?: upscale)?$|video|webm')
re_comment_page_rs = re.compile(r'^\?r=posts/view&(?:amp;)?id=\d+&(?:amp;)?page=\d+$')
re_comment_a_rs = re.compile(r'^index\.php\?r=account/profile&(?:amp;)?id=\d+$')

re_post_page_xb = re.compile(r'^(?:\?page=post&(?:amp;)?s=list|document\.location=\'\?page=favorites|\?page=pool&(?:amp;)?s=show)&.+?$')
re_post_page_bb = re_post_page_xb

re_favorited_by_tag = re.compile(r'^favorited_by[:=]!?([^:=]+)$')
re_pool_tag = re.compile(r'^pool[:=]([^:=]+)$')

re_infolist_filename = re.compile(fr'(?:{"|".join(MODULE_CHOICES)})_!(tags|sources|comments)_\d+-\d+\.txt')

re_ask_values = re.compile(r'[^, ]+')
re_json_entry_value = re.compile(r'^([^: ,]+)[: ,](.+)$')

re_meta_group = re.compile(r'^([^(]+)\(([^)]+)\).*?$')
re_not_a_letter = re.compile(r'[^a-z]+')
re_wtag = re.compile(r'^(?:[^?*]*[?*]).*?$')


def prepare_regex_fullmatch(raw_string: str) -> re.Pattern[str]:
    return re.compile(rf'^{raw_string}$')

#
#
#########################################
