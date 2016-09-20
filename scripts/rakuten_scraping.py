# -*- coding: utf-8 -*-
"""
楽天
"""
import os
import sys
import threading

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from base import BasePurchase, Finish

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
from settings.rakuten import (LOGIN_URL,
                              LOGOUT_URL,
                              PRODUCT_URL,
                              ID,
                              PASSWORD,
                              )
RETRY_COUNT = 100
THREAD_NUM = 5
IS_DEBUG = True

ns = Finish()
ns.end_flag = False

class RakutenPurchase(BasePurchase):

    def product_purchase(self):
        try:
            self._product_purchase()
        except Exception as e:
            print e.__class__
            print e
        finally:
            print 'ログアウト'
            self.driver.get(LOGOUT_URL)
            self.driver.close()

    def _product_purchase(self):
            self.driver.get(PRODUCT_URL)
            self._add_cart()
            self._procedures()
            self._purchase_login()
            self._purchase()

    def _add_cart(self):

        def _cart_element_exists():
            try:
                return WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'new_addToCart')))
            except NoSuchElementException:
                return None

        for i in range(1, RETRY_COUNT):
            if _cart_element_exists():
                break
            else:
                self.driver.execute_script('location.reload()')
                print('reload')

        print '買い物かごに入れる'
        self.driver.find_element_by_class_name('new_addToCart').click()

    def _procedures(self):
        print '購入手続き'

        self.wait.until(EC.presence_of_element_located((By.ID, 'js-cartBtn')))

        cart_btn = self.driver.find_element_by_id('js-cartBtn')
        cart_btn.click()

    def _purchase_login(self):
        print('ログイン')

        self.wait.until(EC.presence_of_element_located((By.NAME, 'u')))

        self.driver.find_element_by_name('u').send_keys(ID)
        self.driver.find_element_by_name('p').send_keys(PASSWORD)
        self.driver.find_element_by_class_name('btn-red').click()
        self.driver.find_element_by_class_name('check-all_off').click()

    def _purchase(self):
        if ns.end_flag:
            print 'not _purchase'
            return

        print '最終決済'
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-red')))

        if not IS_DEBUG:
            # ↓最終決済
            self.driver.find_element_by_class_name('btn-red').click()
        else:
            print 'DEBUG _purchase'
        ns.end_flag = True
        return

if __name__ == '__main__':
    threads = []
    for i in range(THREAD_NUM):
        test = RakutenPurchase()
        t = threading.Thread(target=test.product_purchase)
        threads.append(t)
        t.start()
