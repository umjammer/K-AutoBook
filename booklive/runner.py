# --- coding: utf-8 ---
"""
booklive の実行クラスモジュール
"""

from runner import DirectPageRunner
from booklive.manager import Manager


class Runner(DirectPageRunner):
    """
    booklive の実行クラス
    https://booklive.jp/bviewer/s/?cid=208562_003&rurl=https%3A%2F%2Fbooklive.jp%2Findex%2Fno-charge%2Fcategory_id%2FC
    """

    domain_pattern = 'booklive\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['bviewer\\/s\\/\\?cid=(\\d{6,8}_\\d{3})']
    """
    サポートする booklive のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        booklive の実行
        """
        self._run('booklive', Manager)
