# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from base64 import b64decode
from json import loads
from os import path, listdir, rename as rename_file
from re import fullmatch as re_fullmatch, sub as re_sub
from typing import Tuple, Pattern, Dict, List

# internal
from app_defines import DEFAULT_ENCODING, FILE_NAME_FULL_MAX_LEN
from app_gui_defines import SLASH, UNDERSCORE
from app_re import re_replace_symbols, re_tags_exclude_major1, re_tags_exclude_major2, re_numbered_or_counted_tag
from app_utils import trim_undersores


TAG_ALIASES_STR = (
    'eyJidW5ueV9ib3kiOiAiMStib3lzIiwgIm1hbGUiOiAiMStib3lzIiwgIm1hbGVfc29sbyI6ICIxK2JveXMiLCAibWFsZWRvbSI6ICIxK2JveXMiLCAibWFsZXN1YiI6ICIxK2'
    'JveXMiLCAibW9uc3Rlcl9ib3kiOiAiMStib3lzIiwgIm9yY19tYWxlIjogIjErYm95cyIsICIxMDFfZGFsbWF0aWFuX3N0cmVldCI6ICIxMDFfZGFsbWF0aWFucyIsICIybWFs'
    'ZSI6ICIyYm95cyIsICIybWFsZXMiOiAiMmJveXMiLCAiM21hbGUiOiAiM2JveXMiLCAiNjlfcG9zZSI6ICI2OSIsICI2OV9wb3NpdGlvbiI6ICI2OSIsICI2OV9zdGFuZGluZy'
    'I6ICI2OSIsICJzdGFuZGluZ182OSI6ICI2OSIsICJ4ZW5vbW9ycGgiOiAiYWxpZW4iLCAiYW5hbF9zZXgiOiAiYW5hbCIsICJhbmFsaW5ndXMiOiAiYW5hbCIsICJhbmlsaW5n'
    'dXMiOiAiYW5hbCIsICJyZWN0dW0iOiAiYW5hbCIsICJzc2JidyI6ICJiYnciLCAiYmRzbV9jb2xsYXIiOiAiYmRzbSIsICJiZHNtX2dlYXIiOiAiYmRzbSIsICJiZHNtX2hhcm'
    '5lc3MiOiAiYmRzbSIsICJiZHNtX291dGZpdCI6ICJiZHNtIiwgImJkc21fcm9vbSI6ICJiZHNtIiwgImJkc21fc3VpdCI6ICJiZHNtIiwgImJzZG0iOiAiYmRzbSIsICJtYXNv'
    'Y2hpc20iOiAiYmRzbSIsICJtYXNvY2hpc3QiOiAiYmRzbSIsICJhbGxpZ2F0b3IiOiAiYmVhc3QiLCAiYW5pbWFsIjogImJlYXN0IiwgImZlcmFsIjogImJlYXN0IiwgImZlcm'
    'FsX29uX2ZlcmFsIjogImJlYXN0IiwgImZlcmFsX3BlbmV0cmF0ZWQiOiAiYmVhc3QiLCAiZmVyYWxfcGVuZXRyYXRpbmciOiAiYmVhc3QiLCAibWFtbWFsIjogImJlYXN0Iiwg'
    'Im1lcGhpdGlkIjogImJlYXN0IiwgIm9jZWxvdCI6ICJiZWFzdCIsICJwcm9jeW9uaWQiOiAiYmVhc3QiLCAicmVwdGlsZSI6ICJiZWFzdCIsICJyb2RlbnQiOiAiYmVhc3QiLC'
    'AiZWdnX2J1bGdlIjogImJlbGx5X2J1bGdlIiwgInN0b21hY2hfYnVsZ2UiOiAiYmVsbHlfYnVsZ2UiLCAiZmVtYWxlX29uX2ZlcmFsIjogImJlc3RpYWxpdHkiLCAiZmVyYWxf'
    'b25fYW50aHJvIjogImJlc3RpYWxpdHkiLCAiZmVyYWxfb25fZmVtYWxlIjogImJlc3RpYWxpdHkiLCAiZmVyYWxfb25faHVtYW4iOiAiYmVzdGlhbGl0eSIsICJmZXJhbF9vbl'
    '9tYWxlIjogImJlc3RpYWxpdHkiLCAiaHVtYW5fb25fZmVyYWwiOiAiYmVzdGlhbGl0eSIsICJtYWxlX29uX2ZlcmFsIjogImJlc3RpYWxpdHkiLCAiem9vcGhpbGlhIjogImJl'
    'c3RpYWxpdHkiLCAiYmlrZXN1aXQiOiAiYm9keXN1aXQiLCAiYmlvc3VpdCI6ICJib2R5c3VpdCIsICJiaXRjaF9zdWl0IjogImJvZHlzdWl0IiwgImJpdGNoc3VpdCI6ICJib2'
    'R5c3VpdCIsICJidW5ueV9zdWl0IjogImJvZHlzdWl0IiwgImJ1bm55c3VpdCI6ICJib2R5c3VpdCIsICJjYXRfc3VpdCI6ICJib2R5c3VpdCIsICJjYXRzdWl0IjogImJvZHlz'
    'dWl0IiwgImdpbXBfc3VpdCI6ICJib2R5c3VpdCIsICJnaW1wc3VpdCI6ICJib2R5c3VpdCIsICJwbHVnX3N1aXQiOiAiYm9keXN1aXQiLCAicGx1Z3N1aXQiOiAiYm9keXN1aX'
    'QiLCAic3dpbV9zdWl0IjogImJvZHlzdWl0IiwgInN3aW1zdWl0IjogImJvZHlzdWl0IiwgInplcm9fc3VpdCI6ICJib2R5c3VpdCIsICJ6ZXJvc3VpdCI6ICJib2R5c3VpdCIs'
    'ICJib3VuZCI6ICJib25kYWdlIiwgImJvdW5kX2FybXMiOiAiYm9uZGFnZSIsICJib3VuZF9mZWV0IjogImJvbmRhZ2UiLCAiYm91bmRfaGFuZHMiOiAiYm9uZGFnZSIsICJib3'
    'VuZF9sZWdzIjogImJvbmRhZ2UiLCAiYm91bmRfbmVjayI6ICJib25kYWdlIiwgImJvdW5kX3BlbmlzIjogImJvbmRhZ2UiLCAiYm91bmRfdG9fYmVkIjogImJvbmRhZ2UiLCAi'
    'Ym91bmRfdG9fY2hhaXIiOiAiYm9uZGFnZSIsICJib3VuZF93cmlzdHMiOiAiYm9uZGFnZSIsICJicmVhc3RfYm9uZGFnZSI6ICJib25kYWdlIiwgImNoYWlyX2JvbmRhZ2UiOi'
    'AiYm9uZGFnZSIsICJtdW1taWZpY2F0aW9uIjogImJvbmRhZ2UiLCAibXVtbWlmaWVkIjogImJvbmRhZ2UiLCAicHJlZGljYW1lbnRfYm9uZGFnZSI6ICJib25kYWdlIiwgInJl'
    'c3RyYWluIjogImJvbmRhZ2UiLCAicmVzdHJhaW5lZCI6ICJib25kYWdlIiwgInJlc3RyYWludCI6ICJib25kYWdlIiwgInJlc3RyYWludHMiOiAiYm9uZGFnZSIsICJyaWJib2'
    '5fYm9uZGFnZSI6ICJib25kYWdlIiwgInJvcGVfYm9uZGFnZSI6ICJib25kYWdlIiwgInNoaWJhcmkiOiAiYm9uZGFnZSIsICJzdGVlbF9ib25kYWdlIjogImJvbmRhZ2UiLCAi'
    'c3RyYXBwYWRvIjogImJvbmRhZ2UiLCAic3RyYXBwZWRfZG93biI6ICJib25kYWdlIiwgInN1c3BlbmRlZCI6ICJib25kYWdlIiwgInN1c3BlbnNpb24iOiAiYm9uZGFnZSIsIC'
    'JzdXNwZW5zaW9uX2JvbmRhZ2UiOiAiYm9uZGFnZSIsICJ0YWlsX2JvbmRhZ2UiOiAiYm9uZGFnZSIsICJ0YXBlX2JvbmRhZ2UiOiAiYm9uZGFnZSIsICJ3ZWJfYm9uZGFnZSI6'
    'ICJib25kYWdlIiwgImJvdmluZSI6ICJib3ZpZCIsICJjYW5pbiI6ICJjYW5pZCIsICJjYW5pbmUiOiAiY2FuaWQiLCAiY2FuaXMiOiAiY2FuaWQiLCAiY29sbGllIjogImNhbm'
    'lkIiwgImRpcmVfd29sZiI6ICJjYW5pZCIsICJkb2Jlcm1hbiI6ICJjYW5pZCIsICJodXNreSI6ICJjYW5pZCIsICJsYWJyYWRvciI6ICJjYW5pZCIsICJtYWxhbXV0ZSI6ICJj'
    'YW5pZCIsICJtYXN0aWZmIjogImNhbmlkIiwgInBpdF9idWxsIjogImNhbmlkIiwgInBpdGJ1bGwiOiAiY2FuaWQiLCAicG9vZGxlIjogImNhbmlkIiwgInJldHJpZXZlciI6IC'
    'JjYW5pZCIsICJzYW1veWVkIjogImNhbmlkIiwgInNwYW5pZWwiOiAiY2FuaWQiLCAid29sZiI6ICJjYW5pZCIsICJ3b2xmZG9nIjogImNhbmlkIiwgImFiZHVjdGVkIjogImNh'
    'cHR1cmVkIiwgImFiZHVjdGlvbiI6ICJjYXB0dXJlZCIsICJhcnJlc3RlZCI6ICJjYXB0dXJlZCIsICJjYWdlZCI6ICJjYXB0dXJlZCIsICJjYXB0aXZlIjogImNhcHR1cmVkIi'
    'wgImNhcHR1cmUiOiAiY2FwdHVyZWQiLCAiY2hhaW5lZCI6ICJjYXB0dXJlZCIsICJkZXRhaW5lZCI6ICJjYXB0dXJlZCIsICJqYWlsZWQiOiAiY2FwdHVyZWQiLCAia2lkbmFw'
    'IjogImNhcHR1cmVkIiwgImtpZG5hcHBlZCI6ICJjYXB0dXJlZCIsICJraWRuYXBwaW5nIjogImNhcHR1cmVkIiwgInNoYWNrbGVkIjogImNhcHR1cmVkIiwgInRyYXBwZWQiOi'
    'AiY2FwdHVyZWQiLCAiY2F0Z2lybCI6ICJjYXRfZ2lybCIsICJkZWVyX3RhdXIiOiAiY2VudGF1ciIsICJkZWVydGF1ciI6ICJjZW50YXVyIiwgImNlcnZpbmUiOiAiY2Vydmlk'
    'IiwgImJsdWVfY3VtIjogImN1bSIsICJjdW1fYmF0aCI6ICJjdW0iLCAiY3VtX2JlbGx5IjogImN1bSIsICJjdW1fYnViYmxlIjogImN1bSIsICJjdW1fYnVja2V0IjogImN1bS'
    'IsICJjdW1fY292ZXJlZCI6ICJjdW0iLCAiY3VtX2RyaW5raW5nIjogImN1bSIsICJjdW1fZHJpcCI6ICJjdW0iLCAiY3VtX2RyaXBwaW5nIjogImN1bSIsICJjdW1fZmlsbGVk'
    'IjogImN1bSIsICJjdW1fZmxvb2QiOiAiY3VtIiwgImN1bV9mcm9tX2FzcyI6ICJjdW0iLCAiY3VtX2Zyb21fcHVzc3kiOiAiY3VtIiwgImN1bV9nbGF6ZSI6ICJjdW0iLCAiY3'
    'VtX2h1bmdyeSI6ICJjdW0iLCAiY3VtX2luX2FudXMiOiAiY3VtIiwgImN1bV9pbl9hc3MiOiAiY3VtIiwgImN1bV9pbl9jbG90aGVzIjogImN1bSIsICJjdW1faW5fY29uZG9t'
    'IjogImN1bSIsICJjdW1faW5fY29udGFpbmVyIjogImN1bSIsICJjdW1faW5faGFpciI6ICJjdW0iLCAiY3VtX2luX21vdXRoIjogImN1bSIsICJjdW1faW5fbm9zZSI6ICJjdW'
    '0iLCAiY3VtX2luX3B1c3N5IjogImN1bSIsICJjdW1faW5fdGhyb2F0IjogImN1bSIsICJjdW1faW5fdXRlcnVzIjogImN1bSIsICJjdW1faW5zaWRlIjogImN1bSIsICJjdW1f'
    'amFyIjogImN1bSIsICJjdW1fa2lzcyI6ICJjdW0iLCAiY3VtX2xlYWsiOiAiY3VtIiwgImN1bV9sZWFraW5nIjogImN1bSIsICJjdW1fbGljayI6ICJjdW0iLCAiY3VtX21pbG'
    'tpbmciOiAiY3VtIiwgImN1bV9vbl9hc3MiOiAiY3VtIiwgImN1bV9vbl9iYWxscyI6ICJjdW0iLCAiY3VtX29uX2JvZHkiOiAiY3VtIiwgImN1bV9vbl9icmVhc3RzIjogImN1'
    'bSIsICJjdW1fb25fYnV0dCI6ICJjdW0iLCAiY3VtX29uX2NoZXN0IjogImN1bSIsICJjdW1fb25fY2xvdGhlcyI6ICJjdW0iLCAiY3VtX29uX2ZhY2UiOiAiY3VtIiwgImN1bV'
    '9vbl9mZWV0IjogImN1bSIsICJjdW1fb25fZ3JvdW5kIjogImN1bSIsICJjdW1fb25faGFpciI6ICJjdW0iLCAiY3VtX29uX2hhbmQiOiAiY3VtIiwgImN1bV9vbl9sZWciOiAi'
    'Y3VtIiwgImN1bV9vbl9wZW5pcyI6ICJjdW0iLCAiY3VtX29uX3NlbGYiOiAiY3VtIiwgImN1bV9vbl9zdG9tYWNoIjogImN1bSIsICJjdW1fb25fdG9uZ3VlIjogImN1bSIsIC'
    'JjdW1fcG9vbCI6ICJjdW0iLCAiY3VtX3B1ZGRsZSI6ICJjdW0iLCAiY3VtX3JpbmciOiAiY3VtIiwgImN1bV9zaG90IjogImN1bSIsICJjdW1fc3BhdHRlciI6ICJjdW0iLCAi'
    'Y3VtX3NxdWlydCI6ICJjdW0iLCAiY3VtX3N0YWluIjogImN1bSIsICJjdW1fc3RyYW5kIjogImN1bSIsICJjdW1fc3RyaW5nIjogImN1bSIsICJjdW1fc3dhbGxvdyI6ICJjdW'
    '0iLCAiY3VtX3N3YXAiOiAiY3VtIiwgImN1bWRyaXAiOiAiY3VtIiwgImN1bWR1bXAiOiAiY3VtIiwgImN1bWx1YmUiOiAiY3VtIiwgImN1bW1pbmciOiAiY3VtIiwgImN1bXBv'
    'b2wiOiAiY3VtIiwgImN1bXNlYSI6ICJjdW0iLCAiY3Vtc2hvdCI6ICJjdW0iLCAiY3Vtc2x1dCI6ICJjdW0iLCAiY3Vtc3RyaW5nIjogImN1bSIsICJncmVlbl9jdW0iOiAiY3'
    'VtIiwgInByZWN1bSI6ICJjdW0iLCAidGhpY2tfY3VtIjogImN1bSIsICJoYW5hX3NvbmciOiAiZC52YSIsICJkYW5nYW5yb25wYV92MyI6ICJkYW5nYW5yb25wYSIsICJuZXdf'
    'ZGFuZ2Fucm9ucGFfdjMiOiAiZGFuZ2Fucm9ucGEiLCAic3VwZXJfZGFuZ2Fucm9ucGFfMiI6ICJkYW5nYW5yb25wYSIsICJkcm93X2VsZiI6ICJkYXJrX2VsZiIsICJkdW5tZX'
    'IiOiAiZGFya19lbGYiLCAiZHVubWVyX2VsZiI6ICJkYXJrX2VsZiIsICJkZWFkIjogImRlYXRoIiwgInJvZV9kZWVyIjogImRlZXIiLCAiZGVsdGFydW5lX2NoYXB0ZXJfMSI6'
    'ICJkZWx0YXJ1bmUiLCAiZGVsdGFydW5lX2NoYXB0ZXJfMiI6ICJkZWx0YXJ1bmUiLCAiZGVsdGFydW5lX2NoYXB0ZXJfMyI6ICJkZWx0YXJ1bmUiLCAiZGVtb25fYm95IjogIm'
    'RlbW9uIiwgImRlbW9uX2h1bWFub2lkIjogImRlbW9uIiwgImRlbW9ucyI6ICJkZW1vbiIsICJkZXZpbCI6ICJkZW1vbiIsICJkZXZpbF9naXJsIjogImRlbW9uIiwgImVyZWRh'
    'ciI6ICJkZW1vbiIsICJkZW1vbl9naXJsIjogImRlbW9uZXNzIiwgImRlbW9uX2dpcmxzIjogImRlbW9uZXNzIiwgImRlbW9uZ2lybCI6ICJkZW1vbmVzcyIsICJkZW1vbmdpcm'
    'xzIjogImRlbW9uZXNzIiwgImRlcnBfZXllcyI6ICJkZXJwIiwgImRvZ2dpcmwiOiAiZG9nX2dpcmwiLCAiZHdhcmZfZmVtYWxlIjogImR3YXJmIiwgImVlbF9pbl9hc3MiOiAi'
    'ZWVsIiwgImVlbF9pbl9wdXNzeSI6ICJlZWwiLCAiZWVsX2luX3VyZXRocmEiOiAiZWVsIiwgImVlbF9pbnNlcnRpb24iOiAiZWVsIiwgImVnZ19iaXJ0aCI6ICJlZ2ciLCAiZW'
    'dnX2Zyb21fYXNzIjogImVnZyIsICJlZ2dfZnJvbV9tb3V0aCI6ICJlZ2ciLCAiZWdnX2Zyb21fcHVzc3kiOiAiZWdnIiwgImVnZ19pbXBsYW50YXRpb24iOiAiZWdnIiwgImVn'
    'Z19pbl9hc3MiOiAiZWdnIiwgImVnZ19pbl9tb3V0aCI6ICJlZ2ciLCAiZWdnX2luX3B1c3N5IjogImVnZyIsICJlZ2dfaW5zZXJ0aW9uIjogImVnZyIsICJlZ2dfbGF5aW5nIj'
    'ogImVnZyIsICJlZ2duYW50IjogImVnZyIsICJlZ2dzX2luX3N0b21hY2giOiAiZWdnIiwgIm9yYWxfZWdnX2ltcGxhbnRhdGlvbiI6ICJlZ2ciLCAiZWx2ZXMiOiAiZWxmIiwg'
    'ImhpZ2hfZWxmIjogImVsZiIsICJ3b29kX2VsZiI6ICJlbGYiLCAiZXF1aW5lIjogImVxdWlkIiwgImZhY2Vfc2l0dGluZyI6ICJmYWNlc2l0dGluZyIsICJmYWNlc2l0IjogIm'
    'ZhY2VzaXR0aW5nIiwgImZhY2VzaXR0aW5nX3BvdiI6ICJmYWNlc2l0dGluZyIsICJjdW1fZmFydCI6ICJmYXJ0IiwgImZhY2VfZmFydCI6ICJmYXJ0IiwgImZhY2VmYXJ0Ijog'
    'ImZhcnQiLCAiZmFydF9jbG91ZCI6ICJmYXJ0IiwgImZhcnRfZmV0aXNoIjogImZhcnQiLCAiZmFydF9pbl9mYWNlIjogImZhcnQiLCAiZmFydF9pbl9tb3V0aCI6ICJmYXJ0Ii'
    'wgImZhcnRfb25fZGljayI6ICJmYXJ0IiwgImZhcnRfb25fZmFjZSI6ICJmYXJ0IiwgImZhcnRfc25pZmZpbmciOiAiZmFydCIsICJmYXJ0aW5nX2luX2ZhY2UiOiAiZmFydCIs'
    'ICJmYXJ0aW5nX2luX21vdXRoIjogImZhcnQiLCAiZmFydGluZ19vbl9mYWNlIjogImZhcnQiLCAiZmFydGpvYiI6ICJmYXJ0IiwgImZhcnRzIjogImZhcnQiLCAiZmVsaW5lIj'
    'ogImZlbGlkIiwgImZlbGlzIjogImZlbGlkIiwgImZlbWJveXN1YiI6ICJmZW1ib3kiLCAiYW5hbF9maXN0aW5nIjogImZpc3RpbmciLCAiYXV0b2Zpc3RpbmciOiAiZmlzdGlu'
    'ZyIsICJkZWVwX2Zpc3RpbmciOiAiZmlzdGluZyIsICJkb3VibGVfZmlzdGluZyI6ICJmaXN0aW5nIiwgInNlbGZfZmlzdGluZyI6ICJmaXN0aW5nIiwgInZhZ2luYWxfZmlzdG'
    'luZyI6ICJmaXN0aW5nIiwgImZveGdpcmwiOiAiZm94X2dpcmwiLCAiYmxhY2tfZnVyIjogImZ1ciIsICJibHVlX2Z1ciI6ICJmdXIiLCAiYm9keV9mdXIiOiAiZnVyIiwgImJy'
    'b3duX2Z1ciI6ICJmdXIiLCAiZGFya19mdXIiOiAiZnVyIiwgImdyYXlfZnVyIjogImZ1ciIsICJncmVlbl9mdXIiOiAiZnVyIiwgImdyZXlfZnVyIjogImZ1ciIsICJvcmFuZ2'
    'VfZnVyIjogImZ1ciIsICJwaW5rX2Z1ciI6ICJmdXIiLCAicHVycGxlX2Z1ciI6ICJmdXIiLCAicmVkX2Z1ciI6ICJmdXIiLCAidGFuX2Z1ciI6ICJmdXIiLCAid2V0X2Z1ciI6'
    'ICJmdXIiLCAid2hpdGVfZnVyIjogImZ1ciIsICJ5ZWxsb3dfZnVyIjogImZ1ciIsICJhbnRocm9fZm9jdXMiOiAiZnVycnkiLCAiYW50aHJvX29uX2FudGhybyI6ICJmdXJyeS'
    'IsICJhbnRocm9fb25fZmVyYWwiOiAiZnVycnkiLCAiYW50aHJvX29ubHkiOiAiZnVycnkiLCAiZnVycmVkX2RyYWdvbiI6ICJmdXJyeSIsICJmdXJyaWZpY2F0aW9uIjogImZ1'
    'cnJ5IiwgImZ1cnJ5X2FzcyI6ICJmdXJyeSIsICJmdXJyeV9icmVhc3RzIjogImZ1cnJ5IiwgImZ1cnJ5X2VhcnMiOiAiZnVycnkiLCAiZnVycnlfZmVtYWxlIjogImZ1cnJ5Ii'
    'wgImZ1cnJ5X2ludGVyc2V4IjogImZ1cnJ5IiwgImZ1cnJ5X21hbGUiOiAiZnVycnkiLCAiZnVycnlfb25seSI6ICJmdXJyeSIsICJmdXJyeV90YWlsIjogImZ1cnJ5IiwgImZ1'
    'cnJ5ZmljYXRpb24iOiAiZnVycnkiLCAibWFtbWFsX2h1bWFub2lkIjogImZ1cnJ5IiwgInNjYWxpZSI6ICJmdXJyeSIsICJzZXh5ZnVyIjogImZ1cnJ5IiwgIndvcmdlbiI6IC'
    'JmdXJyeSIsICJ5aWZmIjogImZ1cnJ5IiwgInlpZmZpbmciOiAiZnVycnkiLCAiZnV0YV93aXRoX21hbGUiOiAiZnV0YV9vbl9tYWxlIiwgImZ1dGFuYXJpL21hbGUiOiAiZnV0'
    'YV9vbl9tYWxlIiwgImRlbW9uX2Z1dGEiOiAiZnV0YW5hcmkiLCAiZWxmX2Z1dGEiOiAiZnV0YW5hcmkiLCAiZnV0YS9jdW50Ym95IjogImZ1dGFuYXJpIiwgImZ1dGEvZmVtYW'
    'xlIjogImZ1dGFuYXJpIiwgImZ1dGEvZmVtYm95IjogImZ1dGFuYXJpIiwgImZ1dGEvZnV0YSI6ICJmdXRhbmFyaSIsICJmdXRhL21hbGUiOiAiZnV0YW5hcmkiLCAiZnV0YV8i'
    'OiAiZnV0YW5hcmkiLCAiZnV0YV9iYWxscyI6ICJmdXRhbmFyaSIsICJmdXRhX2NvY2siOiAiZnV0YW5hcmkiLCAiZnV0YV9mb2N1cyI6ICJmdXRhbmFyaSIsICJmdXRhX2dpYW'
    '50ZXNzIjogImZ1dGFuYXJpIiwgImZ1dGFfaXNfYmlnZ2VyIjogImZ1dGFuYXJpIiwgImZ1dGFfaXNfc21hbGxlciI6ICJmdXRhbmFyaSIsICJmdXRhX21pbGYiOiAiZnV0YW5h'
    'cmkiLCAiZnV0YV9vbl9mZW1hbGUiOiAiZnV0YW5hcmkiLCAiZnV0YV9vbl9mZW1ib3kiOiAiZnV0YW5hcmkiLCAiZnV0YV9vbl9mdXRhIjogImZ1dGFuYXJpIiwgImZ1dGFfb2'
    '5fdG9wIjogImZ1dGFuYXJpIiwgImZ1dGFfb25seSI6ICJmdXRhbmFyaSIsICJmdXRhX3BvdiI6ICJmdXRhbmFyaSIsICJmdXRhX3NhbnNfYmFsbHMiOiAiZnV0YW5hcmkiLCAi'
    'ZnV0YV9zYW5zX3B1c3N5IjogImZ1dGFuYXJpIiwgImZ1dGFfc29sbyI6ICJmdXRhbmFyaSIsICJmdXRhX3N1YiI6ICJmdXRhbmFyaSIsICJmdXRhX3dpZmUiOiAiZnV0YW5hcm'
    'kiLCAiZnV0YV93aXRoX2ZlbWFsZSI6ICJmdXRhbmFyaSIsICJmdXRhX3dpdGhfZmVtYm95IjogImZ1dGFuYXJpIiwgImZ1dGFfd2l0aF9mdXRhIjogImZ1dGFuYXJpIiwgImZ1'
    'dGFkb20iOiAiZnV0YW5hcmkiLCAiZnV0YW5hcmkvY3VudGJveSI6ICJmdXRhbmFyaSIsICJmdXRhbmFyaS9mZW1hbGUiOiAiZnV0YW5hcmkiLCAiZnV0YW5hcmkvZmVtYm95Ij'
    'ogImZ1dGFuYXJpIiwgImZ1dGFuYXJpL2Z1dGEiOiAiZnV0YW5hcmkiLCAiZnV0YW5hcmlfcGVuZXRyYXRlZCI6ICJmdXRhbmFyaSIsICJmdXRhbmFyaV9wZW5ldHJhdGluZyI6'
    'ICJmdXRhbmFyaSIsICJmdXRhbmFyaV9wb3YiOiAiZnV0YW5hcmkiLCAiZnV0YW5hcmlfdHJhbnNmb3JtYXRpb24iOiAiZnV0YW5hcmkiLCAiZnV0YW5hcml6YXRpb24iOiAiZn'
    'V0YW5hcmkiLCAiZnV0YXN1YiI6ICJmdXRhbmFyaSIsICJtaW5pZnV0YSI6ICJmdXRhbmFyaSIsICJzb2xlX2Z1dGEiOiAiZnV0YW5hcmkiLCAic29sb19mdXRhIjogImZ1dGFu'
    'YXJpIiwgImJhbGxfZ2FnIjogImdhZyIsICJiYWxsZ2FnIjogImdhZyIsICJiYW1ib29fZ2FnIjogImdhZyIsICJiaXRfZ2FnIjogImdhZyIsICJiaXRlX2dhZyI6ICJnYWciLC'
    'AiYmxhY2tfYmFsbF9nYWciOiAiZ2FnIiwgImJsdWVfYmFsbF9nYWciOiAiZ2FnIiwgImJvbmVfZ2FnIjogImdhZyIsICJjbGVhdmVfZ2FnIjogImdhZyIsICJjbG90aF9nYWci'
    'OiAiZ2FnIiwgImNvY2tfZ2FnIjogImdhZyIsICJkZW50YWxfZ2FnIjogImdhZyIsICJkaWxkb19nYWciOiAiZ2FnIiwgImdhZ19iYWxsIjogImdhZyIsICJnYWdfYm9uZGFnZS'
    'I6ICJnYWciLCAiZ2FnX2hhcm5lc3MiOiAiZ2FnIiwgImdhZ19tYXNrIjogImdhZyIsICJnYWdnZWQiOiAiZ2FnIiwgImdhZ2dpbmciOiAiZ2FnIiwgImhhbmRnYWciOiAiZ2Fn'
    'IiwgImhhcm5lc3NfYmFsbF9nYWciOiAiZ2FnIiwgImhhcm5lc3NfYml0X2dhZyI6ICJnYWciLCAiaGFybmVzc19iaXRlX2dhZyI6ICJnYWciLCAiaGFybmVzc19nYWciOiAiZ2'
    'FnIiwgImhhcm5lc3NfcmluZ19nYWciOiAiZ2FnIiwgImltcHJvdmlzZWRfZ2FnIjogImdhZyIsICJtb3V0aF9nYWciOiAiZ2FnIiwgIm11enpsZV9nYWciOiAiZ2FnIiwgIm9u'
    'YWhvbGVfZ2FnIjogImdhZyIsICJvcGVuX21vdXRoX2dhZyI6ICJnYWciLCAib3RtX2dhZyI6ICJnYWciLCAib3Zlcl90aGVfbW91dGhfZ2FnIjogImdhZyIsICJvdmVyX3RoZV'
    '9ub3NlX2dhZyI6ICJnYWciLCAicGFuZWxfZ2FnIjogImdhZyIsICJwYW50eV9nYWciOiAiZ2FnIiwgInBpbmtfYmFsbF9nYWciOiAiZ2FnIiwgInBsdWdfZ2FnIjogImdhZyIs'
    'ICJwdXJwbGVfYmFsbF9nYWciOiAiZ2FnIiwgInJlZF9iYWxsX2dhZyI6ICJnYWciLCAicmluZ19nYWciOiAiZ2FnIiwgInJvcGVfZ2FnIjogImdhZyIsICJyb3BlZ2FnIjogIm'
    'dhZyIsICJzaGFyZWRfZ2FnIjogImdhZyIsICJzdHVmZmVkX21vdXRoX2dhZyI6ICJnYWciLCAidGFwZV9nYWciOiAiZ2FnIiwgInRlbnRhY2xlX2dhZyI6ICJnYWciLCAid2Vi'
    'X2dhZyI6ICJnYWciLCAid2hpdGVfYmFsbF9nYWciOiAiZ2FnIiwgImdhbmdfYmFuZyI6ICJnYW5nYmFuZyIsICJnYW5nX3JhcGUiOiAiZ2FuZ2JhbmciLCAiZ2FuZ3JhcGUiOi'
    'AiZ2FuZ2JhbmciLCAiYW5hbF9nYXBlIjogImdhcGUiLCAiYmlnX2dhcGUiOiAiZ2FwZSIsICJnYXBpbmciOiAiZ2FwZSIsICJnYXBpbmdfYW51cyI6ICJnYXBlIiwgImdhcGlu'
    'Z19hc3MiOiAiZ2FwZSIsICJnYXBpbmdfY2xvYWNhIjogImdhcGUiLCAiZ2FwaW5nX25pcHBsZSI6ICJnYXBlIiwgImdhcGluZ19uaXBwbGVzIjogImdhcGUiLCAiZ2FwaW5nX3'
    'B1c3l5IjogImdhcGUiLCAiZ2FwaW5nX3VyZXRocmEiOiAiZ2FwZSIsICJodWdlX2dhcGUiOiAiZ2FwZSIsICJiYXJhIjogImdheSIsICJiYXJhX3RpZGRpZXMiOiAiZ2F5Iiwg'
    'ImJhcmFfdGl0cyI6ICJnYXkiLCAiYmFyYWthIjogImdheSIsICJiYXJha2luZyI6ICJnYXkiLCAiYmFyYWx1c3QiOiAiZ2F5IiwgImJhcmFzdWlzaG91IjogImdheSIsICJiYX'
    'JheW90IjogImdheSIsICJiYXJhem9rdSI6ICJnYXkiLCAiYmlzZXh1YWxfbWFsZSI6ICJnYXkiLCAiZ2F5X2FuYWxfbWFzdHVyYmF0aW9uIjogImdheSIsICJnYXlfYmFyIjog'
    'ImdheSIsICJnYXlfYmVhciI6ICJnYXkiLCAiZ2F5X2Jsb3dqb2IiOiAiZ2F5IiwgImdheV9kZW5pYWwiOiAiZ2F5IiwgImdheV9kb2NraW5nIjogImdheSIsICJnYXlfZG9taW'
    '5hdGlvbiI6ICJnYXkiLCAiZ2F5X2hhbmRqb2IiOiAiZ2F5IiwgImdheV9oYXJlbSI6ICJnYXkiLCAiZ2F5X29yZ3kiOiAiZ2F5IiwgImdheV9wb3Juc3RhciI6ICJnYXkiLCAi'
    'Z2F5X3ByaWRlIjogImdheSIsICJnYXlfcHJpZGVfY29sb3JzIjogImdheSIsICJnYXlfc2V4IjogImdheSIsICJnYXlfc291bmQiOiAiZ2F5IiwgImdheV90b19zdHJhaWdodC'
    'I6ICJnYXkiLCAiZ2F5X3dpdGhfd29tYW4iOiAiZ2F5IiwgImdheV93cmVzdGxpbmciOiAiZ2F5IiwgImdheXRvciI6ICJnYXkiLCAibWVuX2tpc3NpbmciOiAiZ2F5IiwgImdp'
    'cmFmZmUiOiAiZ2lyYWZmaWQiLCAiZ2xwcnlfaG9sZSI6ICJnbG9yeWhvbGUiLCAiZ29vZ2lybCI6ICJnb29fZ2lybCIsICJzbGltZV9naXJsIjogImdvb19naXJsIiwgInNsaW'
    '1lZ2lybCI6ICJnb29fZ2lybCIsICJnb3RoaWZpZWQiOiAiZ290aCIsICJtYXJlIjogImhvcnNlIiwgInBvbnkiOiAiaG9yc2UiLCAic3RhbGxpb24iOiAiaG9yc2UiLCAiaHll'
    'bmEiOiAiaHlhZW5pZCIsICJpZ3VhbmEiOiAiaWd1YW5pZCIsICJjbG9uZWNlc3QiOiAiaW5jZXN0IiwgImltcGxpZWRfaW5jZXN0IjogImluY2VzdCIsICJtb21jZXN0IjogIm'
    'luY2VzdCIsICJzZWxmY2VzdCI6ICJpbmNlc3QiLCAidHdpbmNlc3QiOiAiaW5jZXN0IiwgImN1bV9pbmZsYXRpb24iOiAiaW5mbGF0aW9uIiwgImN1bWZsYXRpb24iOiAiaW5m'
    'bGF0aW9uIiwgImVnZ19pbmZsYXRpb24iOiAiaW5mbGF0aW9uIiwgInNsaW1lX2luZmxhdGlvbiI6ICJpbmZsYXRpb24iLCAiaW5qdXJlIjogImluanVyeSIsICJpbmp1cmVkIj'
    'ogImluanVyeSIsICJpbmp1cmVzIjogImluanVyeSIsICJhcmFjaG5pZCI6ICJpbnNlY3QiLCAiYXJ0aHJvcG9kIjogImluc2VjdCIsICJiZWUiOiAiaW5zZWN0IiwgImJlZXMi'
    'OiAiaW5zZWN0IiwgImNlbnRpcGVkZSI6ICJpbnNlY3QiLCAiY29ja3JvYXNoIjogImluc2VjdCIsICJlYXJ0aHdvcm0iOiAiaW5zZWN0IiwgImdhc3Ryb3BvZCI6ICJpbnNlY3'
    'QiLCAiaG9ybmV0IjogImluc2VjdCIsICJpbnNlY3RvaWQiOiAiaW5zZWN0IiwgImxlZWNoIjogImluc2VjdCIsICJsZWVjaGVzIjogImluc2VjdCIsICJsb2N1c3QiOiAiaW5z'
    'ZWN0IiwgImxvY3VzdHMiOiAiaW5zZWN0IiwgIm1hZ2dvdCI6ICJpbnNlY3QiLCAibWFnZ290cyI6ICJpbnNlY3QiLCAibWFudGlzIjogImluc2VjdCIsICJtb3NxdWl0byI6IC'
    'JpbnNlY3QiLCAibW90aCI6ICJpbnNlY3QiLCAicXVlZW5fYmVlIjogImluc2VjdCIsICJzcGlkZXIiOiAiaW5zZWN0IiwgInRhcmFudHVsYSI6ICJpbnNlY3QiLCAidmVzcGlk'
    'IjogImluc2VjdCIsICJ3YXNwIjogImluc2VjdCIsICJ3YXNwcyI6ICJpbnNlY3QiLCAid29ybSI6ICJpbnNlY3QiLCAid29ybXMiOiAiaW5zZWN0IiwgImthaV9zYSI6ICJrYW'
    'lzYSIsICJibGFja19sYXRleCI6ICJsYXRleCIsICJsYXRleF9ib2R5c3VpdCI6ICJsYXRleCIsICJsYXRleF9jbG90aGluZyI6ICJsYXRleCIsICJsYXRleF9kcmVzcyI6ICJs'
    'YXRleCIsICJsYXRleF9nbG92ZXMiOiAibGF0ZXgiLCAibGF0ZXhfbGVnZ2luZ3MiOiAibGF0ZXgiLCAibGF0ZXhfbGVnd2VhciI6ICJsYXRleCIsICJsYXRleF9zdG9ja2luZ3'
    'MiOiAibGF0ZXgiLCAibGF0ZXhfc3VpdCI6ICJsYXRleCIsICJsYXRleF90aGlnaGhpZ2h0cyI6ICJsYXRleCIsICJydWJiZXIiOiAibGF0ZXgiLCAicnViYmVyX2Jvb3RzIjog'
    'ImxhdGV4IiwgInJ1YmJlcl9jbG90aGluZyI6ICJsYXRleCIsICJydWJiZXJfZ2xvdmVzIjogImxhdGV4IiwgInJ1YmJlcl9zdWl0IjogImxhdGV4IiwgImxlemRvbSI6ICJsZX'
    'NiaWFuIiwgImxlenN1YiI6ICJsZXNiaWFuIiwgInl1cmkiOiAibGVzYmlhbiIsICJsaW9uZXNzIjogImxpb24iLCAibWFyaW9fZ29sZiI6ICJtYXJpbyIsICJtYXJpb19rYXJ0'
    'IjogIm1hcmlvIiwgIm1hcmlvX3BhcnR5IjogIm1hcmlvIiwgIm1hcmlvX3Rlbm5pcyI6ICJtYXJpbyIsICJwYXBlcl9tYXJpbyI6ICJtYXJpbyIsICJzdXBlcl9tYXJpbyI6IC'
    'JtYXJpbyIsICJzdXBlcl9tYXJpb182NCI6ICJtYXJpbyIsICJteV9saXR0bGVfcG9ueSI6ICJtbHAiLCAibXlfbGl0dGxlX3BvbnlfZnJpZW5kc2hpcF9pc19tYWdpYyI6ICJt'
    'bHAiLCAibXlfbGl0dGxlX3BvbnlfdGhlX21vdmllIjogIm1scCIsICJnYXJnb3lsZSI6ICJtb25zdGVyIiwgImdhcmdveWxlcyI6ICJtb25zdGVyIiwgIm1vdXNlZ2lybCI6IC'
    'Jtb3VzZV9naXJsIiwgIm11c3RlbGEiOiAibXVzdGVsaWQiLCAibXVzdGVsaW5lIjogIm11c3RlbGlkIiwgIm5hcnV0bzpfdGhlX2xhc3QiOiAibmFydXRvIiwgIm5hcnV0b19i'
    'b21iIjogIm5hcnV0byIsICJuYXJ1dG9fc2hpcHB1bmRlbiI6ICJuYXJ1dG8iLCAibmllcjpfYXV0b21hdGEiOiAibmllciIsICJuaWVyX3JlcGxpY2FudCI6ICJuaWVyIiwgIm'
    'thbGRvcmVpIjogIm5pZ2h0X2VsZiIsICJudW1idWhfNSI6ICJudW1iYWhfNSIsICJibG93am9iIjogIm9yYWwiLCAiZmFjZV9mdWNrIjogIm9yYWwiLCAiZmFjZV9mdWNraW5n'
    'IjogIm9yYWwiLCAiZmFjZWZ1Y2siOiAib3JhbCIsICJmZWxsYXRpbyI6ICJvcmFsIiwgIm9yYWxfY3JlYW1waWUiOiAib3JhbCIsICJvcmFsX2luc2VydGlvbiI6ICJvcmFsIi'
    'wgIm9yYWxfa25vdHRpbmciOiAib3JhbCIsICJvcmFsX21hc3R1cmJhdGlvbiI6ICJvcmFsIiwgIm9yYWxfcGVuZXRyYXRpb24iOiAib3JhbCIsICJvcmFsX3JhcGUiOiAib3Jh'
    'bCIsICJvcmFsX3NleCI6ICJvcmFsIiwgInNwaXRyb2FzdCI6ICJvcmFsIiwgInN1Y2tpbmciOiAib3JhbCIsICJ0b25ndWVfam9iIjogIm9yYWwiLCAidG9uZ3Vlam9iIjogIm'
    '9yYWwiLCAiM3NvbWUiOiAib3JneSIsICI0c29tZSI6ICJvcmd5IiwgIjVzb21lIjogIm9yZ3kiLCAiNnNvbWUiOiAib3JneSIsICJmaXZlc29tZSI6ICJvcmd5IiwgImZvdXJz'
    'b21lIjogIm9yZ3kiLCAiZ3JvdXBfc2V4IjogIm9yZ3kiLCAic2l4c29tZSI6ICJvcmd5IiwgInRocmVlc29tZSI6ICJvcmd5IiwgInBlcnNvbmFfM19wb3J0YWJsZSI6ICJwZX'
    'Jzb25hXzMiLCAicGVyc29uYV80X2FyZW5hIjogInBlcnNvbmFfNCIsICJwZXJzb25hXzRfdGhlX2dvbGRlbiI6ICJwZXJzb25hXzQiLCAicGVyc29uYV81X3JveWFsIjogInBl'
    'cnNvbmFfNSIsICJwZXRnaXJ0bCI6ICJwZXRfZ2lybCIsICJhc3Npc3RlZF9wZWUiOiAicGlzc2luZyIsICJkcmlua2luZ19wZWUiOiAicGlzc2luZyIsICJtb3V0aF9wZWUiOi'
    'AicGlzc2luZyIsICJwYW50eV9wZWUiOiAicGlzc2luZyIsICJwZWVpbmciOiAicGlzc2luZyIsICJzaXR0aW5nX3BlZSI6ICJwaXNzaW5nIiwgInN0YW5kaW5nX3BlZSI6ICJw'
    'aXNzaW5nIiwgInVyaW5hdGluZyI6ICJwaXNzaW5nIiwgInVyaW5hdGlvbiI6ICJwaXNzaW5nIiwgInVyaW5lX2luX2FzcyI6ICJwaXNzaW5nIiwgInVyaW5lX2luX21vdXRoIj'
    'ogInBpc3NpbmciLCAidXJpbmVfcG9vbCI6ICJwaXNzaW5nIiwgInVyaW5lX3N0cmVhbSI6ICJwaXNzaW5nIiwgImRpZ2ltb24iOiAicG9rZW1vbiIsICJlc3Blb24iOiAicG9r'
    'ZW1vbiIsICJmbGFyZW9uIjogInBva2Vtb24iLCAiZ2FyZGV2b2lyIjogInBva2Vtb24iLCAiZ2xhY2VvbiI6ICJwb2tlbW9uIiwgImpvbHRlb24iOiAicG9rZW1vbiIsICJsb3'
    'B1bm55IjogInBva2Vtb24iLCAicG9rZV9iYWxsIjogInBva2Vtb24iLCAicG9rZWJhbGwiOiAicG9rZW1vbiIsICJwb2tlbW9uX2J3IjogInBva2Vtb24iLCAicG9rZW1vbl9i'
    'dzIiOiAicG9rZW1vbiIsICJwb2tlbW9uX2RwcHQiOiAicG9rZW1vbiIsICJwb2tlbW9uX2ZvY3VzIjogInBva2Vtb24iLCAicG9rZW1vbl9nbyI6ICJwb2tlbW9uIiwgInBva2'
    'Vtb25fZ3NjIjogInBva2Vtb24iLCAicG9rZW1vbl9oZ3NzIjogInBva2Vtb24iLCAicG9rZW1vbl9tYXN0ZXJzIjogInBva2Vtb24iLCAicG9rZW1vbl9vbmx5IjogInBva2Vt'
    'b24iLCAicG9rZW1vbl9vcmFzIjogInBva2Vtb24iLCAicG9rZW1vbl9yZ2J5IjogInBva2Vtb24iLCAicG9rZW1vbl9yc2UiOiAicG9rZW1vbiIsICJwb2tlbW9uX3NtIjogIn'
    'Bva2Vtb24iLCAicG9rZW1vbl9zcyI6ICJwb2tlbW9uIiwgInBva2Vtb25fc3YiOiAicG9rZW1vbiIsICJwb2tlbW9uX3h5IjogInBva2Vtb24iLCAicG9rZW1vcnBoIjogInBv'
    'a2Vtb24iLCAicG9rZXBoaWxpYSI6ICJwb2tlbW9uIiwgInBva8OpbW9uIjogInBva2Vtb24iLCAicG9rw6lwaGlsaWEiOiAicG9rZW1vbiIsICJyZW5hbW9uIjogInBva2Vtb2'
    '4iLCAic25lYXNsZXIiOiAicG9rZW1vbiIsICJzeWx2ZW9uIjogInBva2Vtb24iLCAidW1icmVvbiI6ICJwb2tlbW9uIiwgInZhcG9yZW9uIjogInBva2Vtb24iLCAicG9ueWdp'
    'cmwiOiAicG9ueV9naXJsIiwgInBvbnlfcGxheSI6ICJwb255cGxheSIsICJwcmVnbmFuY3kiOiAicHJlZ25hbnQiLCAiYnVubnkiOiAicmFiYml0IiwgImxlcG9yaWQiOiAicm'
    'FiYml0IiwgInJhYmJpdF9naXJsIjogInJhYmJpdF9naXJsIiwgInJhYmJpdGdpcmwiOiAicmFiYml0X2dpcmwiLCAicmF0Z2lybCI6ICJyYXRfZ2lybCIsICJyb2JvdGdpcmwi'
    'OiAicm9ib3RfZ2lybCIsICJydWxlNjMiOiAicnVsZV82MyIsICJjb3Byb3BoYWdpYSI6ICJzY2F0IiwgImV4Y2Vzc2l2ZV9zY2F0IjogInNjYXQiLCAiZmVjZXMiOiAic2NhdC'
    'IsICJwb29wIjogInNjYXQiLCAicG9vcGluZyI6ICJzY2F0IiwgInNjYXRfZWF0aW5nIjogInNjYXQiLCAic2NhdF9waWxlIjogInNjYXQiLCAic2hpdCI6ICJzY2F0IiwgInNo'
    'aXR0aW5nIjogInNjYXQiLCAic2hhZG93X2VsZiI6ICJzaGFkb3dfZWxmIiwgInNoYXJrX2dpcmwiOiAic2hhcmtfZ2lybCIsICJzaGFya2dpcmwiOiAic2hhcmtfZ2lybCIsIC'
    'JlbnNsYXZlZCI6ICJzbGF2ZSIsICJlbnNsYXZlZF9yb3lhbCI6ICJzbGF2ZSIsICJzbGF2ZV9ib3kiOiAic2xhdmUiLCAic2xhdmVib3kiOiAic2xhdmUiLCAic2xhdmVnaXJs'
    'IjogInNsYXZlIiwgInNsYXZlcyI6ICJzbGF2ZSIsICJ0YW1lZCI6ICJzbGF2ZSIsICJnb28iOiAic2xpbWUiLCAiZ29vX2JveSI6ICJzbGltZSIsICJnb29fY3JlYXR1cmUiOi'
    'Aic2xpbWUiLCAiZ29vX2hhaXIiOiAic2xpbWUiLCAiZ29vX2h1bWFub2lkIjogInNsaW1lIiwgImdvb19tb25zdGVyIjogInNsaW1lIiwgImdvb190ZW50YWNsZSI6ICJzbGlt'
    'ZSIsICJnb29fdGVudGFjbGVzIjogInNsaW1lIiwgImdvb190cmFuc2Zvcm1hdGlvbiI6ICJzbGltZSIsICJnb29leSI6ICJzbGltZSIsICJzbGltZV9ib3kiOiAic2xpbWUiLC'
    'Aic2xpbWVfaGFpciI6ICJzbGltZSIsICJzbGltZV9tb25zdGVyIjogInNsaW1lIiwgInNsaW1lYm95IjogInNsaW1lIiwgInNsaW15IjogInNsaW1lIiwgInNsdXRfYmVsdCI6'
    'ICJzbHV0IiwgInNsdXRfY2FwIjogInNsdXQiLCAic2x1dF9jb2xsYXIiOiAic2x1dCIsICJzbHV0X2tpdHR5IjogInNsdXQiLCAic2x1dF9vd25lciI6ICJzbHV0IiwgInNsdX'
    'RfcHJpbnQiOiAic2x1dCIsICJ3ZW5jaCI6ICJzbHV0IiwgIndob3JlIjogInNsdXQiLCAiY29icmEiOiAic25ha2UiLCAicHl0aG9uIjogInNuYWtlIiwgInNxdWlydGluZyI6'
    'ICJzcXVpcnQiLCAib2RvciI6ICJzdGluayIsICJzbWVsbHkiOiAic3RpbmsiLCAic21lbGx5X2FzcyI6ICJzdGluayIsICJzbWVsbHlfY29jayI6ICJzdGluayIsICJzbWVsbH'
    'lfZmVldCI6ICJzdGluayIsICJzdGlua19saW5lcyI6ICJzdGluayIsICJzdGlua3kiOiAic3RpbmsiLCAic3Rpbmt5X2ZlZXQiOiAic3RpbmsiLCAiaGV0ZXJvIjogInN0cmFp'
    'Z2h0IiwgImhldGVyb19zZXgiOiAic3RyYWlnaHQiLCAiaGV0ZXJvc2V4dWFsIjogInN0cmFpZ2h0IiwgInJlY2VpdmluZ19wb3YiOiAidGFrZXJfcG92IiwgInN1Ym1pc3Npdm'
    'VfcG92IjogInRha2VyX3BvdiIsICJmb3hfdGF1ciI6ICJ0YXVyIiwgImZveHRhdXIiOiAidGF1ciIsICJ3b2xmX3RhdXIiOiAidGF1ciIsICJ3b2xmdGF1ciI6ICJ0YXVyIiwg'
    'InRla2tlbl81X2RhcmtfcmVzdXJyZWN0aW9uIjogInRla2tuIiwgInRla2tlbl90YWdfdG91cm5hbWVudCI6ICJ0ZWtrbiIsICJ0ZWtrZW5fdGFnX3RvdXJuYW1lbnRfMiI6IC'
    'J0ZWtrbiIsICJ0ZW50YWNsZV9faW5fbW91dGgiOiAidGVudGFjbGUiLCAidGVudGFjbGVfZmVsbGF0aW8iOiAidGVudGFjbGUiLCAidGVudGFjbGVfZ3JhYiI6ICJ0ZW50YWNs'
    'ZSIsICJ0ZW50YWNsZV9oYWlyIjogInRlbnRhY2xlIiwgInRlbnRhY2xlX2luX2FudXMiOiAidGVudGFjbGUiLCAidGVudGFjbGVfaW5fYXNzIjogInRlbnRhY2xlIiwgInRlbn'
    'RhY2xlX2luX3B1c3N5IjogInRlbnRhY2xlIiwgInRlbnRhY2xlX21vbnN0ZXIiOiAidGVudGFjbGUiLCAidGVudGFjbGVfb25fZmVtYWxlIjogInRlbnRhY2xlIiwgInRlbnRh'
    'Y2xlX29uX2Z1dGEiOiAidGVudGFjbGUiLCAidGVudGFjbGVfb25fbWFsZSI6ICJ0ZW50YWNsZSIsICJ0ZW50YWNsZV9wZW5ldHJhdGlvbiI6ICJ0ZW50YWNsZSIsICJ0ZW50YW'
    'NsZV9waXQiOiAidGVudGFjbGUiLCAidGVudGFjbGVfcmFwZSI6ICJ0ZW50YWNsZSIsICJ0ZW50YWNsZV9zZXgiOiAidGVudGFjbGUiLCAidGVudGFjbGVqb2IiOiAidGVudGFj'
    'bGUiLCAidGVudGFjbGVzX29uX2ZlbWFsZSI6ICJ0ZW50YWNsZSIsICJ0ZW50YWNsZXNfb25fZnV0YSI6ICJ0ZW50YWNsZSIsICJ0ZW50YWNsZXNfb25fbWFsZSI6ICJ0ZW50YW'
    'NsZSIsICJ0aWVkX2FybXMiOiAidGllZF91cCIsICJ0aWVkX2JhbGxzIjogInRpZWRfdXAiLCAidGllZF9kb3duIjogInRpZWRfdXAiLCAidGllZF9mZWV0IjogInRpZWRfdXAi'
    'LCAidGllZF9oYWlyIjogInRpZWRfdXAiLCAidGllZF9oYW5kcyI6ICJ0aWVkX3VwIiwgInRpZWRfbGVncyI6ICJ0aWVkX3VwIiwgInRpZWRfcGVuaXMiOiAidGllZF91cCIsIC'
    'J0aWVkX3RvZXMiOiAidGllZF91cCIsICJ0b3J0dXJlX2NoYW1iZXIiOiAidG9ydHVyZSIsICJ0b3J0dXJlX2RldmljZSI6ICJ0b3J0dXJlIiwgInRvcnR1cmVfcmFjayI6ICJ0'
    'b3J0dXJlIiwgInRvcnR1cmVkIjogInRvcnR1cmUiLCAidG9ydHVyZXIiOiAidG9ydHVyZSIsICJ0b3J0dXJlcyI6ICJ0b3J0dXJlIiwgInRvcnR1cmluZyI6ICJ0b3J0dXJlIi'
    'wgImFtYmlndW91c19nZW5kZXIiOiAidHJhbnMiLCAiY3Jvc3NnZW5kZXIiOiAidHJhbnMiLCAiZ2VuZGVyX2JlbmRlciI6ICJ0cmFucyIsICJnZW5kZXJfdHJhbnNvZnJtYXRp'
    'b24iOiAidHJhbnMiLCAiZ2VuZGVyYmVuZCI6ICJ0cmFucyIsICJnZW5kZXJiZW5kZXIiOiAidHJhbnMiLCAiZ2VuZGVyYmVudCI6ICJ0cmFucyIsICJnZW5kZXJzd2FwIjogIn'
    'RyYW5zIiwgIm1hbGVfaGVybSI6ICJ0cmFucyIsICJtYWxlaGVybSI6ICJ0cmFucyIsICJtYW5fYm9vYnMiOiAidHJhbnMiLCAibWFuX3RpdHMiOiAidHJhbnMiLCAibWFuYm9v'
    'YnMiOiAidHJhbnMiLCAibXRhX2Nyb3NzZ2VuZGVyIjogInRyYW5zIiwgIm10YV90cmFuc2Zvcm1hdGlvbiI6ICJ0cmFucyIsICJtdGYiOiAidHJhbnMiLCAibXRmX2Nyb3NzZ2'
    'VuZGVyIjogInRyYW5zIiwgIm10Zl90cmFuc2Zvcm1hdGlvbiI6ICJ0cmFucyIsICJtdGdfY3Jvc3NnZW5kZXIiOiAidHJhbnMiLCAibXRnX3RyYW5zZm9ybWF0aW9uIjogInRy'
    'YW5zIiwgIm10aF9jcm9zc2dlbmRlciI6ICJ0cmFucyIsICJtdGhfdHJhbnNmb3JtYXRpb24iOiAidHJhbnMiLCAibXRpX2Nyb3NzZ2VuZGVyIjogInRyYW5zIiwgIm10aV90cm'
    'Fuc2Zvcm1hdGlvbiI6ICJ0cmFucyIsICJ0dWJlX2ZlZWRpbmciOiAidHViZSIsICJ0dWJlX2dhZyI6ICJ0dWJlIiwgInR1YmVfaW5fYXNzIjogInR1YmUiLCAidHViZV9pbl9t'
    'b3V0aCI6ICJ0dWJlIiwgInR1YmVzIjogInR1YmUiLCAidWdseV9iYXN0YXJkIjogInVnbHkiLCAidWdseV9mZW1hbGUiOiAidWdseSIsICJ1Z2x5X2Z1dGEiOiAidWdseSIsIC'
    'J1Z2x5X21hbGUiOiAidWdseSIsICJ1Z2x5X21hbiI6ICJ1Z2x5IiwgInVyZXRocmFsIjogInVyZXRocmEiLCAidXJldGhyYWxfYmVhZHMiOiAidXJldGhyYSIsICJ1cmV0aHJh'
    'bF9idWxnZSI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX2ZpbmdlcmluZyI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX2Zpc3RpbiI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX2luc2VydG'
    'lvbiI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX2xpY2tpbmciOiAidXJldGhyYSIsICJ1cmV0aHJhbF9vdmlwb3NpdGlvbiI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX3BlbmV0cmF0'
    'aW9uIjogInVyZXRocmEiLCAidXJldGhyYWxfcGx1ZyI6ICJ1cmV0aHJhIiwgInVyZXRocmFsX3NleCI6ICJ1cmV0aHJhIiwgInZpb2xhdGVkIjogInZpb2xlbmNlIiwgInZpb2'
    'xhdGlvbiI6ICJ2aW9sZW5jZSIsICJ2aW9sZW50IjogInZpb2xlbmNlIiwgImFuYWxfdm9yZSI6ICJ2b3JlIiwgImNvY2tfdm9yZSI6ICJ2b3JlIiwgImRldm91cmVkIjogInZv'
    'cmUiLCAiZGV2b3VyaW5nIjogInZvcmUiLCAiZGlnZXN0aW9uIjogInZvcmUiLCAibWFzc192b3JlIjogInZvcmUiLCAib3JhbF92b3JlIjogInZvcmUiLCAicGxhbnRfdm9yZS'
    'I6ICJ2b3JlIiwgInBvc3Rfdm9yZSI6ICJ2b3JlIiwgInNvZnRfdm9yZSI6ICJ2b3JlIiwgInZvcmVfc2V4IjogInZvcmUiLCAid2FyaGFtbWVyXzQwMDAwIjogIndhcmhhbW1l'
    'ciIsICJ3YXJoYW1tZXJfNDBrIjogIndhcmhhbW1lciIsICJ3b2xmZ2lybCI6ICJ3b2xmX2dpcmwiLCAid293IjogIndvcmxkX29mX3dhcmNyYWZ0IiwgInhyYXlfdmlldyI6IC'
    'J4cmF5IiwgInplYnJvaWQiOiAiemVicmEiLCAiem9tYmllX2Z1dGEiOiAiem9tYmllIiwgInpvbWJpZXMiOiAiem9tYmllIn0='
)
TAG_ALIASES = loads(b64decode(TAG_ALIASES_STR))  # type: Dict[str, str]

__UPDATE_TAG_ALIASES__ = True
if __UPDATE_TAG_ALIASES__:
    from base64 import b64encode
    TAG_ALIASES.update({})  # kill warning
    [TAG_ALIASES.pop(k) for k in []]
    TAG_ALIASES.update({
        'healslut': 'slut',
        'heal_slut': 'slut',
        'bimbofication': 'bimbo',
        'bimbofied': 'bimbo',
        'bimbo_lip': 'bimbo',
        'bimbo_lips': 'bimbo',
        'bimbo_body': 'bimbo',
        'bimbo_futanari': 'bimbo',
        'bimbo_anthro': 'bimbo',
        'bimbo_succubus': 'bimbo',
        'bimboed': 'bimbo',
        'bimbos': 'bimbo',
    })
    TAG_ALIASES = {
        k: v
        for k, v in
        sorted(sorted(TAG_ALIASES.items(), key=lambda item: item[0]), key=lambda item: item[1])
    }  # type: Dict[str, str]
    TAG_ALIASES_STR = b64encode(str(TAG_ALIASES).replace('\'', '"').encode()).decode()


def append_filtered_tags(add_string: str, tags_str: str, re_tags_to_process: Pattern, re_tags_to_exclude: Pattern) -> str:
    if len(tags_str) == 0:
        return add_string

    tags_list = tags_str.split(' ')
    tags_toadd_list = []  # type: List[str]

    for tag in tags_list:
        tag = tag.replace('-', '').replace('\'', '')
        if TAG_ALIASES.get(tag) is None and re_fullmatch(re_tags_to_process, tag) is None:
            continue

        # digital_media_(artwork)
        aser_match = re_fullmatch(r'^([^(]+)\(([^)]+)\).*$', tag)
        aser_valid = False
        if aser_match:
            major_skip_match1 = re_fullmatch(re_tags_exclude_major1, aser_match.group(1))
            major_skip_match2 = re_fullmatch(re_tags_exclude_major2, aser_match.group(2))
            if major_skip_match1 or major_skip_match2:
                continue
            stag = trim_undersores(aser_match.group(1))
            if len(stag) >= 14:
                continue
            tag = stag
            aser_valid = True

        tag = trim_undersores(tag)
        alias = TAG_ALIASES.get(tag)
        if alias:
            tag = alias

        if re_fullmatch(re_tags_to_exclude, tag):
            continue

        do_add = True
        if len(tags_toadd_list) > 0:
            nutag = re_sub(r'[^a-z]+', '', re_sub(re_numbered_or_counted_tag, r'\1', tag))
            # try and see
            # 1) if this tag can be consumed by existing tags
            # 2) if this tag can consume existing tags
            for i in reversed(range(len(tags_toadd_list))):
                t = re_sub(re_numbered_or_counted_tag, r'\1', tags_toadd_list[i].lower())
                nut = re_sub(r'[^a-z]+', '', t)
                if len(nut) >= len(nutag) and (nutag in nut):
                    do_add = False
                    break
            if do_add:
                for i in reversed(range(len(tags_toadd_list))):
                    t = re_sub(re_numbered_or_counted_tag, r'\1', tags_toadd_list[i].lower())
                    nut = re_sub(r'[^a-z]+', '', t)
                    if len(nutag) >= len(nut) and (nut in nutag):
                        if aser_valid is False and tags_toadd_list[i][0].isupper():
                            aser_valid = True
                        del tags_toadd_list[i]
        if do_add:
            if aser_valid:
                for i, c in enumerate(tag):  # type: int, str
                    if (i == 0 or tag[i - 1] == UNDERSCORE) and c.isalpha():
                        tag = f'{tag[:i]}{c.upper()}{tag[i + 1:]}'
            tags_toadd_list.append(tag)

    return f'{add_string}{UNDERSCORE}{re_sub(re_replace_symbols, UNDERSCORE, UNDERSCORE.join(sorted(tags_toadd_list)))}'


def untag_files(files: Tuple[str]) -> int:
    untagged_count = 0
    try:
        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            base_path, full_name = tuple(full_path.rsplit(SLASH, 1))
            if not re_fullmatch(r'^(?:[a-z]{2}_)?(?:\d+?)[_].+?$', full_name):
                continue
            name, ext = path.splitext(full_name)
            untagged_name = re_sub(r'^([a-z]{2}_)?(\d+?)[_.].+?$', r'\1\2', name)
            new_name = f'{base_path}{SLASH}{untagged_name}{ext}'
            rename_file(full_path, new_name)
            untagged_count += 1
    except Exception:
        pass

    return untagged_count


def retag_files(files: Tuple[str], re_tags_to_process: Pattern, re_tags_to_exclude: Pattern) -> int:
    retagged_count = 0
    try:
        tagfiles_lines_full = []  # type: List[Tuple[str, str]]
        full_path = files[0].replace('\\', SLASH)
        base_path = full_path[:full_path.rfind(SLASH)]
        curdirfiles = list(listdir(base_path))
        for f in curdirfiles:
            if re_fullmatch(r'^[a-z]{2}_!tags_\d+?-\d+?\.txt$', f):
                with open(f'{base_path}{SLASH}{f}', 'r', encoding=DEFAULT_ENCODING) as fo:
                    tagfiles_lines_full.extend({tuple(a.strip().split(': ', 1)) for a in fo.readlines() if len(a) > 1})

        tagdict = {v[0][3:]: v[1] for v in tagfiles_lines_full}  # type: Dict[str, str]

        for full_path in files:
            full_path = full_path.replace('\\', SLASH)
            base_path, full_name = tuple(full_path.rsplit(SLASH, 1))
            name, ext = path.splitext(full_name)
            maxlen = FILE_NAME_FULL_MAX_LEN - len(full_path)
            if not re_fullmatch(r'^(?:[a-z]{2}_)?(?:\d+?)[.].+?$', full_name):
                continue
            untagged_name_noext = re_sub(r'^([a-z]{2}_)?(\d+?)[_.].+?$', r'\1\2', name)
            try:
                tags = tagdict[name[3:] if name[0].isalpha() else name]
            except Exception:
                continue
            score_str, tags_rest = tuple(tags.split(' ', 1))
            add_str = append_filtered_tags(score_str, tags_rest, re_tags_to_process, re_tags_to_exclude)
            new_name = trim_undersores(f'{untagged_name_noext}{UNDERSCORE}{add_str if len(add_str) <= maxlen else add_str[:maxlen]}')
            new_name = f'{base_path}{SLASH}{new_name}{ext}'
            rename_file(full_path, new_name)
            retagged_count += 1
    except Exception:
        pass

    return retagged_count

#
#
#########################################
