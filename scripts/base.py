# -*- coding: utf-8 -*-
"""
http://selenium-python.readthedocs.io/locating-elements.html#locating-by-xpath
"""

import os
import sys
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


WAIT_SECOND = 10
path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))


class ExclusiveLock(Exception):
    pass


class Lock(object):

    def __init__(self):
        self.thread = None

    def check_lock(self, thread_num, message):
        thread = 'thread_{}'.format(thread_num)
        if self.thread and thread != self.thread:
            raise ExclusiveLock(message)

    def set_lock(self, thread_num):
        self.thread = 'thread_{}'.format(thread_num)


class BasePurchase():
    def __init__(self, thread_num):
        self.driver = webdriver.Chrome(driver_path)
        self.wait = WebDriverWait(self.driver, WAIT_SECOND)
        self.thread_num = thread_num

    def product_purchase(self):
       pass

    def _product_purchase(self):
        pass

    def _cart_element_exists(self):
        pass

    def _add_cart(self):
        pass

    def _procedures(self):
        pass

    def _purchase_login(self):
        pass

    def _purchase(self):
        pass


def get_logger(file_name):
    logging.basicConfig(level=logging.INFO,
    filename=file_name,
    format="%(asctime)s %(levelname)-7s %(message)s")
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)
    return logger