# --- coding: utf-8 ---
"""
設定クラスモジュール
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
        self.raw = data
        """
        raw data
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
        if 'chrome_binary' in data:
            self.chrome_binary = data['chrome_binary']
        if 'headless' in data:
            self.headless = bool(data['headless'])
        if 'log_directory' in data:
            self.log_directory = data['log_directory']
        return
