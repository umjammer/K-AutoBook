# --- coding: utf-8 ---
"""
comic-days の操作を行うためのクラスモジュール

http://redsquirrel87.altervista.org/doku.php/manga-downloader and cfr :P
"""

import json
import math
import os
import time
import requests
from os import path
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from PIL import Image
from comicdays.config import Config, ImageFormat


class Manager(object):
    """
    comic-days の操作を行うためのクラス
    """

    IMAGE_DIRECTORY = '/tmp/k/'
    """
    画像を一時的に保存するディレクトリ
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        comicdays の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        comic-days の設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
        self.cid = directory
        """
        cid
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
            raise Exception('No output directory')
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
        time.sleep(2)
        self._check_directory(self.directory)

        _sleep_time = (self.config.sleep_time if self.config is not None else 0.5)

        _script = self.browser.find_by_id('episode-json').first._element
        _json = json.loads(_script.get_attribute('data-value'))

        _pages = _json['readableProduct']['pageStructure']['pages']
        _total = len(_pages)

        self.pbar = tqdm(total=_total, bar_format='{n_fmt}/{total_fmt}')

        s = requests.session()
        s.mount('https://', HTTPAdapter(max_retries=3))
        s.headers.update({'User-Agent': f'{self.browser.driver.execute_script("return navigator.userAgent")}'})

        for i, page in enumerate([x for x in _pages if x['type'] == 'main']):
            self.fetch_page(s, self.directory, page, i)
            self.pbar.update(1)
            time.sleep(_sleep_time)

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

    @staticmethod
    def decrypt_image(src, MULTIPLE=8, DIVIDE_NUM=4):
        w, h = src.size
        cw = math.floor(w / (DIVIDE_NUM * MULTIPLE)) * MULTIPLE
        ch = math.floor(h / (DIVIDE_NUM * MULTIPLE)) * MULTIPLE
        dest = Image.new('RGB', (w, h))
        dest.paste(src)
        for e in range(0, DIVIDE_NUM * DIVIDE_NUM):
            t = math.floor(e / DIVIDE_NUM) * ch
            n = e % DIVIDE_NUM * cw
            r = math.floor(e / DIVIDE_NUM)
            i = e % DIVIDE_NUM * DIVIDE_NUM + r
            o = i % DIVIDE_NUM * cw
            s = math.floor(i / DIVIDE_NUM) * ch
            dest.paste(src.crop((n, t, n + cw, t + ch)), (o, s, o + cw, s + ch))
        return dest

    def fetch_page(self, session, title, page, count):
        _temporary_page = Manager.IMAGE_DIRECTORY + 'K-AutoBook.png'
        with open(_temporary_page, 'wb') as f:
            url = page['src']
            resp = session.get(url, stream=True, timeout=30)
            f.write(resp.content)

        _image = self.decrypt_image(Image.open(_temporary_page))
        _name = os.path.join(title, '%03d' % count + self._get_extension())
        _image.save(_name, self._get_save_format().upper())
