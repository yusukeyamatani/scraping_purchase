# -*- coding: utf-8 -*-
"""
楽天
楽天はブラウザ毎に情報が管理されるため、購入直前時のみ排他Lockする
"""
import threading
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from base import BasePurchase, Lock, get_logger
from settings.rakuten import (LOGOUT_URL,
                              PRODUCT_URL,
                              ID,
                              PASSWORD,
                              )

lock = Lock()

logger = get_logger('rakuten_purchase.log')

RETRY_COUNT = 1000
THREAD_NUM = 5
IS_DEBUG = True


class RakutenPurchase(BasePurchase):
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
        self.driver.get(PRODUCT_URL)
        self._add_cart()
        self._procedures()
        self._purchase_login()
        self._purchase()

    def _add_cart(self):

        def _cart_element_exists():
            try:
                return self.driver.find_element_by_class_name('new_addToCart')
            except NoSuchElementException:
                return None

        for i in range(1, RETRY_COUNT):
            if _cart_element_exists():
                break
            else:
                self.driver.execute_script('location.reload()')
                logger.info('thread_{}: reload'.format(self.thread_num))
                time.sleep(0.3)

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
        lock.check_lock(self.thread_num, '_purchase')

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-red')))

        if not IS_DEBUG:
            # ↓最終決済
            self.driver.find_element_by_class_name('btn-red').click()
            logger.info('thread_{}: purchase finish'.format(self.thread_num))
        else:
            logger.info('thread_{}: DEBUG_purchase'.format(self.thread_num))

        lock.set_lock(self.thread_num)

if __name__ == '__main__':
    threads = []
    for i in range(THREAD_NUM):
        rakuten = RakutenPurchase(i)
        t = threading.Thread(target=rakuten.product_purchase)
        threads.append(t)
        t.start()
