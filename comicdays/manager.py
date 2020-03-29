# --- coding: utf-8 ---
"""
comic-days の操作を行うためのクラスモジュール

http://redsquirrel87.altervista.org/doku.php/manga-downloader and cfr :P
"""

import json
import math
from io import BytesIO
from PIL import Image
from manager import AbstractManager, get_session


class Manager(AbstractManager):
    """
    comic-days の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        comic-days の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self._wait()

        _script = self.browser.find_by_id('episode-json').first._element
        _json = json.loads(_script.get_attribute('data-value'))
        _pages = [x for x in _json['readableProduct']['pageStructure']['pages'] if x['type'] == 'main']
        self._set_total(len(_pages))

        session = get_session(self.browser.driver.execute_script("return navigator.userAgent;"))

        for i, page in enumerate(_pages):
            self.fetch_page(session, page['src'], i)
            self.pbar.update(1)
            self._sleep()

        return True

    @staticmethod
    def decrypt_image(src, MULTIPLE=8, DIVIDE_NUM=4):
        """
        coreview decryption
        """
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

    def fetch_page(self, session, url, count):
        _image = self.decrypt_image(Image.open(BytesIO(session.get(url).content)))
        if self._is_config_jpeg():
            _image = _image.convert('RGB')
        self._save_image(count, _image)
