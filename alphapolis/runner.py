# --- coding: utf-8 ---
"""
アルファポリスの実行クラスモジュール
"""

import re
from runner import AbstractRunner
from alphapolis.manager import Manager


class Runner(AbstractRunner):
    """
    アルファポリスの実行クラス
    """

    def run(self):
        """
        アルファポリスの実行
        """
        destination = self.get_output_dir()
        manager = Manager(self.browser, None, destination)
        manager.start(self.url)
