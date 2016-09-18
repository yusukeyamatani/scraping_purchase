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


class CartException(Exception):
    pass


def _product_purchase():
    _login()
    browser.get(PRODUCT_URL)
    _add_cart()
    _procedures()
    _purchase()


def _login():
    print('ログイン')
    browser.get(LOGIN_URL)
    time.sleep(1) # 画面表を待つ 秒数は適当
    browser.find_element_by_id('ap_email').send_keys(ID)
    browser.find_element_by_id('ap_password').send_keys(PASSWORD)
    browser.find_element_by_id("signInSubmit").click()


def _add_cart():

    def _click_cart():
        try:
            link = browser.find_element_by_link_text('1-Clickで注文する場合は、サインインをしてください。')
            link.click()
            if not IS_DEBUG:
                one_click_cart = browser.find_element_by_id("oneClickBuyButton")
                one_click_cart.click()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            raise CartException

    browser.get(PRODUCT_URL)
    for i in range(1, RETRY_COUNT):
        try:
            try:
                _click_cart()
                break
            except CartException:
                add_cart = browser.find_element_by_id("submit.add-to-cart")
                add_cart.click()
                break
        except NoSuchElementException:
            print('reload')
            browser.execute_script("location.reload()")


def _procedures():
    print('購入手続き')
    cart_btn = browser.find_element_by_id('hlb-ptc-btn')
    cart_btn.click()


def _purchase():
    url = browser.current_url
    if url == 'https://www.amazon.co.jp/gp/buy/spc/handlers/display.html?hasWorkingJavascript=1':
        print('最終決済')
        if not IS_DEBUG:
            # ↓最終決済
            browser.find_element_by_name("placeYourOrder1").click()
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
        pass
        print('ログアウト')
        browser.get(LOGOUT_URL)
