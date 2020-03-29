# --- coding: utf-8 ---
"""
line manga の設定モジュール
"""

from config import AbstractConfig


class Config(AbstractConfig):
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

        if 'username' in data:
            self.username = data['username']
        if 'password' in data:
            self.password = data['password']
        if 'cookie' in data:
            self.cookie = data['cookie']
