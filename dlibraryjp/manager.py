# --- coding: utf-8 ---
"""
d-library.jp
"""

import base64
import hashlib
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

from manager import AbstractManager


class Manager(AbstractManager):
    """
    Manages 'd-library.jp' scraping.
    """

    PAGE_CHANGE_TIMEOUT = 10
    """
    max seconds to wait for the canvas to change after turning a page.
    """

    MAX_RETRY = 3
    """
    max retries of turning a page when the canvas doesn't change.
    """

    def __init__(self, driver, config=None, directory='./', prefix=''):
        """
        Creates 'd-library.jp' manager.
        @param driver selenium instance
        """
        super().__init__(driver, config, directory, prefix)

        self.pbar = tqdm(bar_format='{n_fmt}/{total_fmt}')

        self.next_key = Keys.ARROW_LEFT
        """
        The key for next page.
        """

    def start(self, url=None):
        """
        Starts scraping.
        @return an error message or True when succeeded.
        """
        self.driver.set_window_size(960, 1280)

        self._wait()

        self._sleep(3)

        self._switch_to_viewer()

        # wait for the first page rendered
        data = self._wait_for_canvas_change(None)
        if data is None:
            return 'Failed to get the first page'

        count = 0
        last_hash = None
        while True:
            hash_ = self._hash(data)
            if hash_ != last_hash:
                self._save_data(count, data)
                self.pbar.update(1)
                count += 1
                last_hash = hash_

            if self._is_last_page():
                break

            data = self._next(last_hash)
            if data is None:
                if self._is_last_page():
                    break
                return f'Page did not advance after page {count}, stopped'

            self._sleep()
        return True

    def _switch_to_viewer(self):
        """
        Switches into the viewer iframe (again).
        """
        self.driver.switch_to.default_content()
        iframe = self.driver.find_element(By.ID, 'binb')
        self.driver.switch_to.frame(iframe)

    def _get_canvas_data(self):
        """
        @return base64 image data of the current canvas, or None
        """
        try:
            img = self.driver.find_element(By.CSS_SELECTOR, '#main_canvas2')
            data = self.driver.execute_script(
                "var c = arguments[0];"
                "if (!c || c.width === 0 || c.height === 0) return null;"
                "return c.toDataURL('image/%s');" % self._format, img)
        except Exception:
            # lost iframe context, stale element etc.
            try:
                self._switch_to_viewer()
            except Exception:
                pass
            return None
        if not data or ',' not in data:
            return None
        return data.split(',', 1)[1]

    @staticmethod
    def _hash(data):
        return hashlib.md5(data.encode('ascii')).hexdigest()

    def _save_data(self, count, data):
        name = '%s%s%03d%s' % (self.directory, self.prefix, count, self._extension)
        with open(name, 'wb') as f:
            f.write(base64.b64decode(data))

    def _wait_for_canvas_change(self, last_hash):
        """
        Waits until the canvas shows an image different from last_hash.
        @return new image data, or None on timeout
        """
        end = time.time() + self.PAGE_CHANGE_TIMEOUT
        while time.time() < end:
            data = self._get_canvas_data()
            if data is not None and self._hash(data) != last_hash:
                # wait a moment and re-read to avoid capturing a half drawn canvas
                self._sleep(0.3)
                data2 = self._get_canvas_data()
                if data2 is not None and data2 == data:
                    return data
                continue
            if self._is_last_page():
                return None
            time.sleep(0.3)
        return None

    def _next(self, last_hash):
        """
        Turns to the next page.
        @return new image data, or None when the page didn't change
        """
        for i in range(self.MAX_RETRY):
            self._turn_page(i)
            data = self._wait_for_canvas_change(last_hash)
            if data is not None:
                return data
            if self._is_last_page():
                return None
        return None

    def _turn_page(self, attempt):
        """
        Sends the "next page" action, using a different method for each attempt.
        """
        try:
            if attempt == 0:
                # press *and release*, otherwise following presses become key repeats
                ActionChains(self.driver).key_down(self.next_key).key_up(self.next_key).perform()
            elif attempt == 1:
                # focus may have been lost, re-enter the iframe and send to body
                self._switch_to_viewer()
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(self.next_key)
            else:
                # dispatch the key event directly
                self.driver.execute_script("""
                    ['keydown', 'keyup'].forEach(function(t) {
                        var e = new KeyboardEvent(t, {key: 'ArrowLeft', code: 'ArrowLeft',
                            keyCode: 37, which: 37, bubbles: true, cancelable: true});
                        (document.activeElement || document.body).dispatchEvent(e);
                        document.dispatchEvent(e);
                    });
                """)
        except Exception as e:
            print(f'turn page failed ({attempt}): {e}')

    def _is_last_page(self):
        """
        @return True when the last page dialog is shown.
        """
        try:
            return len(self.driver.find_elements(By.ID, 'lastPageFrame')) > 0
        except Exception:
            return False
