# --- coding: utf-8 ---
"""
操作を行うためのクラスモジュール
"""

import base64
import io
import time
from abc import ABC, abstractmethod
from os import path, listdir, makedirs
import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from config import AbstractConfig, ImageFormat


class AbstractManager(ABC):
    """
    base class for manager
    """

    MAX_LOADING_TIME = 10
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser=None, config=None, directory='./', prefix=''):
        """
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, AbstractConfig) else None
        """
        設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = prefix
        """
        出力するファイルのプレフィックス
        """
        self.pbar = None
        """
        progress bar
        """

        self._set_directory(directory)
        self._check_directory()

        self._extension = self._get_extension()
        self._format = self._get_save_format()
        self._sleep_time = self.config.sleep_time if self.config is not None else 0.5

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
        print("Change output directory to '%s' because '%s' already exists"
              % (self.directory, directory))

    def _wait(self):
        WebDriverWait(self.browser.driver, self.MAX_LOADING_TIME).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete')

    def _wait_located(self, element):
        WebDriverWait(self.browser.driver, self.MAX_LOADING_TIME).until(EC.presence_of_element_located(element))

    def _get_session(self):
        return get_session(self.browser.driver.execute_script("return navigator.userAgent;"))

    def _set_total(self, total):
        self.pbar = tqdm(total=total, bar_format='{n_fmt}/{total_fmt}')
        # print(f'total: {_total}')

    def _save_image_of_web_element(self, count, element):
        _base64_image = self.browser.driver.execute_script(
            "return arguments[0].toDataURL('image/%s').substring(22);" % self._format, element)
        _name = '%s%s%03d%s' % (self.directory, self.prefix, count, self._extension)
        with open(_name, 'wb') as f:
            f.write(base64.b64decode(_base64_image))

    def _save_image_of_bytes(self, count, bytes_):
        _image = Image.open(io.BytesIO(bytes_))
        if self._is_config_jpeg():
            _image = _image.convert('RGB')
        self._save_image(count, _image)

    def _save_image(self, count, image):
        _name = '%s%s%03d%s' % (self.directory, self.prefix, count, self._extension)
        image.save(_name, self._format.upper())

    def _is_config_jpeg(self):
        return self.config is not None and self.config.image_format == ImageFormat.JPEG

    def _sleep(self):
        time.sleep(self._sleep_time)

    def _press_key(self, key):
        """
        指定したキーを押す
        """
        ActionChains(self.browser.driver).key_down(key).perform()

    @abstractmethod
    def start(self, url=None):
        """
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        pass

    def _check_directory(self):
        """
        ディレクトリの存在を確認して，ない場合はそのディレクトリを作成する
        @param directory 確認するディレクトリのパス
        """
        if not path.isdir(self.directory):
            try:
                makedirs(self.directory)
            except OSError as exception:
                print("ディレクトリの作成に失敗しました({0})".format(self.directory))
                raise

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


def get_file_content_chrome(driver, uri):
    """
    https://stackoverflow.com/questions/47424245/how-to-download-an-image-with-python-3-selenium-if-the-url-begins-with-blob
    """
    result = driver.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[1];
    var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, uri)
    if type(result) == int:
        raise Exception("Request failed with status %s" % result)
    return base64.b64decode(result)


def scroll_down(driver, wait):
    """
    https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    """

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(wait)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_session(ua):
    session = requests.session()
    session.mount('https://', HTTPAdapter(max_retries=3))
    session.headers.update({'User-Agent': f'{ua}'})
    return session