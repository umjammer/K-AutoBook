# --- coding: utf-8 ---
"""
jumpplus の実行クラスモジュール
"""

from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    jumpplus の実行クラス
    https://shonenjumpplus.com/episode/13932016480031086197
    """

    domain_pattern = 'shonenjumpplus\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする jumpplus のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        jumpplus の実行
        """
        self._run('jumpplus')
