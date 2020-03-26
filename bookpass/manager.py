# --- coding: utf-8 ---
"""
bookpass の操作を行うためのクラスモジュール
"""

import base64
from tqdm import tqdm
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from os import path
from bookpass.config import Config, ImageFormat
import os
import time


class Manager(object):
    """
    bookpass の操作を行うためのクラス
    """

    MAX_LOADING_TIME = 5
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        bookpass の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        bookpass の設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
        self.next_key = Keys.ARROW_LEFT
        """
        次のページに進むためのキー
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
        print("Change output directory to '%s' because '%s' already exists"
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
        time.sleep(5)
        self._check_directory(self.directory)
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = self.config.sleep_time if self.config is not None else 0.5
        time.sleep(_sleep_time)

        _canvas = self.browser.find_by_css("div.page > canvas").first._element
        self.browser.driver.set_window_size(int(_canvas.get_attribute('width')),
                                            int(_canvas.get_attribute('height')))
        print(f'size: {_canvas.get_attribute("width")}x{_canvas.get_attribute("height")}')

        self._skip_first_dialog()
        time.sleep(_sleep_time)

        _touch = self.browser.find_by_css("div.Viewer-fit-fill").first

        _touch.click()  # show slider
        _total = self._get_total_page()
        if not _total:
            return '全ページ数の取得に失敗しました'
        time.sleep(_sleep_time)

        _touch = self.browser.find_by_css("body").first
        _touch.click()  # hide slider
        time.sleep(_sleep_time)

        _count = 0
        self.pbar = tqdm(total=_total, bar_format='{n_fmt}/{total_fmt}')
        while _count < _total:
            _name = '%s%s%03d%s' % (self.directory, self.prefix, _count, _extension)

            _canvas = self.browser.find_by_css("div.page > canvas").first._element
            img_base64 = self.browser.driver.execute_script(
                "return arguments[0].toDataURL('image/%s').substring(22);" % _format, _canvas)
            with open(_name, 'wb') as f:
                f.write(base64.b64decode(img_base64))
            self.pbar.update(1)

            self._next()
            time.sleep(_sleep_time)

            _count = _count + 1

        print('', flush=True)
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

    def _skip_first_dialog(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_css('button.Btn_cancel')
        if len(_elements) != 0 and '見ない' in _elements.first.html:
            print('first dialog found, skip...')
            _elements.first.click()
        else:
            print('first dialog not found')

    @staticmethod
    def _check_directory(directory):
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

    def _next(self):
        """
        次のページに進む
        スペースで次のページにすすめるのでスペースキー固定
        """
        self._press_key(self.next_key)
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
