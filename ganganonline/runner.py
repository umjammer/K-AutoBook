# --- coding: utf-8 ---
"""
gangan-online の実行クラスモジュール
"""

from runner import DirectPageRunner
from ganganonline.manager import Manager


class Runner(DirectPageRunner):
    """
    gangan-online の実行クラス
    https://viewer.ganganonline.com/manga/?chapterId=15502
    """

    domain_pattern = 'viewer\\.ganganonline\\.com'
    """
    サポートするドメイン
    """

    patterns = ['manga\\/\\?chapterId=(\\d+)']
    """
    サポートする gangan-online のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        gangan-online の実行
        """
        self._run('ganganonline', Manager)
