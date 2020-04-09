# --- coding: utf-8 ---
"""
web-ace の実行クラスモジュール
"""

from runner import DirectPageRunner
from webace.manager import Manager


class Runner(DirectPageRunner):
    """
    web-ace の実行クラス
    https://web-ace.jp/youngaceup/contents/1000053/episode/1092/
    """

    domain_pattern = 'web-ace\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['youngaceup\\/contents\\/(\\d+)\\/episode\\/(\\d+)']
    """
    サポートする web-ace のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        web-ace の実行
        """
        self._run('webace', Manager)

    def need_reset(self):
        return True
