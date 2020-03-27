# --- coding: utf-8 ---
"""
ebookjapanの操作を行うためのクラスモジュール
"""

import base64
import io
import time
from os import path, listdir, makedirs
from PIL import Image
from retry import retry
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from ebookjapan.config import Config, ImageFormat, BoundOnSide


class Manager(object):
    """
    ebookjapanの操作を行うためのクラス

    trimming has eliminated.
    you should set screen size option in "config.json" or write command line option like
    ```
    Input URL > https://ebookjapan.yahoo.co.jp/books/119594/A000048753/ {"window_size":{"width":784,"height":1200}}
    ```

    how to know screen size
    F12 -> Application -> Frames/Images/'blob:https://ebookjapan.yahoo.co.jp/...'
     * click the address above
     * left pane, encrypted image would be shown, status bar, image size would be shown
     * we'd like to use this size, but we need some calculation for height (like 1248 -> 1200, 1672 -> 1600?, etc.)
     * for width, we can find from the html source, css selector: "canvas", attribute: "width"
    the calculation rule is unknown, i use practical values.
    if we want to get original size, we need to decrypt images
    i know how to decrypt images but i don't know how to get images...

    i really not recommend to use this plugin, use original version of ebookjapan, it's safety.
    """

    MAX_LOADING_TIME = 10
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        ebookjapanの操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        ebookjapan の設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
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
        self.pbar = None
        """
        progress bar
        """

        self._set_directory(directory)
        self._set_prefix(prefix)
        self._set_bound_of_side(None)
        return

    def _set_directory(self, directory):
        """
        ファイルを出力するディレクトリを設定する
        """
        if directory == '':
            self.directory = './'
            print('Output to current directory')
            return
        _base_path = directory.rstrip('/')
        if _base_path == '':
            _base_path = '/'
        elif not path.exists(_base_path):
            self.directory = _base_path + '/'
            return
        else:
            if not len(listdir(_base_path)):
                print(f"Output directory {_base_path} exists but empty")
                self.directory = _base_path + '/'
                return
            _base_path = _base_path + '-'
        i = 1
        while path.exists(_base_path + str(i)):
            i = i + 1
        self.directory = _base_path + str(i) + '/'
        print("Change output directory to '%s' because '%s' alreadly exists"
              % (self.directory, directory))
        return

    def _set_prefix(self, prefix):
        """
        出力ファイルのプレフィックス
        """
        self.prefix = prefix
        return

    def start(self):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        # resize by option
        self.browser.driver.set_window_size(self.config.window_size['width'], self.config.window_size['height'])

        time.sleep(2)
        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'

        _excludes = self._get_blank_check_exclude_pages(_total)
        print(f'excludes: {_excludes}')

        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'
        self._check_directory(self.directory)
        self._set_bound_of_side(self._get_bound_on_side())
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = self.config.sleep_time if self.config is not None else 0.5
        self._move_first_page()
        time.sleep(_sleep_time)

        # re-resize by source
        _canvas = self.browser.find_by_css('canvas').first._element
        _width = _canvas.get_attribute('width')
        self.browser.driver.set_window_size(_width, self.config.window_size['height'])
        print(f'{_width}x{self.config.window_size["height"]}')

        while self._get_current_page() != 1:
            time.sleep(0.1)

        _current = 1
        _count = 0
        self.pbar = tqdm(total=_total, bar_format='{n_fmt}/{total_fmt}')

        while True:

            _image = self._capture(_count in _excludes)
            _name = '%s%s%03d%s' % (self.directory, self.prefix, _count, _extension)
            _image.save(_name, _format.upper())
            self.pbar.update(1)

            if _current < _total:
                self._next()
                while self._get_current_page() != _current + 1:
                    time.sleep(0.1)
                time.sleep(_sleep_time)
            else:
                break

            _current = self._get_current_page()
            _count = _count + 1

        print('', flush=True)
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
        return int(self.current_page_element.html[:-2])

    @staticmethod
    def _check_directory(directory):
        """
        ディレクトリの存在を確認して，ない場合はそのディレクトリを作成する
        @param directory 確認するディレクトリのパス
        """
        if not path.isdir(directory):
            try:
                makedirs(directory)
            except OSError as exception:
                print("ディレクトリの作成に失敗しました({0})".format(directory))
                raise
        return

    @retry(tries=10, delay=1)
    def _capture(self, ignore_blank):
        """
        @param ignore_blank キャプチャミスを無視するかどうか
        """
        _base64_image = self.browser.driver.get_screenshot_as_base64()
        _image = Image.open(io.BytesIO(base64.b64decode(_base64_image)))
        if self.config is not None and (self.config.image_format == ImageFormat.JPEG):
            _image = _image.convert('RGB')

        if self._is_blank_image(_image):
            print(' blank page detected')
            if not ignore_blank:
                raise Exception

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
        self._press_key(self.next_key)
        return

    def _previous(self):
        """
        前のページに戻る
        """
        self._press_key(self.previous_key)
        return

    def _move_first_page(self):
        """
        先頭ページに移動
        """
        while self._get_current_page() != 1:
            self._previous()
        return

    def _press_key(self, key):
        """
        指定したキーを押す
        """
        ActionChains(self.browser.driver).key_down(key).perform()
        return

    def _get_extension(self):
        """
        書き出すファイルの拡張子を取得する
        @return 拡張子
        """
        if self.config is not None:
            if self.config.image_format == ImageFormat.JPEG:
                return '.jpg'
            elif self.config.image_format == ImageFormat.PNG:
                return '.png'
        return '.jpg'

    def _get_save_format(self):
        """
        書き出すファイルフォーマットを取得する
        @return ファイルフォーマット
        """
        if self.config is not None:
            if self.config.image_format == ImageFormat.JPEG:
                return 'jpeg'
            elif self.config.image_format == ImageFormat.PNG:
                return 'png'
        return 'jpeg'

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
        return
