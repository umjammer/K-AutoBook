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

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, manager_class=Manager)
