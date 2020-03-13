# --- coding: utf-8 ---
"""
bookwalkerブックストアの設定モジュール
"""

from enum import IntEnum


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


class Config(object):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self, data=None):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
        """
        self.needs_login = False
        """
        ログインする必要があるかどうか
        """
        self.username = None
        """
        ID
        """
        self.password = None
        """
        パスワード
        """
        self.image_format = ImageFormat.PNG
        """
        書き出す画像フォーマット
        """
        self.sleep_time = 0.5
        """
        ページスクロールのスリープ時間
        """
        self.bound_on_side = BoundOnSide.LEFT
        """
        本の綴じ場所
        """
        if isinstance(data, dict):
            self.update(data)
        return

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        if 'needs_login' in data:
            self.needs_login = data['needs_login']
        if 'username' in data:
            self.username = data['username']
        if 'password' in data:
            self.password = data['password']
        if 'image_format' in data:
            self._set_image_format(data['image_format'])
        if 'sleep_time' in data:
            self.sleep_time = data['sleep_time']
        if 'bound_on_side' in data:
            self._set_bound_on_side(data['bound_on_side'])
        return

    def _set_image_format(self, format):
        """
        書き出す画像のフォーマットを設定する
        使用できるフォーマットは bookstore.ImageFormat.ImageFormat に記されている
        @param format 画像のフォーマット
        """
        if isinstance(format, str):
            _format = format.upper()
            if _format in {ImageFormat.JPEG.name, str(int(ImageFormat.JPEG))}:
                self.image_format = ImageFormat.JPEG
            elif _format in {ImageFormat.PNG.name, str(int(ImageFormat.PNG))}:
                self.image_format = ImageFormat.PNG
        elif isinstance(format, int):
            if format == ImageFormat.JPEG:
                self.image_format = ImageFormat.JPEG
            elif format == ImageFormat.PNG:
                self.image_format = ImageFormat.PNG
        return

    def _set_bound_on_side(self, bound_on_side):
        """
        本の閉じ場所を設定する
        使用できる場所は bookstore.BoundOnSide.BoundOnSide に記されている
        @param bound_on_side 本の綴じ場所
        """
        if isinstance(bound_on_side, str):
            _bound_on_side = bound_on_side.upper()
            if _bound_on_side in {BoundOnSide.RIGHT.name, str(
                    int(BoundOnSide.RIGHT))}:
                self.bound_on_side = BoundOnSide.RIGHT
            elif _bound_on_side in {BoundOnSide.LEFT.name, str(
                    int(BoundOnSide.LEFT))}:
                self.bound_on_side = BoundOnSide.LEFT
        elif isinstance(bound_on_side, int):
            if bound_on_side == BoundOnSide.RIGHT:
                self.bound_on_side = BoundOnSide.RIGHT
            elif bound_on_side == BoundOnSide.LEFT:
                self.bound_on_side = BoundOnSide.LEFT
        return
