# --- coding: utf-8 ---
"""
bookwalker の操作を行うためのクラスモジュール

@see https://github.com/xuzhengyi1995/Bookwalker_Downloader
"""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from os import path
from bookwalker.config import Config, ImageFormat
import base64
import os
import time
from tqdm import tqdm


class Manager(object):
    """
    book-walker の操作を行うためのクラス
    """

    MAX_LOADING_TIME = 10
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        book-walker の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        book-walker の設定情報
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

    @staticmethod
    def _check_is_loading(list_ele):
        is_loading = False
        for i in list_ele:
            if i.is_displayed() is True:
                is_loading = True
                break
        return is_loading

    def start(self):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        time.sleep(2)
        _total = self._get_total_page()
        if _total is None:
            return '全ページ数の取得に失敗しました'
        # print(f'total: {_total}')
        self.current_page_element = self._get_current_page_element()
        if self.current_page_element is None:
            return '現在のページ情報の取得に失敗しました'

        self._check_directory(self.directory)
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = (
            self.config.sleep_time if self.config is not None else 0.5)
        time.sleep(_sleep_time)
        _current = self._get_current_page()
        _count = 0

        # get original size?
        _dummy_canvas = self.browser.driver.find_element_by_css_selector(
            "canvas.dummy")
        self.browser.driver.set_window_size(int(_dummy_canvas.get_attribute('width')),
                                            int(_dummy_canvas.get_attribute('height')))
        print(f'size: {_dummy_canvas.get_attribute("width")}x{_dummy_canvas.get_attribute("height")}')

        self.pbar = tqdm(total=_total, bar_format='{n_fmt}/{total_fmt}')

        while True:
            _name = '%s%s%03d%s' % (self.directory, self.prefix, _count, _extension)

            canvas = self.browser.driver.find_element_by_css_selector(
                ".currentScreen canvas")
            img_base64 = self.browser.driver.execute_script(
                "return arguments[0].toDataURL('image/%s').substring(22);" % _format, canvas)
            with open(_name, 'wb') as f:
                f.write(base64.b64decode(img_base64))
            self.pbar.update(1)

            if _current == _total - 1:
                break

            self._next()
            time.sleep(_sleep_time)

            _current = self._get_current_page()
            _count = _count + 1

        print('', flush=True)
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
            if _elements.first.html != '0':
                return int(_elements.first.html.split('/')[1])
            time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        _elements = self.browser.find_by_id('pageSliderCounter')
        if len(_elements) != 0:
            return _elements.first
        return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
#        print(int(self.current_page_element.html.split('/')[0]))
        return int(self.current_page_element.html.split('/')[0])

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
        """
        next_page = self.browser.driver.find_element_by_css_selector("#renderer")
        ActionChains(self.browser.driver).move_to_element(
            next_page).click().send_keys(Keys.ARROW_LEFT).perform()
        _current = self._get_current_page()
        #WebDriverWait(self.browser.driver, 30).until_not(lambda x: self._get_current_page() == _current + 1)
        WebDriverWait(self.browser.driver, 30).until_not(lambda x: self._check_is_loading(
            x.find_elements_by_css_selector(".loading")))

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
