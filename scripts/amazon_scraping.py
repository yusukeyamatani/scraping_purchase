# -*- coding: utf-8 -*-
"""
Amazon
"""
import os
import sys
import threading

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from base import BasePurchase, Finish

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)

from settings.amazon import (LOGIN_URL,
                             LOGOUT_URL,
                             PRODUCT_URL,
                             ID,
                             PASSWORD,
                             )
CART_TYPE = ['one_click', 'normal']

RETRY_COUNT = 100
THREAD_NUM = 5
IS_DEBUG = True


class Finish(object): pass
ns = Finish()
ns.end_flag = False


class CartExist(Exception):
    pass


class AmazonPurchase(BasePurchase):

    def product_purchase(self):
        self._login()
        self.driver.get(PRODUCT_URL)
        self._add_cart()
        self._procedures()
        self._purchase()

    def _login(self):
        print 'ログイン'

        self.driver.get(LOGIN_URL)

        self.wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))

        self.driver.find_element_by_id('ap_email').send_keys(ID)
        self.driver.find_element_by_id('ap_password').send_keys(PASSWORD)
        self.driver.find_element_by_id('signInSubmit').click()

    def _add_cart(self):
        def _one_click_open_link_exists():
            try:
                return EC.presence_of_element_located((By.LINK_TEXT, '1-Clickで注文する場合は、サインインをしてください。'))
            except NoSuchElementException:
                return None

        def _one_click_exists():
            try:
                return EC.presence_of_element_located((By.ID, 'oneClickBuyButton'))
            except NoSuchElementException:
                return None

        def _cart_exists():
            try:
                return self.wait.until(EC.presence_of_element_located((By.ID, 'submit.add-to-cart')))
            except NoSuchElementException:
                return None

        def _click_cart_type():
            link = _one_click_open_link_exists()
            if link:
                self.driver.find_element_by_link_text('1-Clickで注文する場合は、サインインをしてください。').click()

            if _one_click_exists():
                return CART_TYPE[0]

            if _cart_exists:
                return CART_TYPE[1]

            return None

        self.driver.get(PRODUCT_URL)
        for i in range(1, RETRY_COUNT):
            cart_type = _click_cart_type()
            if cart_type:
                break
            else:
                print 'reload'
                self.driver.execute_script('location.reload()')
        print cart_type
        if cart_type == CART_TYPE[0]:
            if IS_DEBUG:
                print 'DEBUG one click'
                cart_type = CART_TYPE[1]
            else:
                self.driver.find_element_by_id('oneClickBuyButton').click()
        print cart_type
        if cart_type == CART_TYPE[1]:
            self.driver.find_element_by_id('submit.add-to-cart').click()

        if not cart_type:
            raise CartExist

    def _procedures(self):
        print '購入手続き'

        self.wait.until(EC.presence_of_element_located((By.ID, 'hlb-ptc-btn')))

        cart_btn = self.driver.find_element_by_id('hlb-ptc-btn')
        cart_btn.click()

    def _purchase(self):
        if ns.end_flag:
            print 'not _purchase'
            return

        print '最終決済'
        self.wait.until(EC.presence_of_element_located((By.NAME, 'placeYourOrder1')))

        if not IS_DEBUG:
            # ↓最終決済
            self.driver.find_element_by_name('placeYourOrder1').click()
        else:
            print 'DEBUG _purchase'
        ns.end_flag = True
        return

if __name__ == '__main__':
    threads = []
    for i in range(THREAD_NUM):
        test = AmazonPurchase()
        t = threading.Thread(target=test.product_purchase)
        threads.append(t)
        t.start()
