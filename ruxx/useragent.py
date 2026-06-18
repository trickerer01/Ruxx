# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

import random

from fake_useragent import FakeUserAgent

from .vcs import __RUXX_DEBUG__


class UAManager:
    USER_AGENT_DEFAULT = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Goanna/6.7 Firefox/102.0 PaleMoon/33.3.1'
    _orig_useragent = ''

    @staticmethod
    def _generate() -> str:
        ua_generator = FakeUserAgent(browsers=('Firefox',), platforms=('desktop',), fallback=UAManager.USER_AGENT_DEFAULT)
        # noinspection PyProtectedMember
        user_agents = list(set(_['useragent'] for _ in ua_generator._filter_useragents()))
        return random.choice(user_agents)

    @staticmethod
    def orig_user_agent() -> str:
        UAManager._orig_useragent = UAManager._orig_useragent or (UAManager.USER_AGENT_DEFAULT if __RUXX_DEBUG__ else UAManager._generate())
        return UAManager._orig_useragent

    @staticmethod
    def orig_user_agent_as_header_json_str() -> str:
        return f'{{"User-Agent": "{UAManager.orig_user_agent()}"}}'

#
#
#########################################
