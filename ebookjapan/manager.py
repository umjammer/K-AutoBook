# --- coding: utf-8 ---
"""
ebookjapanの操作を行うためのクラスモジュール
"""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from os import path
from ebookjapan.config import Config, ImageFormat, BoundOnSide
import os
import time


class Manager(object):
    """
    ebookjapanの操作を行うためのクラス
    """

    IMAGE_DIRECTORY = '/tmp/k/'
    """
    画像を一時的に保存するディレクトリ
    """

    CHECK_Y = 100
    """
    画像の色の判定を行う Y 座標
    """

    BACKGEROUND_COLOR = '#FEFFFD'
    """
    トリミングを容易にするための背景色
    """

    MAX_LOADING_TIME = 5
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
        self.browser.driver.set_window_size(self.config.window_size['width'], self.config.window_size['height'])
        print(f'{self.config.window_size["width"]}x{self.config.window_size["height"]}')

        time.sleep(2)
        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'
        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'
        self._change_background_color()
        self._check_directory(Manager.IMAGE_DIRECTORY)
        self._check_directory(self.directory)
        self._set_bound_of_side(self._get_bound_on_side())
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = (
            self.config.sleep_time if self.config is not None else 0.5)
        self._move_first_page()
        time.sleep(_sleep_time)
        _current = 1
        _count = 0
        while True:
            self._print_progress(_total, _current)
            _temporary_page = Manager.IMAGE_DIRECTORY + 'K-AutoBook.png'
            self.browser.driver.save_screenshot(_temporary_page)
            _name = '%s%s%03d%s' % (
                self.directory, self.prefix, _count, _extension)
            if _current == _total:
                self._triming(_temporary_page, _name, _format)
                break
            self._next()
            self._triming(_temporary_page, _name, _format)
            time.sleep(_sleep_time)
            _current = self._get_current_page()
            _count = _count + 1
        self._print_progress(_total, is_end=True)
        return True

    def _get_total_page(self):
        """
        全ページ数を取得する
        最初にフッタの出し入れをする
        @return 取得成功時に全ページ数を、失敗時に None を返す
        """
        _elements = self.browser.find_by_css(
            '.footer__page-output > .total-pages')
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

    def _check_directory(self, directory):
        """
        ディレクトリの存在を確認して，ない場合はそのディレクトリを作成する
        @param directory 確認するディレクトリのパス
        """
        if not path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as exception:
                print("ディレクトリの作成に失敗しました({0})".format(directory))
                raise
        return

    def _print_progress(self, total, current=0, is_end=False):
        """
        進捗を表示する
        @param total ページの総数
        @param current 現在のページ数
        @param 最後のページの場合は True を指定する
        """
        if is_end:
            print('%d/%d' % (total, total))
        else:
            print('%d/%d' % (current, total), end='')
            print('\x1B[10000D', end='', flush=True)
        return

    def _triming(self, source, destination, format):
        """
        画像の両端の色と異なる色になる場所でトリミングする
        @param source 元となる画像のパス
        @param destination 出力する画像のパス
        @param format 書き出す画像のフォーマット
        """
        _image = Image.open(source)
        _width, _height = _image.size
        _start_x = 0
        _end_x = _width
        _bases = set()
        for _point_y in range(_height):
            _bases.add(_image.getpixel((0, _point_y)))
            _bases.add(_image.getpixel((_width - 1, _point_y)))
        for _point_x in range(_width):
            _pixel = _image.getpixel((_point_x, Manager.CHECK_Y))
            if _pixel not in _bases:
                _start_x = _point_x
                break
        for _point_x in range(_width)[::-1]:
            _pixel = _image.getpixel((_point_x, Manager.CHECK_Y))
            if _pixel not in _bases:
                _end_x = _point_x + 1
                break
        if _start_x != 0:
            _start_x = _start_x + 58
            _end_x = _end_x - 58
        _image = _image.crop((_start_x, 0, _end_x, _height))
        if self.config is not None and (
                self.config.image_format == ImageFormat.JPEG):
            _image = _image.convert('RGB')
        _image.save(destination, format.upper())
        return

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

    def _change_background_color(self):
        """
        表示されている漫画ページの背景色を変更する
        """

        _script = (
            "document.body.style.backgroundColor = '%s'"
            % Manager.BACKGEROUND_COLOR)
        self.browser.evaluate_script(_script)
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
