#!/usr/bin/env python
# --- coding: utf-8 ---

import json
import os
import re
from os import path
from splinter import Browser
from selenium.webdriver import ChromeOptions
from config import Config
from ebookjapan.runner import Runner as Ebookjapan
from alphapolis.runner import Runner as Alphapolis
from bookwalker.runner import Runner as Bookwalker
from ganganonline.runner import Runner as Ganganonline
from linemanga.runner import Runner as Linemanga


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
        chrome_options.add_argument('high-dpi-support=1')
        chrome_options.add_argument('device-scale-factor=1')
        chrome_options.add_argument('force-device-scale-factor=1')
        _browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name,
            options=chrome_options)
    else:
        _browser = Browser(
            config.driver, headless=config.headless, user_agent=config.user_agent, service_log_path=log_name)
    return _browser


def _main():

    _config = Config(_load_config_data())
    _make_directory(_config.log_directory)
    _browser = _initialize_browser(_config)

    _stripper = re.compile(r'^ +')
    while True:
        try:
            _input_data = _stripper.sub('', input('Input URL > '))
        except EOFError:
            print("\nBye.")
            break
        _inputs_data = _input_data.split(' ', 1)
        _url = _inputs_data[0]
        _options = _inputs_data[1] if 1 < len(_inputs_data) else None
        if _input_data == '':
            continue
        elif _input_data == 'exit':
            print('Bye.')
            break
        elif Ebookjapan.check(_url):
            _runner = Ebookjapan(_browser, _input_data, _config, _options)
        elif Alphapolis.check(_url):
            _runner = Alphapolis(_browser, _input_data, _config, _options)
        elif Bookwalker.check(_url):
            _runner = Bookwalker(_browser, _input_data, _config, _options)
        elif Ganganonline.check(_url):
            _runner = Ganganonline(_browser, _input_data, _config, _options)
        elif Linemanga.check(_url):
            _runner = Linemanga(_browser, _input_data, _config, _options)
        else:
            print('入力されたURLはサポートしていません')
            continue

        _runner.run()

_main()
