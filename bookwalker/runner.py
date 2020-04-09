# --- coding: utf-8 ---
"""
bookwalker の実行クラスモジュール
"""

from runner import DirectPageRunner
from bookwalker.manager import Manager


class Runner(DirectPageRunner):
    """
    bookwalker の実行クラス
    https://viewer.bookwalker.jp/browserWebApi/03/view?cid=57c84cf2-7062-4ef9-9071-45fb249c926e

    詳細ページ https://bookwalker.jp/{cid}/ の赤いボタン "今すぐ読む (無料)" のリンクをコピー
    """

    domain_pattern = 'viewer\\.bookwalker\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['browserWebApi\\/\\d+\\/view\\?cid=([0-9a-f-]+)']
    """
    サポートする bookwalker のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        bookwalker の実行
        """
        self._run('bookwalker', Manager)
