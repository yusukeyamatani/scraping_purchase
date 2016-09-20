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
                              PROCEDURES_URL,
                              PURCHESE_LOGIN_URL,
                              PURCHESE_URL,
                              ID,
                              PASSWORD,
                              )

DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))
RETRY_COUNT = 100
IS_DEBUG = True
DRIVER = webdriver.Chrome(DRIVER_PATH)


def _product_purchase():
        # DRIVER.get(LOGIN_URL)
        # time.sleep(1) # 画面表を待つ 秒数は適当
        # DRIVER.find_element_by_name('u').send_keys(ID)
        # DRIVER.find_element_by_name('p').send_keys(PASSWORD)
        # DRIVER.find_element_by_class_name("loginButton").click()
        DRIVER.get(PRODUCT_URL)
        _add_cart()
        _procedures()
        _purchase_login()
        _purchase()


def _element_exists(m, args):
    try:
        return m(args)
    except NoSuchElementException:
        return None


def _add_cart():
    if DRIVER.current_url != PRODUCT_URL:
        return

    for i in range(1, RETRY_COUNT):
        add_cart = _element_exists(DRIVER.find_element_by_class_name, 'new_addToCart')
        if add_cart:
            print('買い物かごに入れる')
            break
        else:
            DRIVER.execute_script('location.reload()')
            print('reload')
    add_cart.click()


def _procedures():
    if DRIVER.current_url != PROCEDURES_URL:
        return

    print('購入手続き')
    cart_btn = DRIVER.find_element_by_id('js-cartBtn')
    cart_btn.click()


def _purchase_login():
    if DRIVER.current_url != PURCHESE_LOGIN_URL:
        return

    print('ログイン')
    DRIVER.find_element_by_name('u').send_keys(ID)
    DRIVER.find_element_by_name('p').send_keys(PASSWORD)
    DRIVER.find_element_by_class_name('btn-red').click()
    DRIVER.find_element_by_class_name('check-all_off').click()


def _purchase():
    if DRIVER.current_url == PURCHESE_URL:
        return

        print('最終決済')
        if not IS_DEBUG:
            # ↓最終決済
            DRIVER.find_element_by_class_name('btn-red').click()
        else:
            raise

if __name__ == '__main__':
    DRIVER = webdriver.Chrome(DRIVER_PATH)
    DRIVER.set_window_size(1200, 1000)
    DRIVER.implicitly_wait(30)
    try:
        _product_purchase()
    except:
        pass
    finally:
        print('ログアウト')
        DRIVER.get(LOGOUT_URL)
        DRIVER.close()
