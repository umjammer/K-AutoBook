#!/usr/bin/env python
# --- coding: utf-8 ---

import os
import re
import sys
from os import path
from splinter import Browser
from selenium.webdriver import ChromeOptions
from config import Config
from runner import AbstractRunner


def _make_directory(directory):
    if not path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as exception:
            print(f"Directory creation failed ({directory})")
            raise exception


def _initialize_browser(config):
    log_name = path.join(config.log_directory, 'ghostdriver.log')
    if config.driver == 'chrome':
        chrome_options = ChromeOptions()
        if config.chrome_binary:
            print(config.chrome_binary)
            chrome_options.binary_location = config.chrome_binary
        chrome_options.add_argument('high-dpi-support=1')
        chrome_options.add_argument('device-scale-factor=1')
        chrome_options.add_argument('force-device-scale-factor=1')
        chrome_options.add_argument('disable-gpu=1')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name,
            options=chrome_options)
    else:
        browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name)
    return browser


def _reset_browser(browser, config):
    if config.driver == 'chrome':
        print('close chrome driver')
        browser.driver.close()
    print('recreate driver')
    return _initialize_browser(config)


def _main():
    """
    $ python k_auto_book.py url [option]
    or
    $ python k_auto_book.py '?python script'
    """

    config = Config()
    _make_directory(config.log_directory)
    _make_directory(config.base_directory)
    browser = _initialize_browser(config)

    stripper = re.compile(r'^\s+')

    plugin_classes = AbstractRunner.get_plugins()
    # print(f'{plugin_classes}')
    plugins = [p(m, browser, config) for m, p in plugin_classes]

    input_data = None

    if len(sys.argv) > 1:
        input_data = str.join(' ', sys.argv[1:])

    while True:
        if not input_data:
            try:
                input_data = stripper.sub('', input('Input URL > '))
            except EOFError:
                print("\nBye.")
                break

        if input_data == '':
            continue
        elif input_data == 'exit':
            print('Bye.')
            break
        elif input_data[0:1] == '?':
            """
            you can script as python syntax if input strings starts with '?'
            for example:
            
                Input URL > ?[f'https://web-ace.jp/youngaceup/contents/1000053/episode/{n}/' for n in range(1124, 1152)]
            
            this creates urls of range 1124 ~ 1152. and downloads the contents of the url automatically.
            """
            urls = eval(input_data[1:])
            options = None
        else:
            inputs_data = input_data.split(' ', 1)
            urls = [inputs_data[0]]
            options = inputs_data[1] if 1 < len(inputs_data) else None

        input_data = None

        for url in urls:
            done = False
            print(f'url: {url}')
            for plugin in plugins:
                # print(plugin)
                if plugin.check(url):
                    plugin.init(url, options)
                    plugin.run()
                    browser = _reset_browser(browser, config)
                    plugin.reset(browser)
                    print('', flush=True)
                    done = True
            if not done:
                print('URL is not supported')


if __name__ == '__main__':
    _main()
