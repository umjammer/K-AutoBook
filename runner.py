# --- coding: utf-8 ---
"""
実行するためのの抽象クラスモジュール
"""

import inspect
import os
import re
import importlib
from abc import ABC, abstractmethod
from config import BasicSubConfig, ChromeCookie
from manager import CoreViewManager


class AbstractRunner(ABC):
    """
    実行するための抽象クラス
    """

    domain_pattern = ''
    """
    サポートするドメインの正規表現のパターン
    """

    patterns = []
    """
    サポートするパスの正規表現のパターンリスト
    """

    checkers = None
    """
    サポートする URL かどうかの判定機
    """

    @classmethod
    def _initialize_checker(cls):
        """
        サポートする URL かどうかの判定機の初期設定を行う
        """
        cls.checkers = []
        for _pattern in cls.patterns:
            cls.checkers.append(
                re.compile(
                    r'https?://' + cls.domain_pattern + '/' + _pattern))

    @classmethod
    def check(cls, url):
        """
        サポートしているかどうかの判定を行う
        @param url str サポートしているどうかを判定する URL
        @return bool サポートしている場合に True を返す
        """
        if cls.checkers is None:
            cls._initialize_checker()
        for _checker in cls.checkers:
            if _checker.match(url):
                return True
        return False

    def __init__(self):
        self.browser = None
        self.url = None
        self.config = None
        self.sub_config = None
        self.options = None

    def init(self, browser, url, config=None, options=None):
        """
        ブックストアで実行するためのコンストラクタ
        @param browser splinter のブラウザ情報
        @param url str アクセスする URL
        @param config global configuration
        @param options str オプション情報
        """
        self.browser = browser
        """
        splinter のブラウザ情報
        """

        self.url = url
        """
        実行するブックストアの URL
        """

        self.config = config
        """
        global configuration
        """

        self.sub_config = None
        """
        each site configuration
        """

        self.options = self.parse_options(options)
        """
        オプションとして指定する文字列
        オプションのパース方法は継承先に依存する
        """

    @abstractmethod
    def run(self):
        """
        実行メソッド
        """
        pass

    def parse_options(self, options):
        """
        オプションのパース処理
        @param options str オプション文字列
        @return str 引数で受け取ったオプション文字列をそのまま返す
        """
        return options

    def need_reset(self):
        return False

    def _get_id(self):
        for _pattern in self.patterns:
            m = re.match(r'.*' + _pattern, self.url)
            # print(m)
            if m:
                return str.join('-', m.groups())

    def get_output_dir(self):
        return os.path.join(self.config.base_directory, self._get_id())

    @staticmethod
    def get_plugins():
        """
        https://stackoverflow.com/questions/4787291/dynamic-importing-of-modules-followed-by-instantiation-of-objects-with-a-certain
        """

        class_list = []
        for root, dirs, files in os.walk('.'):
            if root == '.' or '__init__.py' not in files:
                continue
            candidates = [file_name for file_name in files if file_name.endswith('.py')
                          and not file_name.startswith('__')]
            if candidates:
                for c in candidates:
                    modname = root[2:].replace('/', '.') + '.' + os.path.splitext(c)[0]
                    try:
                        module = importlib.import_module(modname)
                    except (ImportError, NotImplementedError) as e:
                        continue
                    for cls in dir(module):
                        attr = getattr(module, cls)
                        if (inspect.isclass(attr) and
                                inspect.getmodule(attr) == module and
                                issubclass(attr, AbstractRunner)):
                            # print(f'found in {module.__name__}: {attr}')
                            class_list.append(attr)
        # print(f'{class_list}')
        return class_list

    def _get_cookie(self, host_key):
        if self.sub_config.cookie:
            # TODO check expiry automatically
            return self.sub_config.cookie
        elif self.config.chrome_cookie_db:
            cookie = ChromeCookie(self.config.chrome_cookie_db).get_cookie(host_key)
            self._save_sub_cookie(cookie)
            return cookie
        else:
            return None

    def _save_sub_cookie(self, cookie):
        raise Exception('not implemented yet')

    @staticmethod
    def _get_cookie_dict(cookies):
        cookies = cookies.split('; ')
        cookies_dict = {}
        for i in cookies:
            kv = i.split('=')
            cookies_dict[kv[0]] = kv[1]
        return cookies_dict

    @staticmethod
    def _add_cookies(driver, cookies):
        for i in cookies:
            # print(f"{i}: {cookies[i]}")
            driver.add_cookie({'name': i, 'value': cookies[i]})

    def _set_cookie(self, host_key, top_url):
        """
        should be call after self.sub_config setup
        """
        cookie = self._get_cookie(host_key)
        if cookie:
            self.browser.driver.get(top_url)
            self.browser.driver.delete_all_cookies()
            self._add_cookies(self.browser.driver, self._get_cookie_dict(cookie))
            return True
        else:
            return False


class DirectPageRunner(AbstractRunner, ABC):
    """
    Runner for the first page is viewer direct.
    """

    def _run(self, type_, manager_class=CoreViewManager,
             sub_config_class=BasicSubConfig, host_key=None, top_url=None):
        """
        Runs runner
        """
        self.sub_config = sub_config_class()
        if type_ in self.config.raw:
            self.sub_config.update(self.config.raw[type_])

        if self.config.chrome_cookie_db and host_key and top_url:
            if self._set_cookie( host_key, top_url):
                print('cookie has set')

        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        # _destination = input('Output Path > ')
        _destination = self.get_output_dir()
        print(f'Output Path : {_destination}')

        _manager = manager_class(self.browser, self.sub_config, _destination)
        _result = _manager.start()
        if _result is not True:
            print(_result)
