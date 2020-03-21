# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

from ebookjapan.config import Config as EbookjapanConfig
from bookwalker.config import Config as BookwalkerConfig
from ganganonline.config import Config as GanganonlineConfig
from linemanga.config import Config as LinemangaConfig
from comicwalker.config import Config as ComicwalkerConfig

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
        self.chrome_path = '/usr/local/bin/chromedriver'
        """
        開くブラウザのドライバ
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
        self.ebookjapan = EbookjapanConfig()
        """
        ebookjapan の設定情報
        """
        self.bookwalker = BookwalkerConfig()
        """
        bookwalker の設定情報
        """
        self.ganganonline = GanganonlineConfig()
        """
        ganganonline の設定情報
        """
        self.linemanga = LinemangaConfig()
        """
        linemanga の設定情報
        """
        self.comicwalker = ComicwalkerConfig()
        """
        comicwalker の設定情報
        """
        if isinstance(data, dict):
            self.update(data)
        return

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
        if 'headless' in data:
            self.headless = bool(data['headless'])
        if 'log_directory' in data:
            self.log_directory = data['log_directory']
        if 'ebookjapan' in data:
            self.ebookjapan.update(data['ebookjapan'])
        if 'bookwalker' in data:
            self.bookwalker.update(data['bookwalker'])
        if 'ganganonline' in data:
            self.ganganonline.update(data['ganganonline'])
        if 'linemanga' in data:
            self.linemanga.update(data['linemanga'])
        if 'comicwalker' in data:
            self.comicwalker.update(data['comicwalker'])
        return
