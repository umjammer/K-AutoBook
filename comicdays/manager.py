# --- coding: utf-8 ---
"""
comic-days の操作を行うためのクラスモジュール

http://redsquirrel87.altervista.org/doku.php/manga-downloader and cfr :P
"""

import json
from io import BytesIO
from PIL import Image
from manager import AbstractManager, decrypt_coreview_image


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

        session = self._get_session()

        for i, page in enumerate(_pages):
            self.fetch_page(session, page['src'], i)
            self.pbar.update(1)
            self._sleep()

        return True

    def fetch_page(self, session, url, count):
        _image = decrypt_coreview_image(Image.open(BytesIO(session.get(url).content)))
        if self._is_config_jpeg():
            _image = _image.convert('RGB')
        self._save_image(count, _image)
