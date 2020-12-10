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

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, manager_class=Manager)
