# --- coding: utf-8 ---
"""
book-walker の操作を行うためのクラスモジュール

@see https://github.com/xuzhengyi1995/Bookwalker_Downloader
"""

import time
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from manager import AbstractManager


class Manager(AbstractManager):
    """
    book-walker の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        book-walker の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

        self.next_key = Keys.ARROW_LEFT
        """
        次のページに進むためのキー
        """

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self._wait()

        self._wait_loading()

        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'
        self._set_total(_total)

        # get original size
        _canvas = self.browser.driver.find_element_by_css_selector("canvas.dummy")
        self.browser.driver.set_window_size(int(_canvas.get_attribute('width')),
                                            int(_canvas.get_attribute('height')))
        print(f'size: {_canvas.get_attribute("width")}x{_canvas.get_attribute("height")}')

        self._sleep()

        for _count in range(0, _total):

            _canvas = self.browser.driver.find_element_by_css_selector(".currentScreen canvas")
            self._save_image_of_web_element(_count, _canvas)
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
        _elements = self.browser.find_by_id('pageSliderCounter')
        if len(_elements) == 0:
            return None
        for _ in range(Manager.MAX_LOADING_TIME):
            # print(_elements.first.html)
            if re.match('^\\d+/\\d+$', _elements.first.html.strip()):
                return int(_elements.first.html.split('/')[1])
            time.sleep(1)
        return None

    def _next(self):
        """
        次のページに進む
        """
        self._press_key(self.next_key)
        self._wait_loading()

    def _wait_loading(self):
        WebDriverWait(self.browser.driver, 30).until_not(lambda x: self._check_is_loading(
            x.find_elements_by_css_selector(".loading")))

    @staticmethod
    def _check_is_loading(list_ele):
        is_loading = False
        for i in list_ele:
            if i.is_displayed() is True:
                is_loading = True
                break
        return is_loading
