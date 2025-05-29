from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import csv
import os
from tqdm import tqdm
import traceback
import sys

# ------------- initializing list for search -------------
filename = 'Matrix-Bot/matrix-expired-lists/2024/expired-5-28-24.csv'
# filename = 'Matrix-Bot/matrix-expired-lists/Will Cool Club List (2).csv'


Addresses = []

suffixes = ["DR", "RD", "CT", "ST", "AVE", "CIR", "BLVD", "CIR", "TER", "WAY", "LN"]
def remove_suffix(text):
    for suffix in suffixes:
        if suffix in text:
            text = text.split(suffix)[0]
    return text

with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        og_addy = row[2]
        addy = row[2].split(" ")
        addy = [remove_suffix(part) for part in addy]
        combined_address = " ".join(addy)
        Addresses.append((combined_address.strip(), row))

# ------------- Initialize the Chrome driver ------------- 
driver = webdriver.Chrome()

try:
    # ------------- Navigate to a website -------------
    devUrl = 'https://nys.mlsmatrix.com/Matrix'
    driver.get(devUrl)

    # ------------- log in -------------
    username = 'BIZIERWI'
    password = 'Hockeyislife24$'

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(username)
    time.sleep(random.randint(1, 10))
    password_input.send_keys(password)
    time.sleep(random.randint(1, 10))
    driver.find_element(By.ID, "loginbtn").click()
    time.sleep(random.randint(1, 10))
    driver.find_element(By.CSS_SELECTOR, "a[href*='javascript:history.back()']").click()
    
    # notifcarion shit
    # print("on notifcation")
    # time.sleep(7)
    # WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.ID, "mat-dialog-0"))
    # )

    # Locate the button by its class within the dialog and click it
    # print("on button click shit")
    # button = driver.find_element(By.XPATH, "//mat-dialog-container//button[contains(@class, 'mat-icon-button') and contains(@class, 'mat-button-base')]")
    # button.click()

    # ------------- navigate to matrix -------------
    time.sleep(random.randint(1, 10))
    matrix_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.app-item.ng-star-inserted")))
    matrix_button.click()
    driver.switch_to.window(driver.window_handles[-1]) # switch tabs

    # ------------- that chicks  message --------------



    # ------------- first search -------------

    time.sleep(random.randint(1, 10))
    search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#ctl02_m_ucSpeedBar_m_lnkGo")))
    
    int_search_bar = driver.find_element(By.ID, "ctl02_m_ucSpeedBar_m_tbSpeedBar")
    int_search_bar.send_keys("74 lennox")  # Replace with your desired search query

    search_button.click()

    time.sleep(5)

    status = driver.find_element(By.CSS_SELECTOR, "span.d49m1 span.Status_S")
    status_text = status.text
    print(status_text)
    time.sleep(5)


    # ------------- for loop search -------------
    expireds = []
    not_expireds = []
    errors = []
    upper = len(Addresses)
    lower = 0
    progress_bar = tqdm(total=upper-lower, desc="Progress")
    for q in range(lower, upper):
        #print("entered loop")
        address = Addresses[q][0]
        try: 

            time.sleep(random.randint(3, 7))
            clear_button = driver.find_element(By.CSS_SELECTOR, "span.mtx-speedbar-clear")
            clear_button.click()
            time.sleep(random.randint(1, 2))

            # search
            two_search_bar = driver.find_element(By.ID, "ctl01_m_ucSpeedBar_m_tbSpeedBar")
            two_search_bar.send_keys(address)

            two_search_button = driver.find_element(By.ID, "ctl01_m_ucSpeedBar_m_lnkGo")
            two_search_button.click()
            time.sleep(random.randint(2, 5))

            # trying to catch the error
            if "Sorry, criteria not understood" in driver.page_source:
                print("Error detected in search criteria.")
                errors.append(Addresses[q])
                progress_bar.update(1)
                continue  # Skip to the next iteration

            # get the status
            d49m1_span = driver.find_element(By.CSS_SELECTOR, 'span.d49m1')
            inner_span = d49m1_span.find_element(By.XPATH, './/span')

            # Extract the text of the status
            elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'd49m7')))
            status = None
            if len(elements) >= 3:
                # Get the text from the 3rd matching element
                third_element = elements[2]
                status_text = third_element.text
                status = status_text
                print(f"\n{address}: {status_text}")
                if status == "X":
                    expireds.append(Addresses[q])
                else: 
                    not_expireds.append((Addresses[q], status))
                    
            else:
                raise Exception()
        
        except ValueError as ve:
            # Handle the specific case where the search criteria were not understood.
            print("An error occurred:", str(ve))
            errors.append(Addresses[q])

        except Exception as y:
            print("An error occurred bitch:", str(y))
            errors.append(Addresses[q])

        progress_bar.update(1)
    progress_bar.close()

    # Wait for a key press to keep the browser open
    input("Press Enter to close the browser...")

    # ------------- Outputting: Correct -------------
        # Status: Tuple(info, og address)
    with open("Matrix-Bot/bot-outputs/OUTPUT.csv", 'w', newline='') as outputfile:
        writer = csv.writer(outputfile)
        for status in expireds:
            writer.writerow(status[1])
        
            


    # ------------- Outputting: Other Statuses -------------
        # Status: Tuple(Tuple(info, og address), Status)
    with open("Matrix-Bot/bot-errors-notActives/other-status-OUTPUT.csv", 'w', newline='') as outputfile:
        writer = csv.writer(outputfile)
        status_name = {"A": "ACTIVE", "C": "CONTINUE SHOW", "U": "UNDER CONTRACT", "P": "PENDING SALE", "S": "CLOSED/RENTED",
                    "W": "WITHDRAWN", "T": "TEMP OFF MARKET"}
        for status in not_expireds:
            info = status[0][1]
            info.append(status_name[status[1]])
            writer.writerow(info)
           

    # ------------- Outputting: Errors-------------
        # Status: Tuple(info, og address)
    with open("Matrix-Bot/bot-errors-notActives/errors-OUTPUT.csv", 'w', newline='') as outputfile:
        writer = csv.writer(outputfile)
        for status in errors:
            writer.writerow(status[1])
            


 # ------------- Other Errror Handeling -------------
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    print(f"An error occurred in {fname} at line {line_number}: {e}")
    traceback.print_exc()

finally:
    # Close the browser
    driver.quit()
