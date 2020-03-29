# --- coding: utf-8 ---
"""
web-ace の操作を行うためのクラスモジュール
"""

from manager import AbstractManager, scroll_down


class Manager(AbstractManager):
    """
    web-ace の操作を行うためのクラス
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        web-ace の操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        super().__init__(browser, config, directory, prefix)

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

        scroll_down(self.browser.driver, self._sleep_time)
        print('scroll down to the bottom of the page.')

        imgs = self.browser.find_by_css("img.viewerFixedImage")
        self._set_total(len(imgs))

        session = self._get_session()

        for _count, img in enumerate(imgs):

            _url = img._element.get_attribute('src')
            # print(_url)

            self._save_image_of_bytes(_count, session.get(_url).content)

            self.pbar.update(1)
            self._sleep()

        return True
