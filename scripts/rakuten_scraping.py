# -*- coding: utf-8 -*-
"""
楽天
"""
import os
import sys
import threading
import logging

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


logging.basicConfig(level=logging.INFO,
    filename="rakuten_purchase.log",
    format="%(asctime)s %(levelname)-7s %(message)s")
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)


RETRY_COUNT = 100
THREAD_NUM = 5
IS_DEBUG = True

fin = Finish()
fin.end_flag = False


class RakutenPurchase(BasePurchase):

    def product_purchase(self):
        try:
            self._product_purchase()
        except Exception as e:
            logger.info('thread_{}: {} {}'.format(self.thread_num, e.__class__, e))
        finally:
            self.driver.get(LOGOUT_URL)
            self.driver.close()
            logger.info('thread_{}: logout'.format(self.thread_num))

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
                logger.info('thread_{}: reload'.format(self.thread_num))

        self.driver.find_element_by_class_name('new_addToCart').click()
        logger.info('thread_{}: add_cart'.format(self.thread_num))

    def _procedures(self):
        self.wait.until(EC.presence_of_element_located((By.ID, 'js-cartBtn')))

        cart_btn = self.driver.find_element_by_id('js-cartBtn')
        cart_btn.click()
        logger.info('thread_{}: procedures'.format(self.thread_num))

    def _purchase_login(self):
        self.wait.until(EC.presence_of_element_located((By.NAME, 'u')))

        self.driver.find_element_by_name('u').send_keys(ID)
        self.driver.find_element_by_name('p').send_keys(PASSWORD)
        self.driver.find_element_by_class_name('btn-red').click()
        self.driver.find_element_by_class_name('check-all_off').click()
        logger.info('thread_{}: purchase_login'.format(self.thread_num))

    def _purchase(self):
        if fin.end_flag:
            logger.info('thread_{}: Purchased in other thread'.format(self.thread_num))
            return

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-red')))

        if not IS_DEBUG:
            # ↓最終決済
            self.driver.find_element_by_class_name('btn-red').click()
            logger.info('thread_{}: purchase finish'.format(self.thread_num))
        else:
            logger.info('thread_{}: DEBUG_purchase'.format(self.thread_num))
        fin.end_flag = True
        return

if __name__ == '__main__':
    threads = []
    for i in range(THREAD_NUM):
        rakuten = RakutenPurchase(i)
        t = threading.Thread(target=rakuten.product_purchase)
        threads.append(t)
        t.start()
