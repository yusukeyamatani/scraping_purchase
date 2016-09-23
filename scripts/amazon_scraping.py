# -*- coding: utf-8 -*-
"""
Amazon
amazonはカートに入れた際に購入個数が各ブラウザで共有され加算されるので、1台がカート追加に成功した時点で排他Lockする
"""
import os
import sys
import threading
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from base import BasePurchase, Lock, get_logger
from settings.amazon import (LOGIN_URL,
                             LOGOUT_URL,
                             PRODUCT_URL,
                             ID,
                             PASSWORD,
                             )

lock = Lock()

logger = get_logger('amazon_purchase.log')

CART_TYPE = ['one_click', 'normal']
RETRY_COUNT = 100
THREAD_NUM = 5
IS_DEBUG = True


class CartExist(Exception):
    pass


class AmazonPurchase(BasePurchase):

    def product_purchase(self):
        try:
            self._product_purchase()
        except Exception as e:
            logger.info('thread_{}: {} {}'.format(self.thread_num, e.__class__.__name__, e))
        finally:
            self.driver.get(LOGOUT_URL)
            self.driver.close()
            logger.info('thread_{}: logout'.format(self.thread_num))

    def _product_purchase(self):
        self._login()
        self._one_click_on()
        self.driver.get(PRODUCT_URL)
        self._add_cart()
        self._procedures()
        self._purchase()

    def _login(self):
        self.driver.get(LOGIN_URL)
        self.wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))

        self.driver.find_element_by_id('ap_email').send_keys(ID)
        self.driver.find_element_by_id('ap_password').send_keys(PASSWORD)
        self.driver.find_element_by_id('signInSubmit').click()
        logger.info('thread_{}: login'.format(self.thread_num))

    def _one_click_on(self):
        self.driver.get('https://www.amazon.co.jp/gp/css/account/address/view.html')
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'myab-1click-button')))

        self.driver.find_element_by_class_name('myab-1click-button').click()
        logger.info('thread_{}: one_click ON'.format(self.thread_num))

    def _add_cart(self):

        def _one_click_exists():
            try:
                return self.driver.find_element_by_id('oneClickBuyButton')
            except NoSuchElementException:
                return None

        def _cart_exists():
            try:
                return self.driver.find_element_by_id('submit.add-to-cart')
            except NoSuchElementException:
                return None

        def _click_cart_type():

            if _one_click_exists():
                return CART_TYPE[0]

            if _cart_exists():
                return CART_TYPE[1]

            return None

        self.driver.get(PRODUCT_URL)
        for i in range(1, RETRY_COUNT):
            cart_type = _click_cart_type()
            logger.info('thread_{}: cart_type {}'.format(self.thread_num, cart_type))

            if cart_type:
                break
            else:
                self.driver.execute_script('location.reload()')
                logger.info('thread_{}: reload'.format(self.thread_num))

        if cart_type == CART_TYPE[0]:
            if IS_DEBUG:
                logger.info('thread_{}: DEBUG one click -> normal'.format(self.thread_num))
                cart_type = CART_TYPE[1]
            else:
                lock.check_lock(self.thread_num, '_add_cart:{}'.format(cart_type))

                self.driver.find_element_by_id('oneClickBuyButton').click()
                logger.info('thread_{}: one click'.format(self.thread_num))

        if cart_type == CART_TYPE[1]:
            lock.check_lock(self.thread_num, '_add_cart:{}'.format(cart_type))

            self.driver.find_element_by_id('submit.add-to-cart').click()
            logger.info('thread_{}: add_cart'.format(self.thread_num))

        if not cart_type:
            raise CartExist

    def _procedures(self):
        lock.check_lock(self.thread_num, '_procedures')
        lock.set_lock(self.thread_num)

        self.wait.until(EC.presence_of_element_located((By.ID, 'hlb-ptc-btn')))

        cart_btn = self.driver.find_element_by_id('hlb-ptc-btn')
        cart_btn.click()
        logger.info('thread_{}: procedures'.format(self.thread_num))

    def _purchase(self):
        lock.check_lock(self.thread_num, '_purchase')

        self.wait.until(EC.presence_of_element_located((By.NAME, 'placeYourOrder1')))
        if not IS_DEBUG:
            # ↓最終決済
            self.driver.find_element_by_name('placeYourOrder1').click()
            logger.info('thread_{}: purchase finish'.format(self.thread_num))
        else:
            self.driver.find_element_by_name('placeYourOrder1')
            logger.info('thread_{}: DEBUG_purchase'.format(self.thread_num))

        lock.set_lock(self.thread_num)

if __name__ == '__main__':
    threads = []
    for i in range(THREAD_NUM):
        amazon = AmazonPurchase(i)
        t = threading.Thread(target=amazon.product_purchase)
        threads.append(t)
        t.start()
