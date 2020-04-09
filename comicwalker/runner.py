# --- coding: utf-8 ---
"""
comicwalker の実行クラスモジュール
"""

from runner import DirectPageRunner
from comicwalker.manager import Manager


class Runner(DirectPageRunner):
    """
    comic-walker の実行クラス
    https://comic-walker.com/viewer/?tw=2&dlcl=ja&cid=KDCW_MF09000001010005_68
    """

    domain_pattern = 'comic-walker\\.com'
    """
    サポートするドメイン
    """

    patterns = ['viewer\\/.*&cid=(KDCW_[A-Z]{2}[0-9]{14}_[0-9]{2})']
    """
    サポートする comic-walker のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        comic-walker の実行
        """
        self._run('comicwalker', Manager)
