# --- coding: utf-8 ---
"""
ebookjapanの操作を行うためのクラスモジュール
"""

import base64
import io
import time
from PIL import Image
from retry import retry
from selenium.webdriver.common.keys import Keys
from ebookjapan.config import BoundOnSide
from manager import AbstractManager


class Manager(AbstractManager):
    """
    ebookjapanの操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        ebookjapanの操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

        self.next_key = None
        """
        次のページに進むためのキー
        """
        self.previous_key = None
        """
        前のページに戻るためのキー
        """
        self.current_page_element = None
        """
        現在表示されているページのページ番号が表示されるエレメント
        """
        self.retry_count = 0

        self._set_bound_of_side(None)

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self._wait()

        # resize by option
        self._sleep(2)
        self.browser.driver.set_window_size(1300, 1800)
        self._sleep(2)
        _canvas = self.browser.find_by_css('canvas').first._element
        _height = int(_canvas.get_attribute('height'))
        print(f'height: {_height}')
        self.browser.driver.set_window_size(200, 320)
        self._sleep(2)
        _canvas = self.browser.find_by_css('canvas').first._element
        _width = int(_canvas.get_attribute('width'))
        print(f'width: {_width}')
        self.browser.driver.set_window_size(_width, _height)
        self._sleep()
        print(f'{_width}x{_height}')

        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'

        _excludes = self._get_blank_check_exclude_pages(_total)
        print(f'excludes: {_excludes}')

        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'

        self._set_bound_of_side(self._get_bound_on_side())

        self._move_first_page()
        self._sleep()

        while self._get_current_page() != 1:
            time.sleep(0.1)

        self._set_total(_total)
        for _count in range(0, _total):

            self.retry_count = 0
            self._save_image(_count, self._capture(_count in _excludes))
            self.pbar.update(1)

            self._next()
            self._sleep()

        return True

    def _get_blank_check_exclude_pages(self, _total):
        return [(_total - 1 + p) if p <= 0 else p for p in self.config.blank_check_excludes]

    def _get_total_page(self):
        """
        全ページ数を取得する
        最初にフッタの出し入れをする
        @return 取得成功時に全ページ数を、失敗時に None を返す
        """
        _elements = self.browser.find_by_css('.footer__page-output > .total-pages')
        if len(_elements) == 0:
            return None
        for _ in range(Manager.MAX_LOADING_TIME):
            if _elements.first.html != '0':
                return int(_elements.first.html)
            time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_css('.footer__page-output > output')
        if len(_elements) != 0:
            return _elements.first
        return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
        try:
            return int(self.current_page_element.html[:-2])
        except:
            return 0

    @retry(tries=10, delay=1)
    def _capture(self, ignore_blank):
        """
        @param ignore_blank キャプチャミスを無視するかどうか
        """
        _base64_image = self.browser.driver.get_screenshot_as_base64()
        _image = Image.open(io.BytesIO(base64.b64decode(_base64_image)))
        if self._is_config_jpeg():
            _image = _image.convert('RGB')

        if self._is_blank_image(_image):
            print(f' blank page detected {self.retry_count}')
            if not ignore_blank:
                if self.retry_count < self.config.blank_check_giveup:
                    self.retry_count += 1
                    raise Exception
                else:
                    print(' give up checking, ignore blank')

        return _image

    @staticmethod
    def _is_blank_image(image):
        _width, _height = image.size
        for y in range(_height):
            for x in range(_width):
                r, g, b = image.getpixel((x, y))
                if r != 255 or g != 255 or b != 255:
                    return False
        return True

    def _next(self):
        """
        次のページに進む
        スペースで次のページにすすめるのでスペースキー固定
        """
        _current_page = self._get_current_page()
        self._press_key(self.next_key)
        if self._get_current_page() and self._get_current_page() < self.pbar.total - 1:
            while self._get_current_page() and self._get_current_page() != _current_page + 1:
                time.sleep(0.1)

    def _previous(self):
        """
        前のページに戻る
        """
        self._press_key(self.previous_key)

    def _move_first_page(self):
        """
        先頭ページに移動
        """
        while self._get_current_page() != 1:
            self._previous()

    def _get_bound_on_side(self):
        _current = self._get_current_page()
        self._press_key(Keys.ARROW_LEFT)
        if _current < self._get_current_page():
            return BoundOnSide.RIGHT
        else:
            return BoundOnSide.LEFT

    def _set_bound_of_side(self, bound_on_side):
        """
        ページの綴じ場所から次/前のページへの移動キーを設定する
        @param bound_on_side ページの綴じ場所
        """
        _result = BoundOnSide.RIGHT
        if bound_on_side in {BoundOnSide.RIGHT, BoundOnSide.LEFT}:
            _result = bound_on_side
        elif self.config is not None:
            _result = self.config.bound_on_side
        if _result == BoundOnSide.LEFT:
            self.next_key = Keys.ARROW_RIGHT
            self.previous_key = Keys.ARROW_LEFT
        else:
            self.next_key = Keys.ARROW_LEFT
            self.previous_key = Keys.ARROW_RIGHT
