#!/usr/bin/env python
# --- coding: utf-8 ---

import os
import re
import subprocess
import sys
from os import path
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from config import Config
from runner import AbstractRunner


def _make_directory(directory):
    if not path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as exception:
            print(f"Directory creation failed ({directory})")
            raise exception


def _get_chrome_version_main(chrome_binary=None):
    exe = chrome_binary or uc.find_chrome_executable()
    if exe:
        try:
            out = subprocess.check_output([exe, '--version'], stderr=subprocess.STDOUT).decode()
            m = re.search(r'(\d+)\.', out)
            if m:
                return int(m.group(1))
        except Exception:
            pass
    return None


def _initialize_driver(config, profile="chrome"):
    # TODO out source (best: configuration, better: class)
    log_name = path.join(config.log_directory, 'driver.log')
    version_main = _get_chrome_version_main(config.chrome_binary)
    if profile == 'chrome':
        chrome_options = uc.ChromeOptions()
        if config.chrome_binary:
            print(config.chrome_binary)
            chrome_options.binary_location = config.chrome_binary
        chrome_options.add_argument('--high-dpi-support=1')
        chrome_options.add_argument('--device-scale-factor=1')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--disable-gpu')

        if config.headless:
            print(f"headless: {config.headless}")
            chrome_options.headless = True
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=960,1222')
        if config.profile_directory:
            print(f"use profile: {config.profile_directory}")
            chrome_options.add_argument(f'--user-data-dir={config.profile_directory}')
        if config.user_agent:
            chrome_options.add_argument(f'--user-agent={config.user_agent}')
        # https://stackoverflow.com/a/59111770
        chrome_options.add_argument('--disable-web-security')
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        # service = Service(options=chrome_options, service_args=["--verbose", f"--log-path={log_name}"])
        driver = uc.Chrome(options=chrome_options, service_args=["--verbose", f"--log-path={log_name}"],
                           version_main=version_main)
        if config.headless:
            driver.set_window_size(960, 1222)
    elif profile == 'chrome_headless':
        chrome_options = uc.ChromeOptions()
        if config.chrome_binary:
            print(config.chrome_binary)
            chrome_options.binary_location = config.chrome_binary
        chrome_options.add_argument('--high-dpi-support=1')
        chrome_options.add_argument('--device-scale-factor=1')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument('--app=https://www.google.com')
        chrome_options.add_argument(f'--user-data-dir={config.profile_directory}')
        chrome_options.add_argument('--window-size=847,1228')

        # TODO headless doesn't work at amazon
        if config.user_agent:
            chrome_options.add_argument(f'--user-agent={config.user_agent}')
        # https://stackoverflow.com/a/59111770
        chrome_options.add_argument('--disable-web-security')
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)

        # service = Service(options=chrome_options, service_args=["--verbose", f"--log-path={log_name}"])
        driver = uc.Chrome(options=chrome_options, service_args=["--verbose", f"--log-path={log_name}"],
                           version_main=version_main)
        driver.set_window_size(847, 1228)
    elif profile == 'chrome_existing':
        chrome_options = ChromeOptions()
        if config.chrome_binary:
            print(config.chrome_binary)
            chrome_options.binary_location = config.chrome_binary
        chrome_options.add_argument('--high-dpi-support=1')
        chrome_options.add_argument('--device-scale-factor=1')
        chrome_options.add_argument('--force-device-scale-factor=1')
        chrome_options.add_argument('--disable-gpu')
        if config.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=960,1222')
        if config.user_agent:
            chrome_options.add_argument(f'--user-agent={config.user_agent}')
        # https://stackoverflow.com/a/59111770
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9014")

        service = Service(options=chrome_options, service_args=["--verbose", f"--log-path={log_name}"])
        driver = webdriver.Chrome(service=service)
    else:
        # service = Service(service_args=["--verbose", f"--log-path={log_name}"])
        driver = uc.Chrome(service_args=["--verbose", f"--log-path={log_name}"], version_main=version_main)
    return driver


def _reset_driver(driver, plugin):
    driver.quit()
    print('recreate driver')
    return _initialize_driver(plugin.config, plugin.sub_config.driver)


def _main():
    """
    $ python k_auto_book.py url [option]
    or
    $ python k_auto_book.py '?python script'
    """

    config = Config()
    _make_directory(config.log_directory)
    _make_directory(config.base_directory)
    driver = _initialize_driver(config)
    profile = config.driver
    print(f'driver: {profile}')

    stripper = re.compile(r'^\s+')

    plugin_classes = AbstractRunner.get_plugins()
    # print(f'{plugin_classes}')
    plugins = [p(m, driver, config) for m, p in plugin_classes]

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
                    if done or (plugin.sub_config.driver and plugin.sub_config.driver != profile):
                        driver = _reset_driver(driver, plugin)
                        profile = plugin.sub_config.driver
                        print(f'driver: {profile}')
                        plugin.reset(driver)
                    plugin.init(url, options)
                    plugin.run()
                    print('', flush=True)
                    done = True
            if not done:
                print('URL is not supported')


if __name__ == '__main__':
    _main()
