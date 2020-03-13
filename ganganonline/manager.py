# --- coding: utf-8 ---
"""
ganganonline の操作を行うためのクラスモジュール
"""
import base64

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from os import path
from ganganonline.config import Config, ImageFormat
import os
import time


class Manager(object):
    """
    ganganonline の操作を行うためのクラス
    """

    MAX_LOADING_TIME = 5
    """
    初回読み込み時の最大待ち時間
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        ganganonline の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        ganganonline の設定情報
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

    def _get_file_content_chrome(self, uri):
        """
        https://stackoverflow.com/questions/47424245/how-to-download-an-image-with-python-3-selenium-if-the-url-begins-with-blob
        """
        result = self.browser.driver.execute_async_script("""
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

    def start(self):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self.browser.driver.set_window_size(460, 600)

        time.sleep(2)
        self._check_directory(self.directory)
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = (
            self.config.sleep_time if self.config is not None else 0.5)
        time.sleep(_sleep_time)

        _count = 0
        while True:
            self._print_progress(-1, _count + 1)
            _name = '%s%s%03d%s' % (
                self.directory, self.prefix, _count, _extension)

            img = self.browser.driver.find_element_by_xpath("//img[starts-with(@src, 'blob:')]")
            try:
                self.browser.driver.find_element_by_xpath("//button[text() = '閉じる']")
                break
            except:
                image = self._get_file_content_chrome(img.get_attribute('src'))
                if _count != 0:
                    with open(_name, 'wb') as f:
                        f.write(image)

                self._next()
                time.sleep(_sleep_time)

                _count = _count + 1
        self._print_progress(-1, is_end=True)
        return True

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