# --- coding: utf-8 ---
"""
comicwalker の操作を行うためのクラスモジュール

https://github.com/YunzheZJU/ComicWalkerWalker
"""

import json
import os
import struct
import time
from os import path
from tqdm import tqdm
import requests
from requests.adapters import HTTPAdapter

from comicwalker.config import Config, ImageFormat


class Manager(object):
    """
    comicwalker の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        comicwalker の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        comicwalker の設定情報
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
        s = requests.session()
        s.mount('https://', HTTPAdapter(max_retries=3))
        s.headers.update({'User-Agent': f'{self.browser.driver.execute_script("return navigator.userAgent;")}'})

        time.sleep(2)
        self._check_directory(self.directory)

        _sleep_time = (self.config.sleep_time if self.config is not None else 0.5)
        time.sleep(_sleep_time)

        self.pbar = tqdm(bar_format='{n_fmt}/{total_fmt}')

        self.fetch_episode(s, self.directory, self.cid)

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
    def generate(key):
        result = []
        for i, k in enumerate(key):
            code = ord(k)
            code = code - 87 if code >= 97 else code - 48
            if i % 2 == 0:
                result.append(code * 16)
            else:
                result[(i - 1) // 2] += code
        return result

    def fetch_page(self, session, title, page, count):
        # pid = page['id']
        fn = os.path.join(title, '%03d' % count + self._get_extension())
        with open(fn, 'wb') as f:
            url = page['meta']['source_url']
            key = Manager.generate(page['meta']['drm_hash'][:16])
            resp = session.get(url, stream=True, timeout=30)
            for i, c in enumerate(resp.content):
                f.write(struct.pack('B', c ^ key[i % 8]))
        self.pbar.update(1)

    def fetch_episode(self, session, title, cid):
        resp = session.get('https://ssl.seiga.nicovideo.jp/api/v1/comicwalker/episodes/' + cid + '/frames', timeout=30)
        frame = json.loads(resp.text)['data']['result']
        for i, page in enumerate(frame):
            self.fetch_page(session, title, page, i)
