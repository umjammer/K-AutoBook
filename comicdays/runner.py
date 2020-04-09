# --- coding: utf-8 ---
"""
comic-days の実行クラスモジュール
"""

from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    comic-days の実行クラス
    https://comic-days.com/volume/13932016480030155016
    """

    domain_pattern = 'comic-days\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする comic-days のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        comic-days の実行
        """
        self._run('comicdays')
