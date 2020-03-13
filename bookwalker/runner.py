# --- coding: utf-8 ---
"""
bookwalker の実行クラスモジュール
"""

import sys
from os import path
from datetime import datetime
from runner import AbstractRunner
from bookwalker.login import YahooLogin
from bookwalker.manager import Manager


class Runner(AbstractRunner):
    """
    bookwalker の実行クラス
    https://viewer.bookwalker.jp/browserWebApi/03/view?cid=57c84cf2-7062-4ef9-9071-45fb249c926e
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'viewer\\.bookwalker\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['browserWebApi\\/\\d+\\/[\\w\\?=-]+']
    """
    サポートする bookwalker のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        bookwalker の実行
        """
        try:
            if (self.config.bookwalker.needs_login and
                    not self._is_login() and not self._login()):
                return
        except Exception as err:
            _filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, _filename))
            print('ログイン時にエラーが発生しました: %s' %
                  err.with_traceback(sys.exc_info()[2]))
            return
        print('Loading page of inputed url (%s)' % self.url)
        self.browser.visit(self.url)

        print('Open main page')

#        _destination = input('Output Path > ')
        _destination = self.url[self.url.rindex('=') + 1:]
        print(f'Output Path : {_destination}')
        _manager = Manager(
            self.browser, self.config.bookwalker, _destination)
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
        if self.config.bookwalker.username and self.config.bookwalker.password:
            yahoo = YahooLogin(
                self.browser,
                self.config.bookwalker.username,
                self.config.bookwalker.password)
        else:
            yahoo = YahooLogin(self.browser)
        if yahoo.login():
            Runner.is_login = True
            return True
        return False
