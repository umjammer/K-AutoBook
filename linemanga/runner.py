# --- coding: utf-8 ---
"""
linemanga の実行クラスモジュール
"""

import sys
from doctest import Example
from os import path
from datetime import datetime
from runner import AbstractRunner
from linemanga.login import LineLogin
from linemanga.manager import Manager
import time


class Runner(AbstractRunner):
    """
    linemanga の実行クラス
    https://manga.line.me/book/viewer?id=92dc0b4e-c5d4-4518-9fba-d78fb1e6b0f0
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'manga\\.line\\.me'
    """
    サポートするドメイン
    """

    patterns = ['book\\/viewer\\?id=[0-9a-f-]+']
    """
    サポートする linemanga のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    login_url = None
    """
    """

    def run(self):
        """
        linemanga の実行
        """
        try:
            self.browser.driver.get('https://manga.line.me/')
            self.browser.driver.delete_all_cookies()
            self._add_cookies(self.browser.driver, self._get_cookie_dict(self.config.linemanga.cookie))

            self.browser.driver.get('https://manga.line.me/store/')
            time.sleep(1)

            if (self.config.linemanga.needs_login and
                    not self._is_login() and not self._login()):
                return
        except Exception as err:
            _filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, _filename))
            raise err
        print('Loading page of inputed url (%s)' % self.url)
        self.browser.visit(self.url)

        print('Open main page')

#        _destination = input('Output Path > ')
        _destination = self.url[self.url.rindex('=') + 1:]
        print(f'Output Path : {_destination}')
        _manager = Manager(
            self.browser, self.config.linemanga, _destination)
        _result = _manager.start()
        if _result is not True:
            print(_result)
        return

    def _is_login(self):
        """
        ログイン状態の確認を行う
        @return ログインしている場合に True を、していない場合に False を返す
        """
        if Runner.is_login:
            return True
        self.browser.driver.get('https://manga.line.me/')
        time.sleep(1)
        #print(self.browser.driver.page_source)
        try:
            a = self.browser.driver.find_element_by_xpath("//a[text() = 'ログイン']")
            self.login_url = a.get_attribute('href')
            print(self.login_url)
            Runner.is_login = True
            return False
        except:
            pass
        return True

    def _login(self):
        """
        ログイン処理を行う
        @return ログイン成功時に True を返す
        """
        if self.config.linemanga.username and self.config.linemanga.password:
            line = LineLogin(
                self.browser,
                self.login_url,
                self.config.linemanga.username,
                self.config.linemanga.password)
        else:
            line = LineLogin(self.browser)
        if line.login():
            Runner.is_login = True
            return True
        return False

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
            #print(f"{i}: {cookies[i]}")
            driver.add_cookie({'name': i, 'value': cookies[i]})
