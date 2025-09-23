
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

driver=webdriver.Chrome()

driver.get("https://catalog.onliner.by/mobile")

# Собираем все ссылки на объявления с выбранной страницы
def get_all_links_on_page():
    elements = driver.find_elements(By.CLASS_NAME, value='catalog-form__link')
    # elements = driver.find_elements(by=By.CSS_SELECTOR, value="#container > div > div > div > div > div.catalog-content > div.catalog-wrapper > div > div > div.catalog-form__tabs > div > div > div > div > div.catalog-form__filter-part.catalog-form__filter-part_2 > div.catalog-form__offers > div > div:nth-child(1) > div > div > div.catalog-form__offers-part.catalog-form__offers-part_data > div.catalog-form__description.catalog-form__description_primary.catalog-form__description_base-additional.catalog-form__description_font-weight_semibold.catalog-form__description_condensed-other > a")
    # <a href="https://catalog.onliner.by/mobile/xiaomi/redmi15c8256ebk" class="catalog-form__link catalog-form__link_primary-additional catalog-form__link_base-additional catalog-form__link_font-weight_semibold catalog-form__link_nodecor"> Телефон Xiaomi Redmi 15C 4G 8GB/256GB международная версия (черный) </a>
    ads_list = []
    for element in elements:
        ads_list.append(element.get_attribute('href'))
        # print(element.get_attribute('href'), '\n')

    return ads_list

links = get_all_links_on_page()
links