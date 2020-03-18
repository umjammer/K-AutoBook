# --- coding: utf-8 ---
"""
line manga を使用するためにYahooアカウントでログインするためのクラスモジュール
"""
from getpass import getpass
from urllib import request
from PIL import Image
import io
import time


class LineLogin(object):
    """
    アカウントでログインするためのクラス
    """

    def __init__(self, browser, login_url=None, _id=None, password=None):
        """
         でログインするためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        @param _id Line ID
        @param password パスワード
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self._id = _id
        """
        Yahoo ID
        None が設定されている場合はユーザ入力を求める
        """
        self.password = password
        """
        パスワード
        None が設定されている場合はユーザ入力を求める
        """
        self.login_url = login_url
        """
        ログインページの URL
        """
        return

    def login(self):
        """
        ログインを行う
        @return ログイン成功時に True を返す
        """
        print('Loading Line Manga top page')
        self.browser.visit(self.login_url)
        for _try_count in range(4):
            _line_id = input('Input Line ID > ') if (
                self._id is None) else self._id
            _password = getpass('Input Password > ') if (
                self.password is None) else self.password
            print('Trying login: ' + _line_id)
            self.browser.execute_script(
                'element = document.getElementById("id");' +
                f'element.value = "{_line_id}";')
            time.sleep(.3)
            self.browser.execute_script(
                'element = document.getElementById("passwd");' +
                f'element.value = "{_password}";')
            time.sleep(.3)
            print('Confirm Line ID')
            _form = self.browser.driver.find_element_by_xpath('//form')
            _form.submit()
            time.sleep(1)
            print('Trying login')
            if self._is_login_error():
                print('ログインに失敗しました')
                if self._id is not None and self.password is not None:
                    return False
                continue
            if not self._is_login_page():
                _one_time_password = None
                _is_succeeded_login = False
                print('Succeeded login')
                return True
        return False

    def _is_login_page(self):
        """
        ログインページかどうかを判定する
        """
        return self.browser.url.startswith('https://access.line.me/dialog/oauth/weblogin')

    def _is_login_error(self):
        """
        ログインエラーかどうかを判定する
        @return ログインエラーの場合に True を返す
        """
        _elements = self.browser.find_by_css('div.yregertxt > h2.yjM')
        return self._is_login_page() and len(_elements) != 0
