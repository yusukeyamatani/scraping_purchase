# -*- coding: utf-8 -*-
"""
http://selenium-python.readthedocs.io/locating-elements.html#locating-by-xpath
"""
import os
import sys
import threading

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from settings.rakuten import (LOGIN_URL,
                              LOGOUT_URL,
                              PRODUCT_URL,
                              ID,
                              PASSWORD,
                              )

driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))
RETRY_COUNT = 100
THREAD_NUM = 5
IS_DEBUG = True


class Finish(object): pass
ns = Finish()
ns.end_flag = False


class RakutenPurchase():
    def __init__(self):
        self.driver = webdriver.Chrome(driver_path)
        self.wait = WebDriverWait(self.driver, 5)

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

    def _cart_element_exists(self):
        try:
            return WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'new_addToCart')))
        except NoSuchElementException:
            return None

    def _add_cart(self):
        for i in range(1, RETRY_COUNT):
            if self._cart_element_exists():
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
