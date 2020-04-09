# --- coding: utf-8 ---
"""
magazinepocket の実行クラスモジュール
"""

from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    magazinepocket の実行クラス
    https://pocket.shonenmagazine.com/episode/13933686331610373443
    """

    domain_pattern = 'pocket\\.shonenmagazine\\.com'
    """
    サポートするドメイン
    """

    patterns = ['volume\\/(\\d+)', 'episode\\/(\\d+)']
    """
    サポートする magazinepocket のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        magazinepocket の実行
        """
        self._run('magazinepocket')
