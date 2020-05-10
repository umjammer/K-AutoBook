# --- coding: utf-8 ---
"""
comic-action の実行クラスモジュール
"""

from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    comic-action の実行クラス
    https://comic-action.com/episode/13933686331636733009
    """

    domain_pattern = 'comic-action\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする comic-action のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        comic-action の実行
        """
        self._run('comicaction')
