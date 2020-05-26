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

    domain_pattern = 'www\\.cmoa\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['bib\\/speedreader\\/speed.html\\?cid=(\\d{10}_[a-z]{2}_\\d{4})']
    """
    サポートする comic-cmoa のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        comic-cmoa の実行
        """
        self._run('cmoa', Manager, SubConfigWithCookie, 'cmoa.jp', 'https://www.cmoa.jp/')

    def _save_sub_cookie(self, cookie):
        self.config.save_sub_cookie('cmoa', cookie)
