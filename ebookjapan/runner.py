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


class Runner(AbstractRunner):
    """
    ebookjapan の実行クラス
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'ebookjapan\\.yahoo\\.co\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['books\\/\\d+']
    """
    サポートする ebookjapan のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        ebookjapan の実行
        """
        try:
            if (self.config.ebookjapan.needs_login and
                    not self._is_login() and not self._login()):
                return
        except Exception as err:
            _filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, _filename))
            print('ログイン時にエラーが発生しました: %s' %
                  err.with_traceback(sys.exc_info()[2]))
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

        _destination = self.url[self.url.rindex('books/') + 6:-1].replace('/', '_')
        print(f'Output Path : {_destination}')
#        _destination = input('Output Path > ')
        _manager = Manager(
            self.browser, self.config.ebookjapan, _destination)
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
        if self.config.ebookjapan.username and self.config.ebookjapan.password:
            yahoo = YahooLogin(
                self.browser,
                self.config.ebookjapan.username,
                self.config.ebookjapan.password)
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
        _elements = self.browser.find_by_css('.btn.btn--primary.btn--read')
        if len(_elements) != 0 and '読む' in _elements.first.text:
            _elements.first.click()
            return True
        return False

    def _move_demo_page(self):
        """
        実際の本の試し読みページに移動する
        """
        _elements = self.browser.find_by_css('.book-main__purchase > a.btn')
        if len(_elements) != 0 and _elements.first.text == '試し読み':
            _elements.first.click()
            return True
        return False
