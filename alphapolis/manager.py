# --- coding: utf-8 ---
"""
アルファポリスから漫画をダウンロードするためのクラスモジュール
"""

import re
from manager import AbstractManager


class Manager(AbstractManager):
    """
    アルファポリスから漫画をダウンロードするクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        アルファポリスの操作を行うためのコンストラクタ
        @param directory 出力するファイル群を置くディレクトリ
        @param prefix 出力するファイル名のプレフィックス
        """
        super().__init__(browser, config, directory, prefix)

    def start(self, url=None):
        """
        ページの自動自動ダウンロードを開始する
        @param url アルフォポリスのコンテンツの URL
        """
        session = self._get_session()

        _sources = self._get_image_urls(session, url)
        _total = len(_sources)
        self._set_total(_total)

        for _index in range(_total):
            self._save_image_of_bytes(_index, session.get(_sources[_index]).content)
            self.pbar.update(1)

        return True

    @staticmethod
    def _get_image_urls(session, url):
        """
        漫画画像の URL を取得する
        @param url アルファボリスで漫画を表示しているページの URL
        @return ページの URL のリスト
        """
        _response = session.get(url)
        if _response.status_code != 200:
            raise Exception("漫画データの取得に失敗しました")
        _html = _response.text
        _matches = re.findall('_pages.push\\("(https://.+\\.jpg)"\\);', _html)
        if len(_matches) == 0:
            raise Exception("漫画のページ情報の取得に失敗しました")
        return [_page for _page in _matches]
