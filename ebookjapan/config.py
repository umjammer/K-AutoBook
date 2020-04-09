# --- coding: utf-8 ---
"""
ブックストアの設定モジュール
"""

from config import AbstractConfig, BoundOnSide


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
