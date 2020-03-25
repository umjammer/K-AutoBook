# --- coding: utf-8 ---
"""
zebrackcomic の実行クラスモジュール
"""

import re
import sys
import time
from os import path
from datetime import datetime
from runner import AbstractRunner
from zebrackcomic.login import YahooLogin
from zebrackcomic.manager import Manager
from zebrackcomic.config import Config as ZebrackcomicConfig


class Runner(AbstractRunner):
    """
    zebrack-comic の実行クラス
    https://zebrack-comic.com/title/37/volume/1498/viewer
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'zebrack-comic\\.com'
    """
    サポートするドメイン
    """

    patterns = ['title\\/(\\d+)\\/volume\\/(\\d+)']
    """
    サポートする zebrackcomic のパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        zebrack-comic の実行
        """
        self.sub_config = ZebrackcomicConfig()
        if 'zebrackcomic' in self.config.raw:
            self.sub_config.update(self.config.raw['zebrackcomic'])

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

        if self._move_main_page():
            print('Open main page')
        # elif self._move_demo_page():
        #     print('Open demo page')
        else:
            print('ページの取得に失敗しました')
            return

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

    def _move_main_page(self):
        """
        実際の本のページに移動する
        """
        time.sleep(3)
        _elements = self.browser.find_by_css('button.undefined')
        if len(_elements) != 0:
            _elements.first.click()
            time.sleep(.5)
            try:
                _elements = self.browser.driver.find_element_by_xpath("//*[text()='無料で読む']")
                _elements.click()
                return True
            except Exception as e:
                raise e
        return False

    def _move_demo_page(self):
        """
        実際の本の試し読みページに移動する
        """
        _elements = self.browser.find_by_css('button.undefined')
        if len(_elements) != 0 and _elements.first.text == '試し読み':
            _elements.first.click()
            return True
        return False

    def need_reset(self):
        return True
