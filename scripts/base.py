# -*- coding: utf-8 -*-
"""
http://selenium-python.readthedocs.io/locating-elements.html#locating-by-xpath
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


class Finish(object):
    pass

path = os.path.join(os.path.dirname(__file__), '../')
sys.path.append(path)
driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'driver', 'chromedriver'))


class BasePurchase():
    def __init__(self):
        self.driver = webdriver.Chrome(driver_path)
        self.wait = WebDriverWait(self.driver, 5)

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