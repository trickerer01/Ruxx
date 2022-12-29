# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from re import compile as re_compile

# internal
from app_defines import TAG_LENGTH_MIN, TAG_LENGTH_MAX_RX, TAG_LENGTH_MAX_RN
from app_re_1 import re_tags_exclude_rx_a_i
from app_re_2 import re_tags_exclude_rx_j_r
from app_re_3 import re_tags_exclude_rx_s_z_ex

re_replace_symbols = re_compile(
    r'[^0-9a-zA-Z_+\-\[\]]+'
)

# used with re.sub
# noinspection RegExpAnonymousGroup
re_numbered_or_counted_tag = re_compile(
    r'^(?!rule_?\d+)1?([^\d]+?)(?:_?\d+|s)?$'
)

re_tags_to_process_rx = re_compile(
    r'^(?:.+?_warc.+?|(?:[a-z]+?_)?elf|drae.{3}|tent[a-z]{3}es|(?:bell[a-z]|sto[a-z]{4})_bul[a-z]{2,3}|inf[a-z]{5}n|egg(?:_[a-z]{3,9}|s)?|'
    r'[a-z]{4}hral_i.+?|(?:\d{1,2}\+?)?(?:boys?|girls?|fu[a-z]{2}(?:[a-z]{4}|s)?|in[d-v]{2}cts?)|succ[a-z]{4}|'
    r'bbw|dog|eel|f(?:acesitting|ur)|hmv|pmv|tar|c(?:\.c\.|um)|d\.va|na\'vi|kai\'sa|'
    r'[^(]+\([^)]+\).*?|[a-z_\-]+\d+?|\d{2,4}[a-z_\-]+?|[a-z_]{2,15}sfm|[^_]+_pov|fu[a-z]{2}(?:/|_(?:on|with)_)[a-z]{4}(?:oy)?|'
    fr'[a-z][a-z_]{{{TAG_LENGTH_MIN - 1:d},{TAG_LENGTH_MAX_RX - 1:d}}}|[a-g]ea?st[a-z]{{6}}|[lapymg]{{3}})$'
)
re_tags_to_process_rn = re_compile(
    r'^(?:.+?_warc.+?|(?:[a-z]+?_)?elf|drae.{3}|tent[a-z]{3}es|(?:bell[a-z]|sto[a-z]{4})_bul[a-z]{2,3}|inf[a-z]{5}n|egg(?:_[a-z]{3,9}|s)?|'
    r'[a-z]{4}hral_i.+?|(?:\d{1,2}\+?)?(?:boys?|girls?|fu[a-z]{2}(?:[a-z]{4}|s)?|in[d-v]{2}cts?)|succ[a-z]{4}|'
    r'bbw|dog|eel|f(?:acesitting|ur)|hmv|pmv|tar|c(?:\.c\.|um)|d\.va|nyl|'
    r'[^(]+\([^)]+\).*?|[a-z_\-]+\d+?|\d{2,4}[a-z_\-]+?|[a-z_]{2,15}sfm|[^_]+_pov|fu[a-z]{2}_on_[a-z]{4}|'
    fr'[a-z][a-z_]{{{TAG_LENGTH_MIN - 1:d},{TAG_LENGTH_MAX_RN - 1:d}}}|[a-g]ea?st[a-z]{{6}}|[lapymg]{{3}})$'
)

re_tags_exclude_major1 = re_compile(
    r'^(?:(?:digital|original|traditional)_(?:content|media|painting)|[234]d|h(?:d|ero_outfit)|level_up|p(?:ainting|rotagonist)|tagme|'
    r'war(?:rior|lock)|paladin|hunt(?:er|ress)|rogue|priest(?:ess)?|d(?:e(?:ath_?knight|mon_?hunt(?:er|ress))|ruid(?:ess)?)|'  # wow
    r'shaman|m(?:age|onk)|alliance|horde|'  # wow
    r'(?:human|d(?:warf)|undead|forsaken|t(?:roll)|g(?:nome|oblin)|worgen|pandaren|vulpera)(?:_.+?)?|'  # wow
    r'[a-z]pose|[\da-z_\-]{16,})_$'
)
re_tags_exclude_major2 = re_compile(
    r'^(?:(?:digital|original|traditional)_(?:content|media|painting)|a(?:natomy|rtwork)|c(?:lassic|o(?:loring|mpany))|d(?:isambiguation)|'
    r'e(?:nlargement)|f(?:emale|ilmmaker)|genus|m(?:a(?:p|rkings?)|e(?:dium|tal))|p(?:rojectile|ublisher)|r(?:elationship)|'
    r's(?:oftware|ymbol)|t(?:emperature|raditional)|we(?:apon|bsite)|'
    r'[\da-z_\-]{18,})$'
)

re_tags_exclude_rx = re_compile(
    fr'^(?:{re_tags_exclude_rx_a_i}|{re_tags_exclude_rx_j_r}|{re_tags_exclude_rx_s_z_ex})$'
)

re_tags_exclude_rn = re_compile(
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
    r')$'
)

#
#
#########################################
