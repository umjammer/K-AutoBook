# --- coding: utf-8 ---
"""
web-ace の実行クラスモジュール
"""
import re
import sys
from os import path
from datetime import datetime
from runner import AbstractRunner
from webace.login import YahooLogin
from webace.manager import Manager
from webace.config import Config as WebaceConfig


class Runner(AbstractRunner):
    """
    web-ace の実行クラス
    https://web-ace.jp/youngaceup/contents/1000053/episode/1092/
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'web-ace\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['youngaceup\\/contents\\/(\\d+)\\/episode\\/(\\d+)']
    """
    サポートする web-ace のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        web-ace の実行
        """
        self.sub_config = WebaceConfig()
        if 'webace' in self.config.raw:
            self.sub_config.update(self.config.raw['webace'])

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

        _destination = self.get_id()
        # _destination = input('Output Path > ')
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

    def need_reset(self):
        return True
