# --- coding: utf-8 ---
"""
zebrack-comic の操作を行うためのクラスモジュール
"""

import re
import time
from retry import retry
from selenium.webdriver.common.keys import Keys
from manager import AbstractManager, get_file_content_chrome


class Manager(AbstractManager):
    """
    zebrack-comic の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        zebrack-comic の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

        self.next_key = Keys.ARROW_LEFT
        """
        次のページに進むためのキー
        """
        self.current_page_element = None
        """
        現在表示されているページのページ番号が表示されるエレメント
        """

    def start(self, url=None):
        """
        ページの自動スクリーンショットを開始する
        @return エラーが合った場合にエラーメッセージを、成功時に True を返す
        """
        self.browser.driver.set_window_size(480, 640)

        self._wait()

        _total = self._get_total_page()
        self._set_total(_total)

        for _count in range(0, _total):

            img = self._get_img()
            self._save_image_of_bytes(_count, get_file_content_chrome(self.browser.driver, img.get_attribute('src')))
            self.pbar.update(1)

            self._next()
            self._sleep()

        return True

    @retry(tries=3, delay=1)
    def _get_img(self):
        return self.browser.driver.find_element_by_xpath("//img[starts-with(@src, 'blob:')]")

    def _get_total_page(self):
        """
        全ページ数を取得する
        最初にフッタの出し入れをする
        @return 取得成功時に全ページ数を、失敗時に None を返す
        """
        for _ in range(Manager.MAX_LOADING_TIME):
            try:
                _element = self.browser.driver.find_element_by_xpath("//*[@id='root']/*/div/div[3]/p")
                # print(_element.get_attribute('innerHTML'))
                if re.match('^\\d+ / \\d+$', _element.get_attribute('innerHTML')):
                    return int(_element.get_attribute('innerHTML').split('/')[1].strip())
            except:
                time.sleep(1)
        return None

    def _get_current_page_element(self):
        """
        現在表示されているページのページ数が表示されているエレメントを取得する
        @return ページ数が表示されているエレメントがある場合はそのエレメントを、ない場合は None を返す
        """
        try:
            _element = self.browser.driver.find_element_by_xpath("//*[@id='root']/*/div/div[3]/p")
            return _element
        except:
            return None

    def _get_current_page(self):
        """
        現在のページを取得する
        @return 現在表示されているページ
        """
        # print(int(self.current_page_element.html.split('/')[0]))
        return int(self._get_current_page_element().get_attribute('innerHTML').split('/')[0].strip())

    def _next(self):
        """
        次のページに進む
        スペースで次のページにすすめるのでスペースキー固定
        """
        _current_page = self._get_current_page()
        self._press_key(self.next_key)
        if self._get_current_page() < self.pbar.total - 1:
            while self._get_current_page() != _current_page + 1:
                time.sleep(0.1)
