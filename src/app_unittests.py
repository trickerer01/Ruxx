# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
import os
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main as run_tests

# internal
from app_cmdargs import prepare_arglist
from app_defines import DATE_MIN_DEFAULT, DEFAULT_HEADERS, MODULE_CHOICES, DownloadModes, ItemInfo, ThreadInterruptException
from app_downloaders import DOWNLOADERS_BY_PROC_MODULE, make_downloader
from app_file_parser import IDSTRING_PATTERNS, IDVAL_EQ_SEPARATORS, PREFIX_OPTIONAL_PATTERNS
from app_logger import Logger
from app_module import ProcModule
from app_revision import APP_NAME
from app_tagger import TAG_ALIASES, TagsDB, load_tag_aliases
from app_tags_parser import RE_ANDGR_FULL, RE_FAVS, RE_METAS, RE_ORGRS_FULL, RE_ORGRS_FULL_S, RE_PLAINS, RE_POOLS, RE_SORTS, parse_tags
from app_task import MAX_NEGATIVE_TAGS, MAX_STRING_LENGTHS, MAX_WILDCARDS
from app_utils import normalize_path

__all__ = ('run_all_tests',)


RUN_CONN_TESTS = 0
CUR_PATH = normalize_path(os.path.abspath(os.curdir))

args_argparse_str01 = (
    'sfw asd ned -nds -proxr '
    '-timeout 13 -retries 56 -dmode full -skip_img -skip_vid -lowres -noproxy -proxynodown -prefix -dump_tags -dump_sources -append_info'
)
args_argparse_str02_base = (
    'sfw asd ned -nds -proxt '
    '-threads 8 -proxy http://8.8.8.8:65333 '
    '-headers {"name1":"value1"} -cookies {"name2":"value2"} '
    '-api_key '
    'unut3uuuu832c423chc239c42c4go923cg43o9hASdhjkhkdhr2y938y51397592365183489yry2hy9y489cy239c2c8962c936c59823c68y65bvgsik65783y8123,5555 '
    '-path ' + CUR_PATH
)
args_argparse_str02 = args_argparse_str02_base + ' -mindate 31-12-1950 -maxdate 01-01-2038'
args_argparse_str03 = args_argparse_str02 + ' sort:score'
args_argparse_str04 = args_argparse_str02_base + ' sort:score:desc score:40'
args_argparse_str05 = args_argparse_str02_base + ' -header name2=value2'
args_argparse_str06 = args_argparse_str05 + ' -header Name1=value3 -header NAME2=value4'
args_argparse_str07 = args_argparse_str01 + ' favorited_by:25000'
args_argparse_str08 = args_argparse_str01 + ' -merge_lists'
args_argparse_str09 = args_argparse_str08 + ' -merge_lists -dump_per_item'
args_argparse_str10 = args_argparse_str01 + ' pool:33600'
args_argparse_str11 = args_argparse_str10 + ' favorited_by:25000'
args_tagparse_str1 = (
    'sfw asd ned -nds -proxr sort:id sord:score:asc -rating:explicit score:90 '
    '(t1~t2~t3) (t4~t5) -(t6,t7) -(t8,t9,t10) -(t?1,t*2|t?3|t11,t12*,*t13)'
)
item_str01_rx = (
    '<post height="1291" score="27" file_url="/images/6898/76dfed93372eb7a373ffe2430379cfb1.jpeg" parent_id="90002" '
    'sample_url="/preview/6898/76dfed93372eb7a373ffe2430379cfb1.jpeg" sample_width="961" sample_height="1291" '
    'preview_url="/thumbnails/6898/thumbnail_76dfed93372eb7a373ffe2430379cfb1.jpg" rating="s" '
    'tags=" clothing female female_only flower heart long_hair safe sfw " id="7869261" width="961" change="1683351206" '
    'md5="76dfed93372eb7a373ffe2430379cfb1" creator_id="1825071" has_children="false" created_at="Sat May 06 07:33:08 +0200 2023" '
    'status="active" source="Twitter/safe" has_notes="false" has_comments="false" preview_width="111" preview_height="150"/>'
)
item_str01_rn = (
    '<a href="/post/view/427251" class="thumb shm-thumb shm-thumb-link " data-tags="marnie_(pokemon) pokemon ryumigin" '
    'data-height="1200" data-width="848" data-mime="image/png" data-post-id="427251"><img id="thumb_427251" '
    'title="Marnie_(Pokemon) Pokemon RyumiGin // 848x1200 // 1.2MB // png" '
    'alt="Marnie_(Pokemon) Pokemon RyumiGin // 848x1200 // 1.2MB // png" '
    'height="170" width="120"src="/_thumbs/00c90baef0be3a687f37e70c0a1bb291/thumb.jpg"></a>'
)
item_str01_rs = (
    '<div style="border-radius: 3px; margin: 0px 10px 15px 10px; overflow: hidden; height: 200px; "><a id="7939303" '
    'href="/index.php?r=posts/view&amp;id=7939303"><img  src="/thumbnails/bf/77/thumbnail_bf771345fb58e7ad19087320dc56d76e.jpg" '
    'title="1boy, 1girls, 3d, i love you, kakegurui, kissing, koikatsu, outside, safe, sfw, valentine&#039;s day" '
    'alt="Image: 7939303" style="width: 220px; height: 100%; object-fit: cover; object-position: center;"/></a></div>'
)
item_str01_rp = (
    '<posts count="1" offset="0"><tag author="TinyToonFan9" date="2024-07-26 04:52:59" file_name="1f7aa65042312f.jpg" '
    'file_url="/96/ff/96ff9088317591963b1f7aa65042312f" height="1663" id="6436541" md5="96ff9088317591963b1f7aa65042312f" '
    'preview_height="192" preview_url="/_thumbs/96ff9088317591963b1f7aa65042312f/thumb.jpg" preview_width="115" rating="?" '
    'score="0" source="Zesker-1071936-Ysera_-_World_of_Warcraft.jpg" tags="World_of_Warcraft Ysera Zeskerr" width="1000"></tag></posts>'
)
item_str01_en = (
    '<post_id="4322823" height="1244" width="800" file_url="/data/12/64/1264043fc5d61a7268b1caa3fd12e972.jpg" '
    'sample_url="/data/12/64/1264043fc5d61a7268b1caa3fd12e972.jpg" created_at="2023-09-30T09:28:22.753-04:00" '
    'score="237" has_children="true" parent_id="" comment_count="0" tags="2_horns 5_fingers">'
)
item_str01_xb = (
    '<post height="877" score="1" file_url="/images/666/f0ed148c17e0beb2a4c321098522cdde.jpeg" parent_id="" '
    'sample_url="/samples/666/sample_f0ed148c17e0beb2a4c321098522cdde.jpg" sample_width="850" sample_height="478" '
    'preview_url="/thumbnails/666/thumbnail_f0ed148c17e0beb2a4c321098522cdde.jpg" rating="q" '
    'tags=" 2_girls dragon_girl fainxel green_hair horns yuri " id="1096716" width="1560" change="1723755726" '
    'md5="f0ed148c17e0beb2a4c321098522cdde" creator_id="22119" has_children="false" created_at="Thu Aug 15 23:02:04 +0200 2024" '
    'status="active" source="Pixiv" has_notes="false" has_comments="false" preview_width="150" preview_height="84"/>'
)


class DataStructureIntegrityTests(TestCase):
    def test_integrity01_iteminfo(self) -> None:
        Logger.init(True, True)
        self.assertSetEqual({'source', 'comments', 'score', 'has_children', 'parent_id'}, ItemInfo.optional_slots)
        print(f'{self._testMethodName} passed')

    def test_integrity02_procmodule_dicts(self) -> None:
        Logger.init(True, True)
        self.assertEqual(1, ProcModule.PROC_MODULE_MIN)
        self.assertEqual(7, ProcModule.PROC_MODULE_MAX)
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(ProcModule.PROC_MODULES_BY_NAME))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(ProcModule.PROC_MODULES_NAMES_BY_ID))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(MAX_STRING_LENGTHS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(MAX_NEGATIVE_TAGS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(MAX_WILDCARDS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_PLAINS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_METAS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_SORTS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_FAVS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_POOLS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_ORGRS_FULL))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_ORGRS_FULL_S))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(RE_ANDGR_FULL))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(IDVAL_EQ_SEPARATORS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(IDSTRING_PATTERNS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(PREFIX_OPTIONAL_PATTERNS))
        self.assertEqual(ProcModule.PROC_MODULE_MAX, len(DOWNLOADERS_BY_PROC_MODULE))
        print(f'{self._testMethodName} passed')


class FileCheckTests(TestCase):
    def test_filecheck01_aliases(self) -> None:
        Logger.init(True, True)
        load_tag_aliases()
        self.assertIsNone(TAG_ALIASES.get(''))
        print(f'{self._testMethodName} passed')

    def test_filecheck02_tags(self) -> None:
        Logger.init(True, True)
        TagsDB.try_set_basepath('', traverse=False)
        self.assertEqual(len(MODULE_CHOICES), len(TagsDB.DBFiles))
        print(f'{self._testMethodName} passed')

    def test_filecheck03_tags_load(self) -> None:
        Logger.init(True, True)
        TagsDB.try_set_basepath('', traverse=False)
        for module in MODULE_CHOICES:
            TagsDB._load(module)
            self.assertGreater(len(TagsDB.DB[module]), 0, msg=f'{self._testMethodName} for module \'{module}\' failed')
        print(f'{self._testMethodName} passed')


class ArgParseTests(TestCase):
    def test_argparse01(self) -> None:
        # 5 tags and all bools, try to intersect
        ProcModule.set(ProcModule.RX)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        self.assertIsNotNone(arglist.tags)
        # print(str(arglist.tags))
        self.assertEqual(5, len(arglist.tags))
        print(f'{self._testMethodName} passed')

    def test_argparse02(self) -> None:
        # 5 tags, value types check
        ProcModule.set(ProcModule.RX)
        args = args_argparse_str02
        arglist = prepare_arglist(args.split())
        self.assertIsNotNone(arglist.tags)
        self.assertEqual(5, len(arglist.tags))
        self.assertIsNotNone(arglist.mindate)
        self.assertIsNotNone(arglist.maxdate)
        self.assertIsNotNone(arglist.threads)
        self.assertIsNotNone(arglist.path)
        self.assertIsNotNone(arglist.proxy)
        self.assertIsNotNone(arglist.headers)
        self.assertIsNotNone(arglist.cookies)
        self.assertIsNotNone(arglist.api_key)
        print(f'{self._testMethodName} passed')


class TagParseTests(TestCase):
    def test_tagparse01(self) -> None:
        ProcModule.set(ProcModule.RX)
        args = args_tagparse_str1
        res, tags = parse_tags(args)
        self.assertTrue(res)
        self.assertEqual(14, len(tags))
        print(f'{self._testMethodName} passed')


class LoggerTests(TestCase):
    def test_log01(self) -> None:
        Logger.init(True, False)
        Logger.log('‴﴾₽ὁﻼé₼☼ἦ﴿‴', True, True)
        print(f'{self._testMethodName} passed')


class DownloaderBaseTests(TestCase):
    def test_item01_rx(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('7869261', dwn._extract_id(dwn._local_addr_from_string(item_str01_rx)))
            self.assertEqual('06-05-2023', dwn._extract_post_date(item_str01_rx))
        print(f'{self._testMethodName} passed')

    def test_item01_rn(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RN) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('427251', dwn._extract_id(item_str01_rn))
        print(f'{self._testMethodName} passed')

    def test_item01_rs(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RS) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('7939303', dwn._extract_id(dwn._local_addr_from_string(item_str01_rs)))
            self.assertEqual(DATE_MIN_DEFAULT, dwn._extract_post_date(item_str01_rs))
        print(f'{self._testMethodName} passed')

    def test_item01_rp(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RP) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('6436541', dwn._extract_id(item_str01_rp))
            self.assertEqual('26-07-2024', dwn._extract_post_date(item_str01_rp))
        print(f'{self._testMethodName} passed')

    def test_item01_en(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.EN) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('4322823', dwn._extract_id(item_str01_en))
            self.assertEqual('30-09-2023', dwn._extract_post_date(item_str01_en))
        print(f'{self._testMethodName} passed')

    def test_item01_xb(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.XB) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual('1096716', dwn._extract_id(dwn._local_addr_from_string(item_str01_xb)))
            self.assertEqual('15-08-2024', dwn._extract_post_date(item_str01_xb))
        print(f'{self._testMethodName} passed')

    def test_cmdline01(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str01
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual(5, dwn.get_tags_count())
            self.assertEqual(13, dwn.timeout)
            self.assertEqual(56, dwn.retries)
            self.assertEqual(DownloadModes.FULL, dwn.download_mode)
            self.assertTrue(dwn.skip_images)
            self.assertTrue(dwn.skip_videos)
            self.assertFalse(dwn.prefer_webm)
            self.assertTrue(dwn.low_res)
            self.assertTrue(dwn.ignore_proxy)
            self.assertTrue(dwn.ignore_proxy_dwn)
            self.assertTrue(dwn.add_filename_prefix)
            self.assertTrue(dwn.dump_tags)
            self.assertTrue(dwn.dump_sources)
            self.assertTrue(dwn.append_info)
        print(f'{self._testMethodName} passed')

    def test_cmdline02(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str02
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual(5, dwn.get_tags_count())
            self.assertEqual('31-12-1950', dwn.date_min)
            self.assertEqual('01-01-2038', dwn.date_max)
            self.assertEqual(8, dwn.maxthreads_items)
            self.assertEqual(CUR_PATH, dwn.dest_base_s)
            self.assertEqual('http://8.8.8.8:65333', dwn.proxies.get('http'))
            self.assertEqual('http://8.8.8.8:65333', dwn.proxies.get('https'))
            self.assertEqual('value1', dwn.add_headers.get('name1'))
            self.assertEqual('value2', dwn.add_cookies.get('name2'))
            self.assertEqual('5555', dwn.api_key.user_id)
        print(f'{self._testMethodName} passed')

    def test_cmdline03(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str03
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            self.assertRaises(ThreadInterruptException, dwn._parse_args, arglist)
        print(f'{self._testMethodName} passed')

    def test_cmdline04(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str04
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertFalse(dwn.default_sort)
            self.assertEqual(7, dwn.get_tags_count())
        print(f'{self._testMethodName} passed')

    def test_cmdline05(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str05
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual(2, len(dwn.add_headers))
        print(f'{self._testMethodName} passed')

    def test_cmdline06(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str06
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            self.assertEqual(2, len(dwn.add_headers))
            self.assertEqual('value3', dwn.add_headers['name1'])
            self.assertEqual('value4', dwn.add_headers['name2'])
        print(f'{self._testMethodName} passed')

    def test_cmdline07(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str07
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist, False)
            self.assertEqual('25000', dwn.favorites_search_user)
        print(f'{self._testMethodName} passed')

    def test_cmdline08(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str08
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist, False)
            self.assertTrue(dwn.merge_lists)
        print(f'{self._testMethodName} passed')

    def test_cmdline09(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str09
        self.assertRaises(BaseException, prepare_arglist, args.split())
        print(f'{self._testMethodName} passed')

    def test_cmdline10(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str10
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist, False)
            self.assertEqual('33600', dwn.pool_search_str)
        print(f'{self._testMethodName} passed')

    def test_cmdline11(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str11
        arglist = prepare_arglist(args.split())
        with make_downloader(ProcModule.RX) as dwn:
            self.assertRaises(AssertionError, dwn._parse_args, arglist, False)
        print(f'{self._testMethodName} passed')


# Tests below require actual connection

class ConnTests(TestCase):
    def test_connect_rx01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for rx is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        #                tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id:=2000000', '-severals', '-dmode', 'skip', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RX) as dwn:
            dwn._parse_args(arglist)
            dwn.url = dwn._form_tags_search_address(dwn._consume_custom_module_tags(dwn.tags_str_arr[0]))
            dwn.total_count = dwn._get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')

    def test_connect_rs01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for rx is performed using same web address, we are free to use dry run here
        Logger.init(True, True)
        #                tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id:=7939303', '-severals', '-dmode', 'skip', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RS) as dwn:
            dwn._parse_args(arglist)
            dwn.url = dwn._form_tags_search_address(dwn._consume_custom_module_tags(dwn.tags_str_arr[0]))
            dwn.total_count = dwn._get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')

    def test_connect_rp01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for rx is performed using same web address, we are free to use dry run here
        Logger.init(True, True)
        #               tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id=5915464', '-severals', '-dmode', 'skip', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RP) as dwn:
            dwn._parse_args(arglist)
            dwn.url = dwn._form_tags_search_address(dwn._consume_custom_module_tags(dwn.tags_str_arr[0]))
            dwn.total_count = dwn._get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')

    def test_connect_en01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for rx is performed using same web address, we are free to use dry run here
        Logger.init(True, True)
        #               tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id:4322823', '-severals', '-dmode', 'skip', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.EN) as dwn:
            dwn._parse_args(arglist)
            dwn.url = dwn._form_tags_search_address(dwn._consume_custom_module_tags(dwn.tags_str_arr[0]))
            dwn.total_count = dwn._get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')

    def test_connect_xb01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for xb is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        #                tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id:=1010000', '-severals', '-dmode', 'skip', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.XB) as dwn:
            dwn._parse_args(arglist)
            dwn.url = dwn._form_tags_search_address(dwn._consume_custom_module_tags(dwn.tags_str_arr[0]))
            dwn.total_count = dwn._get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')


class ItemFilterTests(TestCase):
    def test_filter_rx01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        Logger.init(True, True)
        #              tag         flag       v       flag      v     flag      v         flag          v           flag          v
        argslist = ('moonlight', '-dmode', 'skip', '-threads', '8', '-path', CUR_PATH, '-mindate', '01-01-2012', '-maxdate', '01-12-2023')
        # this search yields at least 3200 results (before date filter)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RX) as dwn:
            dwn.launch_download(arglist)
            # self.assertEqual(3015, len(dwn.item_info_dict_all))  # may change too frequently
            self.assertEqual('9081766', next(iter(dwn.item_info_dict_all.values())).id)
            self.assertEqual('963172', next(reversed(dwn.item_info_dict_all.values())).id)
        print(f'{self._testMethodName} passed')


class RealDownloadTests(TestCase):
    def test_down_rx01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for rx is performed using same web address, we are free to use dry run here
        Logger.init(True, True)
        #                tag           tag        flag       v       flag      v      flag            v           flag      v
        argslist = ('id:=2000000', '-overflow', '-dmode', 'skip', '-threads', '2', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RX) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(dwn.fail_count == 0, f'dwn.failCount {dwn.fail_count:d} == 0')
            self.assertTrue(dwn.processed_count == 1, f'dwn.processed_count {dwn.fail_count:d} == 1')
        print(f'{self._testMethodName} passed')

    def test_down_rx02(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        tempfile_id = '6579460'
        tempfile_ext = 'png'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag               flag      v      flag            v           flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RX) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_rs01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        tempfile_id = '7939303'
        tempfile_ext = 'png'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag               flag      v      flag            v           flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RS) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_rs02_fav1(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        fav_user_id = '59309'
        tempfile_id = '6511644'
        tempfile_ext = 'jpeg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag                        flag      v      flag            v           flag      v
        argslist = (f'favorited_by:{fav_user_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RS) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_rp01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        tempfile_id = '5915464'
        tempfile_ext = 'jpg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag              flag      v      flag            v           flag      v
        argslist = (f'id={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RP) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_rp02_fav1(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        fav_user = 'avoidthenoid'
        tempfile_id = '440995'
        tempfile_ext = 'jpg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                 tag                      flag      v      flag            v           flag      v
        argslist = (f'favorited_by={fav_user}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.RP) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_en01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        tempfile_id = '4322823'
        tempfile_ext = 'jpg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag              flag      v      flag            v           flag      v
        argslist = (f'id:{tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.EN) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_en02_fav1(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        fav_user_id = '40533'
        tempfile_id = '3539510'
        tempfile_ext = 'webm'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                 tag                          flag      v      flag            v           flag      v
        argslist = (f'favorited_by:!{fav_user_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.EN) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_en03_fav2(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        fav_user_name = 'link901'
        tempfile_id = '3539510'
        tempfile_ext = 'webm'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                 tag                          flag      v      flag            v           flag      v
        argslist = (f'favoritedby:{fav_user_name}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.EN) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_xb01(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # connection and downloading for xb is performed using same web address, we are free to use dry run here
        Logger.init(True, True)
        #                tag           tag        flag       v       flag      v      flag            v           flag       v
        argslist = ('id:=1010000', '-overflow', '-dmode', 'skip', '-threads', '2', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.XB) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(dwn.fail_count == 0, f'dwn.failCount {dwn.fail_count:d} == 0')
            self.assertTrue(dwn.processed_count == 1, f'dwn.processed_count {dwn.fail_count:d} == 1')
        print(f'{self._testMethodName} passed')

    def test_down_xb02(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        tempfile_id = '789585'
        tempfile_ext = 'jpeg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                  tag               flag      v      flag            v           flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.XB) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_xb03_fav1(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        fav_user_id = '87266'
        tempfile_id = '845348'
        tempfile_ext = 'jpeg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                 tag                          flag      v      flag            v           flag      v
        argslist = (f'favorited_by:{fav_user_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.XB) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')

    def test_down_xb04_pool1(self) -> None:
        if not RUN_CONN_TESTS:
            return
        # this test actually performs a download
        pool_id = '689'
        tempfile_id = '733305'
        tempfile_ext = 'jpeg'
        tdir = TemporaryDirectory(prefix=f'{APP_NAME}_{self._testMethodName}_')
        tempdir = normalize_path(tdir.name)
        tempfile_path = f'{normalize_path(tempdir)}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        #                 tag                          flag      v      flag            v           flag      v
        argslist = (f'pool:{pool_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', tempdir)
        arglist = prepare_arglist(argslist)
        with make_downloader(ProcModule.XB) as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(os.path.isfile(tempfile_path))
        tdir.cleanup()
        print(f'{self._testMethodName} passed')


def run_all_tests() -> None:
    res = run_tests(module='app_unittests', exit=False)
    if not res.result.wasSuccessful():
        print('Fail')
        sys.exit(-1)

#
#
#########################################
