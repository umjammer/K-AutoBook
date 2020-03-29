# --- coding: utf-8 ---
"""
gangan-online の操作を行うためのクラスモジュール
"""

from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from manager import AbstractManager, get_file_content_chrome


class Manager(AbstractManager):
    """
    gangan-online の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        gangan-online の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

        self.pbar = tqdm(bar_format='{n_fmt}/{total_fmt}')

        self.next_key = Keys.ARROW_LEFT
        """
        次のページに進むためのキー
        """

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self._wait()

        self.browser.driver.set_window_size(480, 640)

        _count = 0
        while True:

            img = self.browser.driver.find_element_by_xpath("//img[starts-with(@src, 'blob:')]")
            try:
                self.browser.driver.find_element_by_xpath("//button[text() = '閉じる']")
                break
            except:
                if _count != 0:
                    self._save_image_of_bytes(_count, get_file_content_chrome(self.browser.driver, img.get_attribute('src')))
                    self.pbar.update(1)

                self._next()
                self._sleep()

                _count = _count + 1

        return True

    def _next(self):
        """
        次のページに進む
        """
        self._press_key(self.next_key)
