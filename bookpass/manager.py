# --- coding: utf-8 ---
"""
bookpass の操作を行うためのクラスモジュール
"""

import time
from selenium.webdriver.common.keys import Keys
from manager import AbstractManager


class Manager(AbstractManager):
    """
    bookpass の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        bookpass の操作を行うためのコンストラクタ
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

        _canvas = self.browser.find_by_css("div.page > canvas").first._element
        self.browser.driver.set_window_size(int(_canvas.get_attribute('width')),
                                            int(_canvas.get_attribute('height')))
        print(f'size: {_canvas.get_attribute("width")}x{_canvas.get_attribute("height")}')

        self._skip_first_dialog()
        self._sleep()

        _touch = self.browser.find_by_css("div.Viewer-fit-fill").first
        _touch.click()  # show slider
        self._sleep()

        _total = self._get_total_page()
        if not _total:
            return '全ページ数の取得に失敗しました'

        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'

        _touch = self.browser.find_by_css("body").first
        _touch.click()  # hide slider
        self._sleep()

        self._set_total(_total)
        for _count in range(0, _total):

            _canvas = self.browser.find_by_css("div.page > canvas").first._element
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
        _elements = self.browser.find_by_css('span.maxIndexLabel')
        if len(_elements) == 0:
            # print("no total")
            return None
        for _ in range(Manager.MAX_LOADING_TIME):
            # print(_elements.first.html)
            if _elements.first.html != '{{ value + 1 }}':
                return int(_elements.first.html)
            time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_css('span.indexLabel')
        if len(_elements) != 0:
            return _elements.first
        print("no current")
        return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
        return int(self.current_page_element.html)

    def _skip_first_dialog(self):
        """
        skip help dialog
        """
        _elements = self.browser.find_by_css('button.Btn_cancel')
        if len(_elements) != 0 and '見ない' in _elements.first.html:
            print('first dialog found, skip...')
            _elements.first.click()
        else:
            print('first dialog not found')

    def _next(self):
        """
        次のページに進む
        """
        _current_page = self._get_current_page()
        self._press_key(self.next_key)
        if self._get_current_page() < self.pbar.total - 1:
            while self._get_current_page() != _current_page + 1:
                time.sleep(0.1)
