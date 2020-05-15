# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

from abc import ABC
from enum import IntEnum


class Config(object):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self, data=None):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
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
        self.raw = data
        """
        raw data
        """
        if isinstance(data, dict):
            self.update(data)

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        if 'driver' in data:
            self.driver = data['driver']
        if 'user_agent' in data:
            self.user_agent = data['user_agent']
        if 'chrome_path' in data:
            self.chrome_path = data['chrome_path']
        if 'chrome_binary' in data:
            self.chrome_binary = data['chrome_binary']
        if 'headless' in data:
            self.headless = bool(data['headless'])
        if 'log_directory' in data:
            self.log_directory = data['log_directory']
        if 'base_directory' in data:
            self.base_directory = data['base_directory']


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
        @param data 設定情報
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

    def __init__(self, data=None):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
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
