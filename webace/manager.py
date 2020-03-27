# --- coding: utf-8 ---
"""
web-ace の操作を行うためのクラスモジュール
"""

import io
import requests
from PIL import Image
from os import path

from requests.adapters import HTTPAdapter

from webace.config import Config, ImageFormat
import os
import time
from tqdm import tqdm


class Manager(object):
    """
    web-ace の操作を行うためのクラス
    """

    MAX_LOADING_TIME = 5
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        web-ace の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        webace の設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
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
        self.browser.driver.set_window_size(460, 600)

        time.sleep(5)
        self._check_directory(self.directory)
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = (
            self.config.sleep_time if self.config is not None else 0.5)
        time.sleep(_sleep_time)

        last_height = self.browser.driver.execute_script("return document.body.scrollHeight")

        # https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
        while True:
            # Scroll down to bottom
            self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(_sleep_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.browser.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        session = requests.session()
        session.mount('https://', HTTPAdapter(max_retries=3))
        session.headers.update({'User-Agent': f'{self.browser.driver.execute_script("return navigator.userAgent;")}'})

        imgs = self.browser.find_by_css("img.viewerFixedImage")
        _count = 0
        _total = len(imgs)
        self.pbar = tqdm(total=_total, bar_format='{n_fmt}/{total_fmt}')
        for img in imgs:
            _name = '%s%s%03d%s' % (self.directory, self.prefix, _count, _extension)

            _url = img._element.get_attribute('src')
            # print(_url)
            _image = Image.open(io.BytesIO(session.get(_url).content))
            if self.config is not None and (self.config.image_format == ImageFormat.JPEG):
                _image = _image.convert('RGB')
            _image.save(_name, _format.upper())
            self.pbar.update(1)

            time.sleep(_sleep_time)

            _count = _count + 1

        print('', flush=True)
        return True

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
