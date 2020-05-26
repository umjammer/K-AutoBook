# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

import json
import keyring
import sqlite3
from abc import ABC
from contextlib import closing
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from enum import IntEnum
from os import path


class Config:
    """
    設定情報を管理するためのクラス
    """
    _file_name = 'config.json'

    def __init__(self):
        """
        設定情報を管理するためのコンストラクタ
        """
        self.driver = 'phantomjs'
        """
        開くブラウザのドライバ
        """
        self.chrome_path = None
        """
        currently no mean
        """
        self.chrome_binary = None
        """
        chrome binary
        """
        self.user_agent = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 ' +
            'Safari/537.36')
        """
        User Agent
        """
        self.headless = False
        """
        headless or not
        """
        self.log_directory = '/tmp/k_auto_book/'
        """
        ログを出力するディレクトリパス
        """
        self.base_directory = 'data/'
        """
        Base directory for output
        """
        self.chrome_cookie_db = None
        """
        Chrome Cookie database file name
        """
        self.raw = self._load()
        """
        raw data
        """
        if isinstance(self.raw, dict):
            self.update()

    def update(self):
        """
        設定情報を更新する
        """
        if 'driver' in self.raw:
            self.driver = self.raw['driver']
        if 'user_agent' in self.raw:
            self.user_agent = self.raw['user_agent']
        if 'chrome_path' in self.raw:
            self.chrome_path = self.raw['chrome_path']
        if 'chrome_binary' in self.raw:
            self.chrome_binary = self.raw['chrome_binary']
        if 'headless' in self.raw:
            self.headless = bool(self.raw['headless'])
        if 'log_directory' in self.raw:
            self.log_directory = self.raw['log_directory']
        if 'base_directory' in self.raw:
            self.base_directory = self.raw['base_directory']
        if 'chrome_cookie_db' in self.raw:
            self.chrome_cookie_db = self.raw['chrome_cookie_db']

    @staticmethod
    def _load():
        _path = path.join(path.abspath(path.dirname(__file__)), Config._file_name)
        with open(_path, 'r') as _file:
            _data = json.load(_file)
        return _data

    def save_sub_cookie(self, sub_key, cookie):
        if sub_key not in self.raw:
            self.raw[sub_key] = dict()
        self.raw[sub_key]['cookie'] = cookie
        _path = path.join(path.abspath(path.dirname(__file__)), Config._file_name)
        with open(_path, 'w') as _file:
            json.dump(self.raw, _file, indent=4, sort_keys=False)


class ImageFormat(IntEnum):
    """
    書き出す画像のフォーマット
    """

    JPEG = 1
    """
    JPEG フォーマット
    """
    PNG = 2
    """
    PNG フォーマット
    """


class BoundOnSide(IntEnum):
    """
    本の綴じ場所情報
    """
    RIGHT = 1
    """
    右綴じ
    """
    LEFT = 2
    """
    左綴じ
    """


class AbstractConfig(ABC):

    def __init__(self):
        """
        設定情報を管理するためのコンストラクタ
        """
        self.needs_login = False
        """
        ログインする必要があるかどうか
        """
        self.image_format = ImageFormat.JPEG
        """
        書き出す画像フォーマット
        """
        self.sleep_time = 0.5
        """
        ページスクロールのスリープ時間
        """

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        if 'needs_login' in data:
            self.needs_login = data['needs_login']
        if 'image_format' in data:
            self._set_image_format(data['image_format'])
        if 'sleep_time' in data:
            self.sleep_time = data['sleep_time']

    def _set_image_format(self, format_):
        """
        書き出す画像のフォーマットを設定する
        使用できるフォーマットは bookstore.ImageFormat.ImageFormat に記されている
        @param format_ 画像のフォーマット
        """
        if isinstance(format_, str):
            _format = format_.upper()
            if _format in {ImageFormat.JPEG.name, str(int(ImageFormat.JPEG))}:
                self.image_format = ImageFormat.JPEG
            elif _format in {ImageFormat.PNG.name, str(int(ImageFormat.PNG))}:
                self.image_format = ImageFormat.PNG
        elif isinstance(format_, int):
            if format_ == ImageFormat.JPEG:
                self.image_format = ImageFormat.JPEG
            elif format_ == ImageFormat.PNG:
                self.image_format = ImageFormat.PNG

    def _set_bound_on_side(self, bound_on_side):
        """
        本の閉じ場所を設定する
        使用できる場所は bookstore.BoundOnSide.BoundOnSide に記されている
        @param bound_on_side 本の綴じ場所
        """
        if isinstance(bound_on_side, str):
            _bound_on_side = bound_on_side.upper()
            if _bound_on_side in {BoundOnSide.RIGHT.name, str(int(BoundOnSide.RIGHT))}:
                self.bound_on_side = BoundOnSide.RIGHT
            elif _bound_on_side in {BoundOnSide.LEFT.name, str(int(BoundOnSide.LEFT))}:
                self.bound_on_side = BoundOnSide.LEFT
        elif isinstance(bound_on_side, int):
            if bound_on_side == BoundOnSide.RIGHT:
                self.bound_on_side = BoundOnSide.RIGHT
            elif bound_on_side == BoundOnSide.LEFT:
                self.bound_on_side = BoundOnSide.LEFT


class BasicSubConfig(AbstractConfig):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self):
        """
        設定情報を管理するためのコンストラクタ
        """
        super().__init__()

        self.username = None
        """
        ID
        """
        self.password = None
        """
        パスワード
        """

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        super().update(data)

        if 'username' in data:
            self.username = data['username']
        if 'password' in data:
            self.password = data['password']


class SubConfigWithCookie(BasicSubConfig):
    """
    with cookie sub config
    """

    def __init__(self):
        super().__init__()

        self.cookie = None
        """
        Cookie
        """

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        super().update(data)

        if 'cookie' in data:
            self.cookie = data['cookie']


class _AESCipher:

    def __init__(self, key):
        self.key = key

    def decrypt(self, text):
        cipher = AES.new(self.key, AES.MODE_CBC, IV=(b' ' * 16))
        return self._unpad(cipher.decrypt(text))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]


class ChromeCookie:
    """
    currently MacOS only
    https://gist.github.com/kosh04/36cf6023fb75b516451ce933b9db2207
    windows
    https://stackoverflow.com/questions/60230456/dpapi-fails-with-cryptographicexception-when-trying-to-decrypt-chrome-cookies/60611673#60611673
    """

    # NOTE: Chrome uses Win32_FILETIME format
    # NOTE: 11644473600 == strftime('%s', '1601-01-01')
    _sql = """
        SELECT
          host_key,
          path,
          is_secure,
          name,
          value,
          encrypted_value,
          ((expires_utc / 1000000) - 11644473600)
        FROM
          cookies
        WHERE
          host_key like ?
    """

    def __init__(self, db):
        # TODO does this work on windows???
        password = keyring.get_password('Chrome Safe Storage', 'Chrome').encode()
        salt = b'saltysalt'
        length = 16
        iterations = 1003
        key = PBKDF2(password, salt, length, iterations)

        self._cipher = _AESCipher(key)
        self._db = db

    def get_cookie(self, host_key):

        cookie = ""

        with closing(sqlite3.connect(self._db)) as conn:
            result_set = conn.execute(ChromeCookie._sql, ('%' + host_key + '%',))

            for _host_key, _path, is_secure, name, _value, encrypted_value, _exptime in result_set:

                value = _value
                if encrypted_value[:3] == b'v10':
                    encrypted_value = encrypted_value[3:]  # Trim prefix 'v10'
                    value = self._cipher.decrypt(encrypted_value)
                    value = value.decode()

                # exptime = max(_exptime, 0)
                # secure = str(bool(is_secure)).upper()

                # print(_host_key, 'TRUE', _path, secure, exptime, name, value, sep='\t')
                cookie += name + "=" + value + "; "

        return None if not cookie else cookie[:-2]
