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

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, manager_class=Manager)
