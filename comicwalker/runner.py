# --- coding: utf-8 ---
"""
comicwalker の実行クラスモジュール
"""

import sys
from os import path
from datetime import datetime
from runner import AbstractRunner
from comicwalker.login import YahooLogin
from comicwalker.manager import Manager


class Runner(AbstractRunner):
    """
    comicwalker の実行クラス
    https://comic-walker.com/viewer/?tw=2&dlcl=ja&cid=KDCW_MF09000001010005_68
    """

    domain_pattern = 'comic-walker\\.com'
    """
    サポートするドメイン
    """

    patterns = ['viewer\\/.*&cid=KDCW_[A-Z]{2}[0-9]{14}_[0-9]{2}']
    """
    サポートする comicwalker のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        comicwalker の実行
        """
        try:
            if (self.config.comicwalker.needs_login and
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

        _destination = self.url[self.url.rindex('cid=') + 4:]
        print(f'Output Path : {_destination}')
#        _destination = input('Output Path > ')
        _manager = Manager(
            self.browser, self.config.comicwalker, _destination)
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
        if self.config.comicwalker.username and self.config.comicwalker.password:
            yahoo = YahooLogin(
                self.browser,
                self.config.comicwalker.username,
                self.config.comicwalker.password)
        else:
            yahoo = YahooLogin(self.browser)
        if yahoo.login():
            Runner.is_login = True
            return True
        return False
