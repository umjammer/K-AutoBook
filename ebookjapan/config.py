# --- coding: utf-8 ---
"""
ブックストアの設定モジュール
"""

from enum import IntEnum
from config import AbstractConfig


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


class Config(AbstractConfig):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
        """
        super().__init__()

        self.username = None
        """
        Yahoo! JAPAN ID
        """
        self.password = None
        """
        Yahoo! JAPAN ID のパスワード
        """
        self.bound_on_side = BoundOnSide.LEFT
        """
        本の綴じ場所
        """
        self.blank_check_excludes = set()
        """
        black page checking excludes pages, negative number or zero means (total - 1 + negative_number)
        """
        self.blank_check_giveup = 11
        """
        black page checking give up times
        11 is larger than retry times, means never give up, means retry error stop downloading.
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
        if 'bound_on_side' in data:
            self._set_bound_on_side(data['bound_on_side'])
        if 'blank_check_excludes' in data:
            self.blank_check_excludes = eval(data['blank_check_excludes'])
        if 'blank_check_giveup' in data:
            self.blank_check_giveup = data['blank_check_giveup']

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
