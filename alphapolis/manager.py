# --- coding: utf-8 ---
"""
アルファポリスから漫画をダウンロードするためのクラスモジュール
"""

import re
from urllib import request
from manager import AbstractManager


class Manager(AbstractManager):
    """
    アルファポリスから漫画をダウンロードするクラス
    """

    def __init__(self, directory='./', prefix=''):
        """
        アルファポリスの操作を行うためのコンストラクタ
        @param directory 出力するファイル群を置くディレクトリ
        @param prefix 出力するファイル名のプレフィックス
        """
        super().__init__(directory=directory, prefix=prefix)

    def start(self, url=None):
        """
        ページの自動自動ダウンロードを開始する
        @param url アルフォポリスのコンテンツの URL
        """
        _sources = self._get_image_urls(url)
        _total = len(_sources)
        self._set_total(_total)

        session = self._get_session()

        for _index in range(_total):
            self._save_image_of_bytes(_index, session.get(_sources[_index]).content)
            self.pbar.update(1)

        return True

    @staticmethod
    def _get_image_urls(url):
        """
        漫画画像の URL を取得する
        @param url アルファボリスで漫画を表示しているページの URL
        @return ページの URL のリスト
        """
        _response = request.urlopen(url)
        if _response.getcode() != 200:
            print("漫画データの取得に失敗しました")
            return []
        _html = str(_response.read())
        _matches = re.findall(r"var\s+_base\s*=\s*\"([^\"]+)\";", _html)
        if len(_matches) == 0:
            print("漫画情報のURLの取得に失敗しました")
            return []
        _base = _matches[0]
        _matches = re.findall(r"_pages.push\(\"(\d+\.jpg)\"\);", _html)
        if len(_matches) == 0:
            print("漫画のページ情報の取得に失敗しました")
            return []
        return [_base + _page for _page in _matches]
