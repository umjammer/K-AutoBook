# --- coding: utf-8 ---
"""
kuragebunch の実行クラスモジュール
"""

from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    kuragebunch の実行クラス
    https://kuragebunch.com/episode/10834108156630826048
    """

    domain_pattern = 'kuragebunch\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする kuragebunch のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        kuragebunch の実行
        """
        self._run('kuragebunch')
