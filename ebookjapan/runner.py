# --- coding: utf-8 ---
"""
ebookjapan の実行クラスモジュール
"""

import sys
from os import path
from datetime import datetime
from runner import AbstractRunner
from ebookjapan.login import YahooLogin
from ebookjapan.manager import Manager
from ebookjapan.config import SubConfig


class Runner(AbstractRunner):
    """
    ebookjapan の実行クラス

    https://ebookjapan.yahoo.co.jp/books/145222/A000100547
    """

    is_login = False
    """
    ログイン状態
    """

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, SubConfig)

    def run(self):
        """
        ebookjapan の実行
        """
        try:
            if (self.sub_config.needs_login and
                    not self._is_login() and not self._login()):
                return
        except Exception as e:
            filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, filename))
            print('ログイン時にエラーが発生しました: %s' %
                  e.with_traceback(sys.exc_info()[2]))
            return
        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        if self._move_main_page():
            print('Open main page')
        elif self._move_demo_page():
            print('Open demo page')
        else:
            print('ページの取得に失敗しました')
            return

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
        self.browser.visit(self.url)
        if len(self.browser.find_by_css('.login')) == 0:
            Runner.is_login = True
            return True
        return False

    def _login(self):
        """
        ログイン処理を行う
        @return ログイン成功時に True を返す
        """
        if self.sub_config.username and self.sub_config.password:
            yahoo = YahooLogin(
                self.browser,
                self.sub_config.username,
                self.sub_config.password)
        else:
            yahoo = YahooLogin(self.browser)
        if yahoo.login():
            Runner.is_login = True
            return True
        return False

    def _move_main_page(self):
        """
        実際の本のページに移動する
        """
        elements = self.browser.find_by_css('.btn.btn--primary.btn--read')
        if len(elements) != 0 and '読む' in elements.first.text:
            elements.first.click()
            return True
        return False

    def _move_demo_page(self):
        """
        実際の本の試し読みページに移動する
        """
        elements = self.browser.find_by_css('.book-main__purchase > a.btn')
        if len(elements) != 0 and '試し読み' in elements.first.text:
            elements.first.click()
            return True
        return False
