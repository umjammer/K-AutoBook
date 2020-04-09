# --- coding: utf-8 ---
"""
zebrackcomic の実行クラスモジュール
"""

import time
from config import BasicSubConfig
from runner import AbstractRunner
from zebrackcomic.manager import Manager


class Runner(AbstractRunner):
    """
    zebrack-comic の実行クラス
    https://zebrack-comic.com/title/37/volume/1498/viewer
    """

    domain_pattern = 'zebrack-comic\\.com'
    """
    サポートするドメイン
    """

    patterns = ['title\\/(\\d+)\\/volume\\/(\\d+)']
    """
    サポートする zebrackcomic のパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        zebrack-comic の実行
        """
        self.sub_config = BasicSubConfig()
        if 'zebrackcomic' in self.config.raw:
            self.sub_config.update(self.config.raw['zebrackcomic'])

        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        _destination = self.get_id()
        # _destination = input('Output Path > ')
        print(f'Output Path : {_destination}')

        if self._move_main_page():
            print('Open main page')
        else:
            print('ページの取得に失敗しました')
            return

        _manager = Manager(
            self.browser, self.sub_config, _destination)
        _result = _manager.start()
        if _result is not True:
            print(_result)

    def _move_main_page(self):
        """
        実際の本のページに移動する
        """
        time.sleep(3)
        _elements = self.browser.find_by_css('button.undefined')
        if len(_elements) != 0:
            _elements.first.click()
            time.sleep(.5)
            try:
                _elements = self.browser.driver.find_element_by_xpath("//*[text()='無料で読む']")
                _elements.click()
                return True
            except Exception as e:
                raise e
        return False

    def need_reset(self):
        return True
