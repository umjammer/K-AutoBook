# --- coding: utf-8 ---
"""
実行するためのの抽象クラスモジュール
"""

import inspect
import os
import re
import importlib
from abc import ABC, abstractmethod
from config import BasicSubConfig, ChromeCookie, SubConfigWithCookie
from manager import CoreViewManager


class AbstractRunner(ABC):
    """
    実行するための抽象クラス
    """

    def _initialize_checker(self):
        """
        サポートする URL かどうかの判定機の初期設定を行う
        """
        for pattern in self.sub_config.patterns:
            self.checkers.append(
                re.compile(
                    r'https?://' + self.sub_config.domain + '/' + pattern))

    def check(self, url):
        """
        サポートしているかどうかの判定を行う
        @param url str サポートしているどうかを判定する URL
        @return bool サポートしている場合に True を返す
        """
        for checker in self.checkers:
            if checker.match(url):
                return True
        return False

    def __init__(self, type_, browser, config, sub_config_class=None):
        """
        @param browser splinter のブラウザ情報
        @param config global configuration
        """
        self.type_ = type_
        self.browser = browser
        self.config = config
        self.sub_config = sub_config_class() if sub_config_class else None
        self.url = None
        self.options = None
        self.checkers = []

        if self.sub_config:
            if self.type_ in self.config.raw:
                self.sub_config.update(self.config.raw[self.type_])

            self._initialize_checker()

    def init(self, url, options=None):
        """
        ブックストアで実行するためのコンストラクタ
        @param url str アクセスする URL
        @param options str オプション情報
        """
        self.url = url
        """
        実行するブックストアの URL
        """

        self.options = self._parse_options(options)
        """
        オプションとして指定する文字列
        オプションのパース方法は継承先に依存する
        """

    def reset(self, browser):
        self.browser = browser

    @abstractmethod
    def run(self):
        """
        実行メソッド
        """
        pass

    def _parse_options(self, options):
        """
        オプションのパース処理
        @param options str オプション文字列
        @return str 引数で受け取ったオプション文字列をそのまま返す
        """
        return options

    def _get_id(self):
        for pattern in self.sub_config.patterns:
            m = re.match(r'.*' + pattern, self.url)
            # print(m)
            if m:
                return str.join('-', m.groups())

    def get_output_dir(self):
        return os.path.join(self.config.base_directory, self._get_id())

    @staticmethod
    def get_plugins():
        """
        https://stackoverflow.com/questions/4787291/dynamic-importing-of-modules-followed-by-instantiation-of-objects-with-a-certain
        @return Tuple[module name, plugin class]
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
                            name = module.__name__[:module.__name__.rindex('.')]
                            # print(f'found in {name}: {attr}')
                            class_list.append((name, attr))
        # print(f'{class_list}')
        return class_list

    def _get_cookie(self):
        if self.sub_config.cookie:
            # TODO check expiry automatically
            return self.sub_config.cookie
        elif self.config.chrome_cookie_db:
            cookie = ChromeCookie(self.config.chrome_cookie_db).get_cookie(self.sub_config.host_key)
            self.config.save_sub_cookie(self.type_, cookie)
            return cookie
        else:
            return None

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

    def _set_cookie(self):
        """
        should be call after self.sub_config setup
        """
        cookie = self._get_cookie()
        if cookie:
            self.browser.driver.get(self.sub_config.top_url)
            self.browser.driver.delete_all_cookies()
            self._add_cookies(self.browser.driver, self._get_cookie_dict(cookie))
            return True
        else:
            return False


class DirectPageRunner(AbstractRunner, ABC):
    """
    Runner for the first page is viewer direct.
    """

    def __init__(self, type_, browser, config,
                 sub_config_class=BasicSubConfig, manager_class=CoreViewManager):
        super().__init__(type_, browser, config, sub_config_class)

        self.manager_class = manager_class

    def run(self):
        """
        Runs runner
        """
        # TODO eliminate SubConfigWithCookie
        if self.config.chrome_cookie_db and isinstance(self.sub_config, SubConfigWithCookie):
            if self._set_cookie():
                print('cookie has set')

        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        destination = self.get_output_dir()
        print(f'Output Path : {destination}')

        manager = self.manager_class(self.browser, self.sub_config, destination)
        result = manager.start()
        if result is not True:
            print(result)
