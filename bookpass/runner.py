# --- coding: utf-8 ---
"""
bookpass の実行クラスモジュール
"""

from config import BasicSubConfig
from runner import AbstractRunner
from bookpass.manager import Manager


class Runner(AbstractRunner):
    """
    bookpass の実行クラス
    https://bookpass.auone.jp/pack/detail/?iid=BT000069318400100101&cs=top_freecomics_reco_670&pos=2&tab=1&ajb=3
    """

    domain_pattern = 'bookpass\\.auone\\.jp'
    """
    サポートするドメイン
    """

    patterns = ['pack\\/detail\\/\\?iid=([A-Z]{2}\\d+)']
    """
    サポートする bookpass のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        bookpass の実行
        """
        self.sub_config = BasicSubConfig()
        if 'bookpass' in self.config.raw:
            self.sub_config.update(self.config.raw['bookpass'])

        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        if self._move_main_page():
            print('Open main page')
        else:
            print('ページの取得に失敗しました')
            return

        # _destination = input('Output Path > ')
        _destination = self.get_id()
        print(f'Output Path : {_destination}')

        _manager = Manager(self.browser, self.sub_config, _destination)
        _result = _manager.start()
        if _result is not True:
            print(_result)
        return

    def _move_main_page(self):
        """
        実際の本のページに移動する
        """
        _elements = self.browser.find_by_css('a.button.view_button')
        if len(_elements) != 0 and '読む' in _elements.first.html:
            _elements.first.click()
            return True
        return False
