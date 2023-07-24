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
from unittest import main as run_tests, TestCase
from tempfile import gettempdir

# internal
from app_cmdargs import prepare_arglist
from app_defines import DEFAULT_HEADERS, DownloadModes
from app_download_rx import DownloaderRx
from app_logger import Logger
from app_utils import normalize_path

__all__ = ('run_all_tests',)


CUR_PATH = normalize_path(path.abspath(curdir))

args_argparse_str1 = (
    'sfw asd ned -nds -proxr '
    '-dmode 0 -skip_img -skip_vid -webm -lowres -noproxy -proxynodown -socks -prefix -dump_tags -dump_sources -append_info'
)
args_argparse_str2 = (
    'sfw asd ned -nds -proxt '
    '-low 123 -high 987 -mindate 1950-12-31 -maxdate 2038-01-01 -threads 8 -proxy 8.8.8.8:65333 '
    '-headers {"name1":"value1"} -cookies {"name2":"value2"} '
    '-path ' + CUR_PATH
)


class ArgParseTests(TestCase):
    def test_argparse1(self) -> None:
        # 5 tags and all bools, try to intersect
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        self.assertIsNotNone(arglist.tags)
        self.assertEqual(len(arglist.tags), 5)
        print('test_argparse1 passed')

    def test_argparse2(self) -> None:
        # 5 tags, value types check
        args = args_argparse_str2
        arglist = prepare_arglist(args.split())
        self.assertIsNotNone(arglist.tags)
        self.assertEqual(len(arglist.tags), 5)
        self.assertIsNotNone(arglist.low)
        self.assertIsNotNone(arglist.high)
        self.assertIsNotNone(arglist.mindate)
        self.assertIsNotNone(arglist.maxdate)
        self.assertIsNotNone(arglist.threads)
        self.assertIsNotNone(arglist.path)
        self.assertIsNotNone(arglist.proxy)
        self.assertIsNotNone(arglist.headers)
        self.assertIsNotNone(arglist.cookies)
        print('test_argparse2 passed')


class DownloaderBaseTests(TestCase):
    def test_cmdline1(self) -> None:
        args = args_argparse_str1
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual(dwn.get_tags_count(), 5)
            self.assertEqual(dwn.download_mode, DownloadModes.DOWNLOAD_FULL)
            self.assertEqual(dwn.skip_images, True)
            self.assertEqual(dwn.skip_videos, True)
            self.assertEqual(dwn.prefer_webm, True)
            self.assertEqual(dwn.low_res, True)
            self.assertEqual(dwn.ignore_proxy, True)
            self.assertEqual(dwn.ignore_proxy_dwn, True)
            self.assertEqual(dwn.socks, True)
            self.assertEqual(dwn.add_filename_prefix, True)
            self.assertEqual(dwn.dump_tags, True)
            self.assertEqual(dwn.dump_source, True)
            self.assertEqual(dwn.append_info, True)
        print('test_cmdline1 passed')

    def test_cmdline2(self) -> None:
        args = args_argparse_str2
        arglist = prepare_arglist(args.split())
        with DownloaderRx() as dwn:
            dwn.parse_args(arglist)
            self.assertEqual(dwn.get_tags_count(), 5)
            self.assertEqual(dwn.lower_bound, 123)
            self.assertEqual(dwn.upper_bound, 987)
            self.assertEqual(dwn.date_min, '1950-12-31')
            self.assertEqual(dwn.date_max, '2038-01-01')
            self.assertEqual(dwn.maxthreads_items, 8)
            self.assertEqual(dwn.dest_base, CUR_PATH)
            self.assertEqual(dwn.proxies.get('all'), 'http://8.8.8.8:65333')
            self.assertEqual(dwn.add_headers.get('name1'), 'value1')
            self.assertEqual(dwn.add_cookies.get('name2'), 'value2')
        print('test_cmdline2 passed')


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
            self.assertEqual(dwn.total_count, 1)
        print('test_connect_rx1 passed')


class DownloadTests(TestCase):
    def test_down_rx1(self) -> None:
        # connection and downloading for rx is performed using same web address, we are free to use dry run here (-dmode 1)
        Logger.init(True, True)
        # ____empty,  tag,             tag,       flag,    v,     flag,     v,     flag,         v             flag      v
        argslist = ('id:=2000000', '-overflow', '-dmode', '1', '-threads', '2', '-headers', DEFAULT_HEADERS, '-path', CUR_PATH)
        arglist = prepare_arglist(argslist)
        with DownloaderRx() as dwn:
            dwn.launch(arglist)
            self.assertTrue(dwn.fail_count == 0, f'dwn.failCount {dwn.fail_count:d} == 0')
            self.assertTrue(dwn.processed_count == 1, f'dwn.processed_count {dwn.fail_count:d} == 1')
        print('test_down_rx1 passed')

    def test_down_rx2(self) -> None:
        # this test actually performs a download
        tempfile_id = str(6579460)
        tempfile_ext = 'png'
        tempfile_path = f'{normalize_path(gettempdir())}{tempfile_id}.{tempfile_ext}'
        Logger.init(True, True)
        # ____empty,  tag,            flag,     v,     flag,         v             flag      v
        argslist = (f'id:={tempfile_id}', '-threads', '1', '-headers', DEFAULT_HEADERS, '-path', gettempdir())
        arglist = prepare_arglist(argslist)
        with DownloaderRx() as dwn:
            dwn.launch(arglist)
            self.assertTrue(path.isfile(tempfile_path))
            remove_file(tempfile_path)
        print('test_down_rx2 passed')


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
