#!/usr/bin/env python
# --- coding: utf-8 ---

import json
import os
import re
import sys
from os import path
from splinter import Browser
from selenium.webdriver import ChromeOptions
from config import Config
from runner import AbstractRunner


def _load_config_data():
    _file = open(
        path.join(path.abspath(path.dirname(__file__)), 'config.json'), 'r')
    _data = json.load(_file)
    _file.close()
    return _data


def _make_directory(directory):
    if not path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as exception:
            print("ディレクトリの作成に失敗しました({0})".format(directory))
            raise


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

        _browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name,
            options=chrome_options)
    else:
        _browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name)
    return _browser


def _reset_browser(browser, config):
    if config.driver == 'chrome':
        print('close chrome driver')
        browser.driver.close()
    print('recreate driver')
    return _initialize_browser(config)


def _main():

    _config = Config(_load_config_data())
    _make_directory(_config.log_directory)
    _browser = _initialize_browser(_config)

    _stripper = re.compile(r'^ +')

    _plugins = AbstractRunner.get_plugins()
    # print(f'{_plugins}')

    _input_data = None

    if len(sys.argv) > 1:
        _input_data = str.join(' ', sys.argv[1:])

    while True:
        if not _input_data:
            try:
                _input_data = _stripper.sub('', input('Input URL > '))
            except EOFError:
                print("\nBye.")
                break

        if _input_data == '':
            continue
        elif _input_data == 'exit':
            print('Bye.')
            break
        elif _input_data[0:1] == '?':
            """
            you can script as python syntax if input strings starts with '?'
            for example:
            
                Input URL > ?[f'https://web-ace.jp/youngaceup/contents/1000053/episode/{n}/' for n in range(1124, 1152)]
            
            this creates urls of range 1124 ~ 1152. and downloads the contents of the url  automatically.
            """
            _urls = eval(_input_data[1:])
            _options = None
        else:
            _inputs_data = _input_data.split(' ', 1)
            _urls = [_inputs_data[0]]
            _options = _inputs_data[1] if 1 < len(_inputs_data) else None

        _input_data = None

        for _url in _urls:
            _done = False
            print(f'url: {_url}')
            for _plugin in _plugins:
                # print(_plugin)
                if _plugin.check(_url):
                    _runner = _plugin()
                    _runner.init(_browser, _url, _config, _options)
                    _runner.run()
                    if _runner.need_reset():
                        _browser = _reset_browser(_browser, _config)
                    _done = True
            if not _done:
                print('入力されたURLはサポートしていません')


_main()
