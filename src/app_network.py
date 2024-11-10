# coding=UTF-8
"""
Author: trickerer (https://github.com/trickerer, https://github.com/trickerer01)
"""
#########################################
#
#

# native
from __future__ import annotations
from abc import ABC, abstractmethod
from argparse import Namespace
from multiprocessing.dummy import current_process
from os import path, stat, remove
from re import compile as re_compile
from sys import exc_info
from threading import Thread, Lock as ThreadLock
from time import sleep as thread_sleep
from urllib.parse import urlparse
from warnings import filterwarnings

# requirements
from bs4 import BeautifulSoup
from requests import Session, Response, HTTPError, adapters
from requests.structures import CaseInsensitiveDict

# internal
from app_debug import __RUXX_DEBUG__
from app_defines import (
    ThreadInterruptException, DownloadModes, HtmlCacheMode, CONNECT_TIMEOUT_BASE, CONNECT_RETRIES_BASE, CONNECT_RETRIES_CHUNK,
    WRITE_CHUNK_SIZE, DOWNLOAD_CHUNK_SIZE, KNOWN_EXTENSIONS_VID,
)
from app_gui_defines import SLASH
from app_logger import trace
from app_module import ProcModule

__all__ = ('ThreadedHtmlWorker', 'DownloadInterruptException', 'thread_exit')

filterwarnings('ignore', category=UserWarning)

re_content_range_str = re_compile(r'bytes (\d+)-(\d+)?(?:/(\d+))?')


class DownloadInterruptException(BaseException):
    pass


class FileDownloadResult:
    def __init__(self) -> None:
        self.file_size: int = 0
        self.expected_size: int = 0
        self.retries: int = 0
        self.result_str: str = ''


def thread_exit(err_str='', code=-1) -> None:
    trace(f'Exiting with code {code:d}, message:\n{err_str}', True)
    thread_sleep(0.15)
    raise ThreadInterruptException


class ThreadedWorker(ABC):
    """
    ThreadedWorker !Abstract!
    """
    @abstractmethod
    def __init__(self) -> None:
        self.my_root_thread: Thread | None = None
        self.item_lock: ThreadLock = ThreadLock()
        self.items_all_lock: ThreadLock = ThreadLock()

    def reset_root_thread(self, thread: Thread) -> None:
        self.my_root_thread = thread

    def catch_cancel_or_ctrl_c(self, message: str = '') -> None:
        if self.is_killed():
            thread_exit(message, code=1)

    def is_killed(self) -> bool:
        return self.my_root_thread and getattr(self.my_root_thread, 'killed', False) is True


class ThreadedHtmlWorker(ThreadedWorker):
    """
    ThreadedHtmlWorker !Abstract!
    """
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self.verbose: bool = False
        self.raw_html_cache: dict[str, BeautifulSoup | bytes] = dict()
        self.cache_mode: HtmlCacheMode = HtmlCacheMode.CACHE_BYTES
        self.add_headers: CaseInsensitiveDict[str, str] = CaseInsensitiveDict()
        self.add_cookies: CaseInsensitiveDict[str, str] = CaseInsensitiveDict()
        self.ignore_proxy: bool = False
        self.ignore_proxy_dwn: bool = False
        self.proxies: dict[str, str] | None = None
        self.timeout: int = CONNECT_TIMEOUT_BASE
        self.retries: int = CONNECT_RETRIES_BASE
        self.etags: dict[str, str] = dict()
        self.session: Session | None = None

    @abstractmethod
    def _get_sitename(self) -> str:
        ...

    @abstractmethod
    def _get_module_specific_default_headers(self) -> dict[str, str]:
        ...

    @abstractmethod
    def _get_module_specific_default_cookies(self) -> dict[str, str]:
        ...

    def make_session(self) -> Session:
        s = Session()
        s.adapters.clear()
        s.mount('http://', adapters.HTTPAdapter(pool_maxsize=1, max_retries=0))
        s.mount('https://', adapters.HTTPAdapter(pool_maxsize=1, max_retries=0))
        s.keep_alive = True
        s.headers.update(self.add_headers.copy())
        s.headers['Referer'] = self._get_sitename()
        s.cookies.update(self.add_cookies.copy())
        if self.proxies and not self.ignore_proxy:
            s.proxies.update(self.proxies.copy())
        return s

    def _parse_args(self, args: Namespace) -> None:
        self.verbose = args.verbose or self.verbose
        self.cache_mode = HtmlCacheMode.CACHE_BS if args.cache_html_bloat else HtmlCacheMode.CACHE_BYTES
        self.ignore_proxy = args.noproxy or self.ignore_proxy
        self.ignore_proxy_dwn = args.proxynodown or self.ignore_proxy_dwn
        self.proxies = {'http': str(args.proxy), 'https': str(args.proxy)} if args.proxy else None
        self.timeout = args.timeout or self.timeout
        self.retries = args.retries or self.retries
        if args.headers:
            self.add_headers.update(args.headers)
        if args.cookies:
            self.add_cookies.update(args.cookies)
        for container_base, container_ext in zip((self.add_headers, self.add_cookies), (args.header, args.cookie)):
            pair: tuple[str, str]
            for pair in container_ext or []:
                if pair[0] in container_base:
                    trace(f'Warning (W1): Overriding json value at \'{pair[0]}\' from \'{container_base[pair[0]]}\' to \'{pair[1]}\'')
                container_base[pair[0]] = pair[1]
        self.add_headers.update(self._get_module_specific_default_headers())
        self.add_cookies.update(self._get_module_specific_default_cookies())
        self.session = self.make_session()

    # threaded
    def download_file(self, link: str, item_id: str, dest: str, mode=DownloadModes.FULL) -> FileDownloadResult:
        fullname = dest[dest.rfind(SLASH) + 1:]
        ext_full = fullname[fullname.rfind('.') + 1:]
        ext_char = ext_full[0]
        is_video_ext = ext_full in KNOWN_EXTENSIONS_VID
        touch_mode = mode == DownloadModes.TOUCH
        oldlink = link
        if ProcModule.is_rx():
            link = link.replace('api-cdn-mp4.', 'ws-cdn-video.')

        result = FileDownloadResult()
        result.result_str = f'[{current_process().name}]{" <touch>" if touch_mode else ""} {item_id}({ext_char})... '

        if touch_mode:
            with open(dest, 'wb'):
                pass
        elif mode == DownloadModes.FULL:
            with self.make_session() as s:
                s.stream = True
                while (not (path.isfile(dest) and result.file_size == result.expected_size)) and result.retries < self.retries:
                    if self.is_killed():
                        trace(f'{result.result_str} interrupted', True)
                        raise DownloadInterruptException
                    try:
                        def download_chunk(ofile, start: int, end: int, exp_size: int, chunk_num: int) -> None:
                            headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                       'Accept-Language': 'en-US,en;q=0.5',
                                       'Accept-Encoding': 'gzip, deflate, br',
                                       'DNT': '1',
                                       # 'Host': reqhost,
                                       'Connection': 'keep-alive'}
                            if not single_chunk:
                                headers['Range'] = f'bytes={start:d}-{end:d}'
                            headers.update(self.add_headers.copy())
                            req = s.request('GET', link, timeout=self.timeout, stream=True, headers=headers, allow_redirects=False)
                            req.raise_for_status()
                            temp = bytes()
                            for chunk_w in req.iter_content(WRITE_CHUNK_SIZE):
                                temp += chunk_w
                            req.close()
                            etag = req.headers.get('etag', item_id)
                            content_range = req.headers.get('content-range') if not single_chunk else None
                            content_range_m = re_content_range_str.search(content_range) if content_range else None
                            c_start = content_range_m.group(1) if content_range_m else '0'
                            c_end = content_range_m.group(2) if content_range_m else '0'
                            c_total = content_range_m.group(3) if content_range_m else '0'
                            valid_chunk = True
                            errcode = 0
                            if len(temp) != exp_size or (not single_chunk and int(c_total) != result.expected_size):
                                valid_chunk = False
                                errcode = 1
                            elif etag != self.etags.get(item_id):
                                valid_chunk = False
                                errcode = 2
                            elif not single_chunk and not content_range:
                                valid_chunk = False
                                errcode = 3
                            elif not single_chunk and not content_range_m:
                                valid_chunk = False
                                errcode = 4
                            elif int(c_start) != start or (not single_chunk and int(c_end) != end):
                                valid_chunk = False
                                errcode = 5
                            if valid_chunk is False:
                                if __RUXX_DEBUG__:
                                    trace(f'Warning (W2): {item_id} invalid chunk {chunk_num:d} err {errcode:d}', True)
                                # website may send not an HTTP error but instead just a mismatched chunk and call it good
                                severe_err = errcode in (1, 2, 3, 4)
                                response = Response()
                                response.status_code = 416 if severe_err else 417  # Expectation Failed
                                new_exc = HTTPError(response=response)
                                raise new_exc
                            ofile.write(temp)

                        sreq = s.request('HEAD', link, timeout=self.timeout, allow_redirects=False, headers={'Bytes': str(10**12)})
                        sreq.raise_for_status()
                        result.expected_size = int(sreq.headers.get('content-length', '0'))
                        self.etags[item_id] = sreq.headers.get('etag', item_id)
                        # this code was left here after link replacements had been removed. DO NOT MOVE
                        # reqhost = re_link_host.search(link).group(1)
                        sreq.close()

                        if result.expected_size == 0:
                            err_msg = f'Warning (W2): fetched {item_id}({ext_char}) file is empty.'
                            raise ValueError(err_msg)

                        use_chunked = is_video_ext if ProcModule.is_rx() else True
                        chunks = list(range(0, result.expected_size, DOWNLOAD_CHUNK_SIZE if use_chunked else result.expected_size))
                        single_chunk = (len(chunks) == 1)
                        with open(dest, 'wb') as outf:
                            i = 0
                            chunk_tries = 0
                            while i < len(chunks):
                                if self.is_killed():
                                    raise ThreadInterruptException
                                chunk_begin = chunks[i]
                                chunk_end = result.expected_size - 1 if i == len(chunks) - 1 else chunks[i + 1] - 1
                                expected_chunk_size = (chunk_end - chunk_begin) + 1
                                try:
                                    download_chunk(outf, chunk_begin, chunk_end, expected_chunk_size, i + 1)
                                except (KeyboardInterrupt, ThreadInterruptException) as err:
                                    raise err
                                except (HTTPError, Exception):
                                    if chunk_tries >= CONNECT_RETRIES_CHUNK:
                                        if __RUXX_DEBUG__:
                                            trace(f'Warning (W2): at {item_id} chunk {i + 1:d} catched too many HTTPError 416s!', True)
                                        break
                                    chunk_tries += 1
                                    sleep_time = 2
                                    if __RUXX_DEBUG__:
                                        exc_p1, exc_p2 = tuple(str(exc_info()[k]) for k in range(2))
                                        trace(f'Warning (W2): at {item_id} chunk {i + 1:d} catched {exc_p1}: {exc_p2} retrying...', True)
                                    thread_sleep(sleep_time)
                                    continue
                                chunk_tries = 0
                                i += 1

                        result.file_size = stat(dest).st_size
                        if result.file_size != result.expected_size:
                            trace(f'Warning (W3): size mismatch for {item_id} ({result.file_size:d} / {result.expected_size:d}).'
                                  f' Retrying file.', True)
                            if path.isfile(dest):
                                remove(dest)
                                result.file_size = 0
                            raise IOError
                    except (KeyboardInterrupt, ThreadInterruptException):
                        if path.isfile(dest):
                            result.file_size = stat(dest).st_size
                            if result.file_size != result.expected_size:
                                remove(dest)
                                result.file_size = 0
                        trace(f'{result.result_str}{("interrupted by user." if current_process() == self.my_root_thread else "")}', True)
                        raise DownloadInterruptException
                    except (HTTPError, Exception) as err:
                        if isinstance(err, HTTPError) and err.response.status_code == 404:  # RS cdn error
                            if ProcModule.is_rs():
                                hostname: str = urlparse(link).hostname or 'unk'
                                if hostname.startswith('video') and '-cdn' in hostname:
                                    if __RUXX_DEBUG__:
                                        trace(f'Warning (W3): {item_id} catched HTTPError 404 (host: {hostname})! '
                                              f'Trying no-cdn source...', True)
                                    re_vhost_cdn = re_compile(r'-cdn\d')  # video-cdn1.rs
                                    link = re_vhost_cdn.sub('', link)
                            elif ProcModule.is_rz():
                                assert is_video_ext
                                valid_link_ends = ('', '720')
                                for lidx, link_end in enumerate(valid_link_ends):
                                    lend = f'{link_end}.{ext_full}'
                                    if link.endswith(lend):
                                        new_idx = (lidx + 1) % len(valid_link_ends)
                                        if __RUXX_DEBUG__:
                                            trace(f'Warning (W3): {item_id} catched HTTPError 404 (ends with \'{link_end}\')! '
                                                  f'Trying \'{valid_link_ends[new_idx]}\'...', True)
                                        link = f'{link[:-len(lend)]}{valid_link_ends[new_idx]}.{ext_full}'
                                        break
                            elif ProcModule.is_rx():
                                if link != oldlink:
                                    trace(f'Warning (W3): {item_id} catched HTTPError 404 for normalized link. '
                                          f'Switching to slow link \'{oldlink}\'...', True)
                                    link = oldlink
                        if isinstance(err, HTTPError) and err.response.status_code == 416:  # Requested range is not satisfiable
                            if __RUXX_DEBUG__:
                                trace(f'Warning (W3): {item_id} catched HTTPError 416!', True)
                            if path.isfile(dest):
                                remove(dest)
                                result.file_size = 0
                        result.retries += 1
                        s_result = f'{result.result_str}{str(exc_info()[0])}: {str(exc_info()[1])} retry {result.retries:d}...'
                        trace(s_result, True)
                        thread_sleep(2)
                        continue
        return result

    # threaded
    def wrap_request(self, url: str, tries: int, method: str, **kwargs) -> Response | None:
        r: Response | None = None
        retries = 0
        while retries < tries:
            self.catch_cancel_or_ctrl_c()
            r = None
            try:
                r = self.session.request(method, url, timeout=self.timeout, stream=False, allow_redirects=True, **kwargs)
                r.raise_for_status()
                break
            except (KeyboardInterrupt, ThreadInterruptException):
                thread_exit('interrupted by user.', code=1)
            except (Exception, HTTPError,) as err:
                retries += 1
                sleep_time = 1.0
                threadname = f'{current_process().name}: ' if current_process() != self.my_root_thread else ''
                if isinstance(err, HTTPError) and err.response.status_code == 404:
                    if r is not None and r.content and len(r.content.decode()) > 2:
                        trace(f'{threadname}received code 404 but received html'
                              f'\n{str(exc_info()[0])}: {str(exc_info()[1])}. Continuing...', True)
                        break
                    trace(f'{threadname}catched err 404 {str(exc_info()[0])}: {str(exc_info()[1])}. Aborting...', True)
                    return None
                elif isinstance(err, HTTPError) and err.response.status_code == 429:  # Too Many Requests
                    sleep_time += float(min(9, retries))
                    if __RUXX_DEBUG__:
                        trace(f'{threadname}catched {str(exc_info()[0])}: {str(exc_info()[1])}.'
                              f'{f" Reconnecting in {sleep_time:.1f} sec... {retries:d}" if retries < tries else ""}', True)
                else:
                    trace(f'{threadname}catched {str(exc_info()[0])}: {str(exc_info()[1])}.'
                          f'{f" Reconnecting in {sleep_time:.1f} sec... {retries:d}" if retries < tries else ""}', True)
                thread_sleep(sleep_time)
                continue

        if retries >= tries:
            errmsg = f'Unable to connect. Aborting {url}'
            trace(errmsg, True)
            r = None
        elif r is None:
            trace('ERROR: Failed to receive any data', True)
        elif len(r.cookies) > 0:
            t = self.add_cookies.copy()
            self.add_cookies = r.cookies.copy()
            self.add_cookies.update(t)

        return r

    # threaded
    def fetch_html(self, url: str, tries=0, do_cache=False, method='GET', **kwargs) -> BeautifulSoup | None:
        cached = self.raw_html_cache.get(url, b'')
        if cached:
            return cached if isinstance(cached, BeautifulSoup) else BeautifulSoup(cached, 'html.parser')
        r = self.wrap_request(url, tries or self.retries, method, **kwargs)
        result = BeautifulSoup(r.content, 'html.parser') if r is not None else None
        if result and do_cache:
            self.raw_html_cache[url] = result if self.cache_mode == HtmlCacheMode.CACHE_BS else r.content
        return result

#
#
#########################################
