# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from os import path, curdir, remove as remove_file
from sys import exit as sysexit
from tempfile import gettempdir
from unittest import main as run_tests, TestCase

# internal
from app_cmdargs import prepare_arglist
from app_defines import DEFAULT_HEADERS, DownloadModes, ThreadInterruptException, DATE_MIN_DEFAULT
from app_download_rn import DownloaderRn
from app_download_rs import DownloaderRs
from app_download_rx import DownloaderRx
from app_logger import Logger
from app_utils import normalize_path

__all__ = ('run_all_tests',)


CUR_PATH = normalize_path(path.abspath(curdir))

args_argparse_str1 = (
    'sfw asd ned -nds -proxr '
    '-timeout 13 -retries 56 -dmode 0 -skip_img -skip_vid -lowres -noproxy -proxynodown -prefix -dump_tags -dump_sources -append_info'
)
args_argparse_str2_base = (
    'sfw asd ned -nds -proxt '
    '-threads 8 -proxy http://8.8.8.8:65333 '
    '-headers {"name1":"value1"} -cookies {"name2":"value2"} '
    '-path ' + CUR_PATH
)
args_argparse_str2 = args_argparse_str2_base + ' -mindate 31-12-1950 -maxdate 01-01-2038'
args_argparse_str3 = args_argparse_str2 + ' sort:score'
args_argparse_str4 = args_argparse_str2_base + ' sort:score:desc score:40'
item_str1_rx = (
    '<post height="1291" score="27" file_url="/images/6898/76dfed93372eb7a373ffe2430379cfb1.jpeg" parent_id="90002"'
    ' sample_url="/preview/6898/76dfed93372eb7a373ffe2430379cfb1.jpeg" sample_width="961" sample_height="1291"'
    ' preview_url="/thumbnails/6898/thumbnail_76dfed93372eb7a373ffe2430379cfb1.jpg" rating="s"'
    ' tags=" clothing female female_only flower heart long_hair safe sfw " id="7869261" width="961" change="1683351206"'
    ' md5="76dfed93372eb7a373ffe2430379cfb1" creator_id="1825071" has_children="false" created_at="Sat May 06 07:33:08 +0200 2023"'
    ' status="active" source="Twitter/safe" has_notes="false" has_comments="false" preview_width="111" preview_height="150"/>'
)
item_str1_rn = (
    '<a href="/post/view/427251" class="thumb shm-thumb shm-thumb-link " data-tags="marnie_(pokemon) pokemon ryumigin"'
    ' data-height="1200" data-width="848" data-mime="image/png" data-post-id="427251"><img id="thumb_427251"'
    ' title="Marnie_(Pokemon) Pokemon RyumiGin // 848x1200 // 1.2MB // png"'
    ' alt="Marnie_(Pokemon) Pokemon RyumiGin // 848x1200 // 1.2MB // png"'
    '  height="170" width="120"src="/_thumbs/00c90baef0be3a687f37e70c0a1bb291/thumb.jpg"></a>'
)
item_str1_rs = (
    '<div style="border-radius: 3px; margin: 0px 10px 15px 10px; overflow: hidden; height: 200px; "><a id="7939303"'
    ' href="/index.php?r=posts/view&amp;id=7939303"><img  src="/thumbnails/bf/77/thumbnail_bf771345fb58e7ad19087320dc56d76e.jpg"'
    ' title="1boy, 1girls, 3d, i love you, kakegurui, kissing, koikatsu, outside, safe, sfw, valentine&#039;s day"'
    ' alt="Image: 7939303" style="width: 220px; height: 100%; object-fit: cover; object-position: center;"/></a></div>'
)


class ArgParseTests(TestCase):
    def test_argparse1(self) -> None:
        # 5 tags and all bools, try to intersect
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        self.assertIsNotNone(arglist.tags)
        # print(str(arglist.tags))
        self.assertEqual(5, len(arglist.tags))
        print(f'{self._testMethodName} passed')

    def test_argparse2(self) -> None:
        # 5 tags, value types check
        args = args_argparse_str2
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
        print(f'{self._testMethodName} passed')


class DownloaderBaseTests(TestCase):
    def test_item1_rx(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual('7869261', dwn._extract_id(dwn._local_addr_from_string(item_str1_rx)))
            self.assertEqual('06-05-2023', dwn._extract_post_date(item_str1_rx))
        print(f'{self._testMethodName} passed')

    def test_item1_rn(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        with DownloaderRn() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual('427251', dwn._extract_id(item_str1_rn))
        print(f'{self._testMethodName} passed')

    def test_item1_rs(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        with DownloaderRs() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual('7939303', dwn._extract_id(dwn._local_addr_from_string(item_str1_rs)))
            self.assertEqual(DATE_MIN_DEFAULT, dwn._extract_post_date(item_str1_rs))
        print(f'{self._testMethodName} passed')

    def test_cmdline1(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual(5, dwn.get_tags_count())
            self.assertEqual(13, dwn.timeout)
            self.assertEqual(56, dwn.retries)
            self.assertEqual(DownloadModes.DOWNLOAD_FULL, dwn.download_mode)
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

    def test_cmdline2(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str2
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual(5, dwn.get_tags_count())
            self.assertEqual('31-12-1950', dwn.date_min)
            self.assertEqual('01-01-2038', dwn.date_max)
            self.assertEqual(8, dwn.maxthreads_items)
            self.assertEqual(CUR_PATH, dwn.dest_base)
            self.assertEqual('http://8.8.8.8:65333', dwn.proxies.get('http'))
            self.assertEqual('http://8.8.8.8:65333', dwn.proxies.get('https'))
            self.assertEqual('value1', dwn.add_headers.get('name1'))
            self.assertEqual('value2', dwn.add_cookies.get('name2'))
        print(f'{self._testMethodName} passed')

    def test_cmdline3(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str3
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            self.assertRaises(ThreadInterruptException, dwn.parse_args, arglist)
        print(f'{self._testMethodName} passed')

    def test_cmdline4(self) -> None:
        Logger.init(True, True)
        args = args_argparse_str4
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertFalse(dwn.default_sort)
            self.assertEqual(7, dwn.get_tags_count())
        print(f'{self._testMethodName} passed')


# Tests below require actual connection

class ConnTests(TestCase):
    def test_connect_rx1(self) -> None:
        # connection and downloading for rx is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        # ____empty,  tag,             tag,       flag,    v,     flag,     v,     flag,         v             flag      v
        argslist = ('id:=2000000', '-severals', '-dmode', '1', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            dwn.url = dwn.form_tags_search_address(dwn.tags_str_arr[0])
            dwn.total_count = dwn.get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')

    def test_connect_rs1(self) -> None:
        # connection and downloading for rx is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        # ____empty,  tag,             tag,       flag,    v,     flag,     v,     flag,         v             flag      v
        argslist = ('id:=7939303', '-severals', '-dmode', '1', '-threads', '3', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with DownloaderRs() as dwn:
            dwn.parse_args(arglist)
            dwn.url = dwn.form_tags_search_address(dwn.tags_str_arr[0])
            dwn.total_count = dwn.get_items_query_size_or_html(dwn.url)
            self.assertEqual(1, dwn.total_count)
        print(f'{self._testMethodName} passed')


class DownloadTests(TestCase):
    def test_down_rx1(self) -> None:
        # connection and downloading for rx is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        # ____empty,  tag,             tag,       flag,    v,     flag,     v,     flag,         v             flag      v
        argslist = ('id:=2000000', '-overflow', '-dmode', '1', '-threads', '2', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with DownloaderRx() as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(dwn.fail_count == 0, f'dwn.failCount {dwn.fail_count:d} == 0')
            self.assertTrue(dwn.processed_count == 1, f'dwn.processed_count {dwn.fail_count:d} == 1')
        print(f'{self._testMethodName} passed')

    def test_down_rx2(self) -> None:
        # this test actually performs a download
        tempfile_id = str(6579460)
        tempfile_ext = 'png'
        tempfile_path = f'{normalize_path(gettempdir())}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        # ____empty,  tag,                   flag,     v,     flag,         v             flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', gettempdir())
        arglist = prepare_arglist(argslist)
        with DownloaderRx() as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(path.isfile(tempfile_path))
            remove_file(tempfile_path)
        print(f'{self._testMethodName} passed')

    def test_down_rs1(self) -> None:
        # this test actually performs a download
        tempfile_id = str(7939303)
        tempfile_ext = 'png'
        tempfile_path = f'{normalize_path(gettempdir())}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        # ____empty,  tag,                   flag,     v,     flag,         v             flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', gettempdir())
        arglist = prepare_arglist(argslist)
        with DownloaderRs() as dwn:
            dwn.launch_download(arglist)
            self.assertTrue(path.isfile(tempfile_path))
            remove_file(tempfile_path)
        print(f'{self._testMethodName} passed')


def run_all_tests() -> None:
    res = run_tests(module='app_unittests', exit=False)
    if not res.result.wasSuccessful():
        print('Fail')
        sysexit()


if __name__ == '__main__':
    run_all_tests()

#
#
#########################################
