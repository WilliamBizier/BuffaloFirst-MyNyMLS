# for selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# other
import time
import random
import csv
import os
from tqdm import tqdm
import traceback
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()
username = os.getenv("USERNAME")
passwd = os.getenv("PASSWORD")


def start_realist():
    driver = webdriver.Chrome()
    devUrl = 'https://nys.mlsmatrix.com/Matrix'
    driver.get(devUrl)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    password_input.send_keys(passwd)
    time.sleep(random.randint(1, 10))
    driver.find_element(By.ID, "loginbtn").click()
    time.sleep(random.randint(1, 10))
    driver.find_element(
        By.CSS_SELECTOR, "a[href*='javascript:history.back()']").click()

    time.sleep(10)

    # navigate to realist -------------------------------

    button = WebDriverWait(driver, 45).until(
        EC.element_to_be_clickable((By.XPATH, '//img[@alt="Realist"]/parent::div'))
    )
    button.click()
    driver.switch_to.window(driver.window_handles[-1])  # switch tabs
    time.sleep(10)
    
    return driver
