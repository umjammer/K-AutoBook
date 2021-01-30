# --- coding: utf-8 ---
"""
piccoma の実行クラスモジュール
"""
from piccoma.manager import Manager
from runner import DirectPageRunner


class Runner(DirectPageRunner):
    """
    piccoma の実行クラス
    https://piccoma.com/web/viewer/4267/1471900
    """

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, manager_class=Manager)

