# --- coding: utf-8 ---
"""
zebrackcomic の実行クラスモジュール
"""

import time
from config import BasicSubConfig
from runner import AbstractRunner
from zebrackcomic.manager import Manager


class Runner(AbstractRunner):
    """
    zebrack-comic の実行クラス
    https://zebrack-comic.com/title/37/volume/1498/viewer
    """

    def __init__(self, type_, browser, config):
        super().__init__(type_, browser, config, BasicSubConfig)

    def run(self):
        """
        zebrack-comic の実行
        """
        print('Loading page of inputted url (%s)' % self.url)
        self.browser.visit(self.url)

        destination = self.get_output_dir()
        print(f'Output Path : {destination}')

        if self._move_main_page():
            print('Open main page')
        else:
            print('ページの取得に失敗しました')
            return

        manager = Manager(self.browser, self.sub_config, destination)
        result = manager.start()
        if result is not True:
            print(result)

    def _move_main_page(self):
        """
        実際の本のページに移動する
        """
        time.sleep(3)

        # skip dialog
        clazz = "div.karte-c"
        self.browser.driver.execute_script(f'document.querySelector("{clazz}").style.display = "none";')

        elements = self.browser.find_by_css('button.undefined')
        if len(elements) != 0:
            elements.first.click()
            time.sleep(.5)

            # skip dialog 2
            time.sleep(.5)
            try:
                elements = self.browser.driver.find_element_by_xpath("//*[text()='無料で読む']")
                elements.click()
                return True
            except Exception:
                # skip dialog
                clazz = "div[class*='Modal_modalBase']"
                self.browser.driver.execute_script(f'document.querySelector("{clazz}").style.display = "none";')

                # 試し読み
                elements = self.browser.find_by_css('button[class*="MainContents_trialButton"]')
                if len(elements) != 0:
                    elements.first.click()
                    return True

        return False
