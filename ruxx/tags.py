# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

from enum import Enum, IntEnum, auto
from typing import NamedTuple

__all__ = ('TAG_CATEGORY_NAMES_BY_TYPE', 'TagCategories', 'TagInfo', 'TagTypes', 'tag_type_from_name')


# PyCharm bug PY-53388 (IDE thinks auto() needs an argument)
# noinspection PyArgumentList
class TagTypes(IntEnum):
    TAG_TYPE_GENERAL = auto()
    TAG_TYPE_COPYRIGHT = auto()
    TAG_TYPE_ARTIST = auto()
    TAG_TYPE_CHARACTER = auto()
    TAG_TYPE_META = auto()
    TAG_TYPE_UNKNOWN = auto()
    # EN
    TAG_TYPE_SPECIES = auto()
    TAG_TYPE_LORE = auto()
    TAG_TYPE_INVALID1 = auto()


class TagTypeNames(str, Enum):
    TAG_TYPE_NAME_GENERAL = 'general'
    TAG_TYPE_NAME_COPYRIGHT = 'copyright'
    TAG_TYPE_NAME_ARTIST = 'artist'
    TAG_TYPE_NAME_CHARACTER = 'character'
    TAG_TYPE_NAME_META = 'metadata'
    TAG_TYPE_NAME_UNKNOWN = 'unknown'
    TAG_TYPE_NAME_SPECIES = 'species'  # EN
    TAG_TYPE_NAME_LORE = 'lore'  # EN
    TAG_TYPE_NAME_INVALID1 = 'invalid1'  # EN
    TAG_TYPE_NAME_TAG = 'tag'  # RS


class TagInfo(NamedTuple):
    tag_type: TagTypes
    posts_count: int


# PyCharm bug PY-53388 (IDE thinks auto() needs an argument)
# noinspection PyArgumentList
class TagCategories(IntEnum):
    AUTO = 0
    GENERAL = auto()
    COPYRIGHT = auto()
    ARTIST = auto()
    CHARACTER = auto()
    METADATA = auto()
    # SPECIES = auto()  # EN
    # LORE = auto()  # EN
    # INVALID1 = auto()  # EN
    MAX_CATEGORIES = auto()
    INVALID = auto()


class TagCategoryNames(str, Enum):
    AUTO = 'Auto'
    GENERAL = 'General'
    COPYRIGHT = 'Copyright'
    ARTIST = 'Artist'
    CHARACTER = 'Character'
    METADATA = 'Metadata'
    # SPECIES = 'Species'  # EN
    # LORE = 'Lore'  # EN
    # INVALID1 = 'Invalid1'  # EN
    INVALID = 'Invalid'


TAG_TYPES_BY_NAME: dict[str | TagTypeNames, TagTypes] = {
    TagTypeNames.TAG_TYPE_NAME_GENERAL: TagTypes.TAG_TYPE_GENERAL,
    TagTypeNames.TAG_TYPE_NAME_COPYRIGHT: TagTypes.TAG_TYPE_COPYRIGHT,
    TagTypeNames.TAG_TYPE_NAME_ARTIST: TagTypes.TAG_TYPE_ARTIST,
    TagTypeNames.TAG_TYPE_NAME_CHARACTER: TagTypes.TAG_TYPE_CHARACTER,
    TagTypeNames.TAG_TYPE_NAME_META: TagTypes.TAG_TYPE_META,
    TagTypeNames.TAG_TYPE_NAME_UNKNOWN: TagTypes.TAG_TYPE_UNKNOWN,
    TagTypeNames.TAG_TYPE_NAME_SPECIES: TagTypes.TAG_TYPE_SPECIES,  # EN
    TagTypeNames.TAG_TYPE_NAME_LORE: TagTypes.TAG_TYPE_LORE,  # EN
    TagTypeNames.TAG_TYPE_NAME_INVALID1: TagTypes.TAG_TYPE_INVALID1,  # EN
    TagTypeNames.TAG_TYPE_NAME_TAG: TagTypes.TAG_TYPE_GENERAL,  # RS
}


TAG_NAMES_BY_TYPE: dict[TagTypes, TagTypeNames] = {
    TagTypes.TAG_TYPE_GENERAL: TagTypeNames.TAG_TYPE_NAME_GENERAL,
    TagTypes.TAG_TYPE_COPYRIGHT: TagTypeNames.TAG_TYPE_NAME_COPYRIGHT,
    TagTypes.TAG_TYPE_ARTIST: TagTypeNames.TAG_TYPE_NAME_ARTIST,
    TagTypes.TAG_TYPE_CHARACTER: TagTypeNames.TAG_TYPE_NAME_CHARACTER,
    TagTypes.TAG_TYPE_META: TagTypeNames.TAG_TYPE_NAME_META,
    TagTypes.TAG_TYPE_UNKNOWN: TagTypeNames.TAG_TYPE_NAME_UNKNOWN,
    TagTypes.TAG_TYPE_SPECIES: TagTypeNames.TAG_TYPE_NAME_SPECIES,  # EN
    TagTypes.TAG_TYPE_LORE: TagTypeNames.TAG_TYPE_NAME_LORE,  # EN
    TagTypes.TAG_TYPE_INVALID1: TagTypeNames.TAG_TYPE_NAME_INVALID1,  # EN
}


TAG_CATEGORY_NAMES_BY_TYPE: dict[TagCategories, TagCategoryNames] = {
    TagCategories.AUTO: TagCategoryNames.AUTO,
    TagCategories.GENERAL: TagCategoryNames.GENERAL,
    TagCategories.COPYRIGHT: TagCategoryNames.COPYRIGHT,
    TagCategories.ARTIST: TagCategoryNames.ARTIST,
    TagCategories.CHARACTER: TagCategoryNames.CHARACTER,
    TagCategories.METADATA: TagCategoryNames.METADATA,
    # TagCategories.SPECIES: TagCategoryNames.SPECIES,  # EN
    # TagCategories.LORE: TagCategoryNames.LORE,  # EN
    # TagCategories.INVALID1: TagCategoryNames.INVALID1,  # EN
    TagCategories.INVALID: TagCategoryNames.INVALID,
}


def tag_type_from_name(tag_desc_str: str, p1_idx: int, p2_idx: int) -> TagTypes:
    if all(0 <= _ < len(tag_desc_str) for _ in (p1_idx, p2_idx)):
        tag_type_str = tag_desc_str[p1_idx + 1:p2_idx]
        tag_type = TAG_TYPES_BY_NAME.get(tag_type_str, TagTypes.TAG_TYPE_UNKNOWN)
    else:
        tag_type = TagTypes.TAG_TYPE_UNKNOWN
    return tag_type

#
#
#########################################
