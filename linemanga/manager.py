# --- coding: utf-8 ---
"""
line-manga の操作を行うためのクラスモジュール
"""

import base64
import re
import time
from selenium.webdriver.common.keys import Keys
from manager import AbstractManager


class Manager(AbstractManager):
    """
    line-manga の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        line-manga の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

        self.next_key = Keys.ARROW_LEFT
        """
        次のページに進むためのキー
        """
        self.current_page_element = None
        """
        現在表示されているページのページ番号が表示されるエレメント
        """

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self._wait()

        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'

        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'

        # get original size
        _canvas = self.browser.driver.find_element_by_css_selector("canvas.dummy")
        self.browser.driver.set_window_size(int(_canvas.get_attribute('width')),
                                            int(_canvas.get_attribute('height')))
        print(f'size: {_canvas.get_attribute("width")}x{_canvas.get_attribute("height")}')

        self._sleep()

        self._set_total(_total)
        for _count in range(0, _total):

            _base64_image = self.browser.driver.get_screenshot_as_base64()
            self._save_image_of_bytes(_count, base64.b64decode(_base64_image))
            self.pbar.update(1)

            self._next()
            self._sleep()

        return True

    def _get_total_page(self):
        """
        全ページ数を取得する
        最初にフッタの出し入れをする
        @return 取得成功時に全ページ数を、失敗時に None を返す
        """
        for _ in range(Manager.MAX_LOADING_TIME):
            _elements = self.browser.find_by_css("span.fnViewerSliderNumTotal")
            if len(_elements) != 0:
                # print(f'"{_elements.first.html}"')
                if re.match(r'^\d+$', _elements.first.html.strip()):
                    return int(_elements.first.html.strip())
            time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_css("b.fnViewerSliderNumCurrent")
        if len(_elements) != 0:
            return _elements.first
        return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
        # print(int(self.current_page_element.html))
        return int(self.current_page_element.html)

    def _next(self):
        """
        次のページに進む
        """
        _current_page = self._get_current_page()
        self._press_key(self.next_key)
        if self._get_current_page() < self.pbar.total - 1:
            while self._get_current_page() != _current_page + 1:
                time.sleep(0.1)
