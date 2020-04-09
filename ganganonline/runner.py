# --- coding: utf-8 ---
"""
gangan-online の実行クラスモジュール
"""

import sys
from os import path
from datetime import datetime
from config import BasicSubConfig
from runner import AbstractRunner
from ganganonline.login import YahooLogin
from ganganonline.manager import Manager


class Runner(AbstractRunner):
    """
    gangan-online の実行クラス
    https://viewer.ganganonline.com/manga/?chapterId=15502
    """

    domain_pattern = 'viewer\\.ganganonline\\.com'
    """
    サポートするドメイン
    """

    patterns = ['manga\\/\\?chapterId=(\\d+)']
    """
    サポートする gangan-online のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        gangan-online の実行
        """
        self.sub_config = BasicSubConfig()
        if 'ganganonline' in self.config.raw:
            self.sub_config.update(self.config.raw['ganganonline'])

        try:
            if (self.sub_config.needs_login and
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

        # _destination = input('Output Path > ')
        _destination = self.get_id()
        print(f'Output Path : {_destination}')

        _manager = Manager(
            self.browser, self.sub_config, _destination)
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
