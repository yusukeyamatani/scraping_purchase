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
from settings.amazon import (LOGIN_URL,
                             LOGOUT_URL,
                             PRODUCT_URL,
                             ID,
                             PASSWORD,
                             )


DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))
RETRY_COUNT = 100
IS_DEBUG = True
DRIVER = webdriver.Chrome(DRIVER_PATH)


class CartException(Exception):
    pass


def product_purchase():
    _login()
    DRIVER.get(PRODUCT_URL)
    _add_cart()
    _procedures()
    _purchase()


def _element_exists(m, args):
    try:
        return m(args)
    except NoSuchElementException:
        return None


def _login():
    print(DRIVER.current_url)
    print('ログイン')
    DRIVER.get(LOGIN_URL)
    time.sleep(1) # 画面表を待つ 秒数は適当
    DRIVER.find_element_by_id('ap_email').send_keys(ID)
    DRIVER.find_element_by_id('ap_password').send_keys(PASSWORD)
    DRIVER.find_element_by_id('signInSubmit').click()


def _add_cart():
    print(DRIVER.current_url)

    def _click_cart():

        link = _element_exists(DRIVER.find_element_by_link_text, '1-Clickで注文する場合は、サインインをしてください。')
        if link:
            link.click()

        if not IS_DEBUG:
            one_click_cart = _element_exists(DRIVER.find_element_by_id, 'oneClickBuyButton')
            if one_click_cart:
                one_click_cart.click()
        else:
            one_click_cart = None

        if not one_click_cart:
            add_cart = DRIVER.find_element_by_id('submit.add-to-cart')
            add_cart.click()

    DRIVER.get(PRODUCT_URL)
    for i in range(1, RETRY_COUNT):
        try:
            _click_cart()
        except NoSuchElementException:
            print('reload')
            DRIVER.execute_script('location.reload()')


def _procedures():
    print(DRIVER.current_url)
    print('購入手続き')
    cart_btn = DRIVER.find_element_by_id('hlb-ptc-btn')
    cart_btn.click()


def _purchase():
    print(DRIVER.current_url)
    url = DRIVER.current_url
    if url == 'https://www.amazon.co.jp/gp/buy/spc/handlers/display.html?hasWorkingJavascript=1':
        print('最終決済')
        if not IS_DEBUG:
            # ↓最終決済
            DRIVER.find_element_by_name('placeYourOrder1').click()
        else:
            raise

if __name__ == '__main__':
    DRIVER.set_window_size(1200, 1000)
    url = (DRIVER.current_url)
    print url
    try:
        product_purchase()
    except:
        pass
    finally:
        print('ログアウト')
        DRIVER.get(LOGOUT_URL)
