# --- coding: utf-8 ---
"""
comic-days の実行クラスモジュール
"""

import sys
from os import path
from datetime import datetime
from config import BasicSubConfig
from runner import AbstractRunner
from comicdays.login import YahooLogin
from comicdays.manager import Manager


class Runner(AbstractRunner):
    """
    comic-days の実行クラス
    https://comic-days.com/volume/13932016480030155016
    """

    domain_pattern = 'comic-days\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする comic-days のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        comic-days の実行
        """
        self.sub_config = BasicSubConfig()
        if 'comicdays' in self.config.raw:
            self.sub_config.update(self.config.raw['comicdays'])

        try:
            if self.sub_config.needs_login and not self._is_login() and not self._login():
                return
        except Exception as err:
            _filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(path.join(self.config.log_directory, _filename))
            print('ログイン時にエラーが発生しました: %s' % err.with_traceback(sys.exc_info()[2]))
            return
        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        # _destination = input('Output Path > ')
        _destination = self.get_id()
        print(f'Output Path : {_destination}')

        _manager = Manager(self.browser, self.sub_config, _destination)
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
