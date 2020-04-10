# --- coding: utf-8 ---
"""
booklive の操作を行うためのクラスモジュール
"""

import re
import time
from selenium.webdriver.common.keys import Keys
from manager import AbstractManager
from PIL import Image


class Manager(AbstractManager):
    """
    booklive の操作を行うためのクラス
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
        self.browser.driver.set_window_size(480, 640)

        self._wait()

        _total = self._get_total_page()
        if not _total:
            return '全ページ数の取得に失敗しました'

        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'

        self._set_total(_total)
        for _count in range(0, _total):

            _imgs = self.browser.find_by_css(f"#content-p{_count + 1} div.pt-img img")
            _images = [self._get_image_by_url(_img._element.get_attribute('src')) for _img in _imgs]
            # print(f'images: {len(_images)}')
            _hb = _images[-1].size[1]
            _w = _images[0].size[0]
            _h = sum(self._get_height(_image.size[1], _hb) for _image in _images)
            _dest = Image.new('RGB', (_w, _h))
            _hh = 0
            for _image in _images:
                _dest.paste(_image, (0, _hh, _w, _hh + _image.size[1]))
                _hh += self._get_height(_image.size[1], _hb)
            self._save_image(_count, _dest)

            self.pbar.update(1)

            self._next()
            self._sleep()

        return True

    @staticmethod
    def _get_height(height, base):
        """
        TODO without any reasons
        """
        if base == 534:  # 1600
            if height != base:
                base = 533
        elif base == 400:  # 1200
            pass
        else:
            print(f'unknown base {base}')
        _margin = height - base
        return height - _margin

    def _get_total_page(self):
        """
        全ページ数を取得する
        最初にフッタの出し入れをする
        @return 取得成功時に全ページ数を、失敗時に None を返す
        """
        for _ in range(Manager.MAX_LOADING_TIME):
            _elements = self.browser.find_by_css('#menu_slidercaption')
            if len(_elements) != 0:
                print(_elements.first.html)
                if re.match('^\\d+/\\d+$', _elements.first.html):
                    return int(_elements.first.html.split('/')[1])
            time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_css('#menu_slidercaption')
        if len(_elements) != 0:
            return _elements.first
        print("no current")
        return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
        try:
            return int(self.current_page_element.html.split('/')[0])
        except:
            return 0

    def _next(self):
        """
        次のページに進む
        """
        _current_page = self._get_current_page()
        self._press_key(self.next_key)
        if self._get_current_page() and self._get_current_page() < self.pbar.total - 1:
            while self._get_current_page() != _current_page + 1:
                time.sleep(0.1)
