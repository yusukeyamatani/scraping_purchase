# -*- coding: utf-8 -*-
"""
http://selenium-python.readthedocs.io/locating-elements.html#locating-by-xpath
"""
import os
import time
import sys

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from settings.rakuten import (LOGIN_URL,
                              LOGOUT_URL,
                              PRODUCT_URL,
                              ID,
                              PASSWORD,
                              )

DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))
RETRY_COUNT = 100
IS_DEBUG = True


def _product_purchase():
        # browser.get(LOGIN_URL)
        # time.sleep(1) # 画面表を待つ 秒数は適当
        # browser.find_element_by_name('u').send_keys(ID)
        # browser.find_element_by_name('p').send_keys(PASSWORD)
        # browser.find_element_by_class_name("loginButton").click()
        _add_cart()
        _procedures()
        _login()
        _purchase()


def _add_cart():
    browser.get(PRODUCT_URL)
    for i in range(1, RETRY_COUNT):
        try:
            print("買い物かごに入れる")
            add_cart = browser.find_element_by_class_name("new_addToCart")
            break
        except NoSuchElementException:
            browser.execute_script("location.reload()")
            print('reload')
    add_cart.click()


def _procedures():
    print('購入手続き')
    cart_btn = browser.find_element_by_id('js-cartBtn')
    cart_btn.click()


def _login():
    print('ログイン')
    browser.find_element_by_name('u').send_keys(ID)
    browser.find_element_by_name('p').send_keys(PASSWORD)
    browser.find_element_by_class_name("btn-red").click()
    browser.find_element_by_class_name("check-all_off").click()


def _purchase():
    url = browser.current_url
    if url == 'https://books.step.rakuten.co.jp/rms/mall/book/bs/books/ConfirmOrder':
        print('最終決済')
        if not IS_DEBUG:
            # ↓最終決済
            browser.find_element_by_class_name("btn-red").click()
        else:
            raise

if __name__ == '__main__':
    browser = webdriver.Chrome(DRIVER_PATH)
    browser.set_window_size(1200, 1000)
    try:
        _product_purchase()
    except:
        pass
    finally:
        print('ログアウト')
        browser.get(LOGOUT_URL)
