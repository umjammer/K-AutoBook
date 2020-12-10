# --- coding: utf-8 ---
"""
comic-cmoa の実行クラスモジュール
"""

from config import SubConfigWithCookie
from runner import DirectPageRunner
from booklive.manager import Manager


class Runner(DirectPageRunner):
    """
    comic-cmoa の実行クラス
    https://www.cmoa.jp/bib/speedreader/speed.html?cid=0000101745_jp_0002&u0=1&u1=0&rurl=https%3A%2F%2Fwww.cmoa.jp%2Ftitle%2F101745%2Fvol%2F2%2F
    """

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, SubConfigWithCookie, Manager)
