# --- coding: utf-8 ---
"""
line-manga の実行クラスモジュール
"""

import time
from config import SubConfigWithCookie
from os import path
from datetime import datetime
from runner import AbstractRunner
from linemanga.login import LineLogin
from linemanga.manager import Manager


class Runner(AbstractRunner):
    """
    line-manga の実行クラス
    https://manga.line.me/book/viewer?id=92dc0b4e-c5d4-4518-9fba-d78fb1e6b0f0
    """

    is_login = False
    """
    ログイン状態
    """

    login_url = None
    """
    """

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, SubConfigWithCookie)

    def run(self):
        """
        line-manga の実行
        """
        try:
            if self._set_cookie():
                self.browser.driver.get('https://manga.line.me/store/')
                time.sleep(1)
            else:
                if (self.sub_config.needs_login and
                        not self._is_login() and not self._login()):
                    return
        except Exception as err:
            filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, filename))
            raise err
        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        print('Open main page')

        destination = self.get_output_dir()
        print(f'Output Path : {destination}')

        manager = Manager(
            self.browser, self.sub_config, destination)
        result = manager.start()
        if result is not True:
            print(result)
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
#        print(self.browser.driver.page_source)
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
        if self.sub_config.username and self.sub_config.password:
            line = LineLogin(
                self.browser,
                self.login_url,
                self.sub_config.username,
                self.sub_config.password)
        else:
            line = LineLogin(self.browser)
        if line.login():
            Runner.is_login = True
            return True
        return False
