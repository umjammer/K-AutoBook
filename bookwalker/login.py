# --- coding: utf-8 ---
"""
bookwalkerを使用するためにアカウントでログインするためのクラスモジュール
"""

from getpass import getpass
from urllib import request
from PIL import Image
import io
import time


class YahooLogin(object):
    """
    アカウントでログインするためのクラス
    """

    LOGIN_URL = 'https://member.bookwalker.jp/app/03/login'
    """
    ログインページの URL
    """

    YAHOO_JAPAN_URL = 'https://www.yahoo.co.jp/'
    """
    Yahoo! JAPAN の URL
    """

    ONE_TIME_PASSWORD_URL = 'https://protect.login.yahoo.co.jp/otp/auth'
    """
    ログイン時にワンタイムパスワードを求めるページの URL
    """

    def __init__(self, browser, yahoo_id=None, password=None):
        """
        Yahoo でログインするためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        @param yahoo_id ヤフー ID
        @param password パスワード
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.yahoo_id = yahoo_id
        """
        Yahoo ID
        None が設定されている場合はユーザ入力を求める
        """
        self.password = password
        """
        パスワード
        None が設定されている場合はユーザ入力を求める
        """
        return

    def login(self):
        """
        ログインを行う
        @return ログイン成功時に True を返す
        """
        print('Loading Yahoo JAPAN! top page')
        self.browser.visit(self.YAHOO_JAPAN_URL)
        print('Loading login page')
        _url = self.browser.find_by_css('#Login [data-rapid_p]').first['href']
        self.browser.visit(_url)
        for _try_count in range(4):
            _yahoo_id = input('Input Yahoo ID > ') if (
                self.yahoo_id is None) else self.yahoo_id
            _password = getpass('Input Password > ') if (
                self.password is None) else self.password
            print('Trying login: ' + _yahoo_id)
            self.browser.fill('login', _yahoo_id)
            print('Confirm Yahoo JAPAN! ID')
            self.browser.find_by_id('btnNext').click()
            time.sleep(1)
            self.browser.execute_script(
                'element = document.getElementById("passwd");' +
                'element.disabled = false;' +
                'element.readOnly = false;')
            self.browser.fill('passwd', _password)
            self.browser.find_by_id('btnSubmit').click()
            print('Trying login')
            if self._is_login_error():
                print('ログインに失敗しました')
                if self.yahoo_id is not None and self.password is not None:
                    return False
                continue
            for _count in range(3):
                if self._is_image_captcha():
                    if not self._show_image_captcha():
                        return False
                    _result = input('Input Captcha > ')
                    self.browser.fill('captchaAnswer', _result)
                    self.browser.find_by_css('input[type=image]').first.click()
                elif self._is_login_page():
                    break
                else:
                    break
                if _count == 2 and self._is_image_captcha():
                    print('画像キャプチャが一致しませんでした')
                    return False
            if not self._is_login_page():
                _one_time_password = None
                _is_succeeded_login = False
                for _count in range(4):
                    if self._is_required_one_time_password():
                        if _one_time_password is not None:
                            print('Invalid one time password')
                        _one_time_password = input(
                            'Input one time password > ')
                        self.browser.fill('verify_code', _one_time_password)
                        self.browser.find_by_css('[type=submit]')[0].click()
                    else:
                        _is_succeeded_login = True
                        break
                print('Succeeded login')
                return True
        return False

    def _is_login_page(self):
        """
        ログインページかどうかを判定する
        """
        return self.browser.url.startswith(self.LOGIN_URL)

    def _is_login_error(self):
        """
        ログインエラーかどうかを判定する
        @return ログインエラーの場合に True を返す
        """
        _elements = self.browser.find_by_css('div.yregertxt > h2.yjM')
        return self._is_login_page() and len(_elements) != 0

    def _is_image_captcha(self):
        """
        画像キャプチャに引っかかっているかどうかを取得する
        @return 画像キャプチャをもとめられている場合に True を返す
        """
        _result = self.browser.url.startswith(self.LOGIN_URL)
        _result = _result and self.browser.title == '文字認証を行います。 - Yahoo! JAPAN'
        if _result:
            _names = []
            for _input in self.browser.find_by_tag('input'):
                _names.append(_input['name'])
            _checks = [
                'captchaCdata',
                'captchaMultiByteCaptchaId',
                'captchaView',
                'captchaClassInfo',
                'captchaAnswer'
            ]
            for _check in _checks:
                _result = _result and _check in _names
                if not _result:
                    return _result
        return _result

    def _show_image_captcha(self):
        """
        画像キャプチャを表示する
        @return 画像の表示に成功した場合に True を返す
        """
        _file = io.BytesIO(request.urlopen(self.browser.find_by_id(
            'captchaV5MultiByteCaptchaImg')['src']).read())
        _base_image = Image.open(_file)
        _base_image = _base_image.convert('RGBA')
        _show_image = Image.new(
            'RGBA', _base_image.size, (0xFF, 0xFF, 0xFF, 0x0))
        _width, _height = _base_image.size
        for _point_x in range(_width):
            for _point_y in range(_height):
                _pixel = _base_image.getpixel((_point_x, _point_y))
                if _pixel != (0, 0, 0, 0):
                    _show_image.putpixel((_point_x, _point_y), _pixel)
        _show_image.show()
        return True

    def _is_required_one_time_password(self):
        """
        ワンタイムパスワードを求められているかを確認する
        """
        return self.browser.url.startswith(self.ONE_TIME_PASSWORD_URL)
