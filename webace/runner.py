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

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, manager_class=Manager)
