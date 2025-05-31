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

# load site password passed through the env -------------------------------
load_dotenv()
username = os.getenv("USERNAME")
passwd = os.getenv("PASSWORD")


# load in file that you would like to use -------------------------------
filename = 'realist/main.csv'

addresses = []
with open(filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        addresses.append(row)

print(addresses[0])


# helper functions, lists, and dictionaries
buisnessSuffex = ["LLC", "INC", "LTD", "PTY", "COMPANY"]

# this breaks down the table in the search table
def get_table_value(label):
    xpath = f'//tr[td[1][normalize-space()="{label}"]]/td[2]'
    element = WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    return element.text.strip()

# returns boolean
    # True --> the names are the same
    # False --> new name is found
def check_name(searchName, fullName, firstname, lastname):
    searchName = searchName.lower()
    fullName = fullName.lower()
    firstname = firstname.lower()
    lastname = lastname.lower()

    if any(elem in searchName for elem in buisnessSuffex):
            return False

    elif fullName in searchName or lastname in searchName:
        return True

    return False

    # check for new name
    
# returns boolean
    # True --> Date is Past 9 Months
    # False --> Date is earlier than 9 months
def check_date(saleDate):
    if saleDate.lower() == "n/a":
        return True
    
    saleDate = datetime.strptime(saleDate, "%m/%d/%Y")

    # Calculate 9 months ago from today
    nine_months_ago = datetime.today() - timedelta(days=9*30)  # Approximation

    # Check if the sale date is within the last 9 months
    if saleDate > nine_months_ago:
        return False
    return True


# open up MyNyMLS -------------------------------

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


# begin search -------------------------------

lower = 0
upper = 300

progress_bar = tqdm(total=upper-lower, desc="Progress")

errors = []
NewOwners = []
SameOwners = []
TooRecent = []
for index, i in enumerate(addresses[lower:upper]):
    fullName = i[0]
    propFirstName = i[1]
    propLastName = i[2]
    propAddy = i[3]
    propCity = i[4]
    propState = i[5]
    propZip = i[6]
    OwnerName = billAddress = billCityState = billCity = billState = billState = None
    
    try:
        print("\n\nNew Loop Bitch ass--------------------------------------------")
        
        # search the terms
        link = WebDriverWait(driver, 45).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[text()="Search" and contains(@class, "dashboard-style")]'))
        )
        link.click()

        iAddy = propAddy + ", " + propCity
        print(f"Searching")
        print(f"    Address -> {iAddy}")
        print(f"    Name -> {fullName}")

        input_field = WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="123 Main St, City, State Zip"]')))
        input_field.clear()
        input_field.send_keys(iAddy)
        search_button = WebDriverWait(driver, 45).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "search-btn") and text()=" Search "]'))
        )
        
        time.sleep(5)
        search_button.click()
        
        
        # handler for the too many address search
        try:
            close_btn = WebDriverWait(driver, 45).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Close"]'))
            )
            close_btn.click()
            errors.append(i)
            progress_bar.update(1)
            print("Modal closed Moving on to next one")
            print(f"added to errors\n Total -> {len(errors)}")
            continue
        except TimeoutException:
            print("Modal did not appear 1")
            
        except:
            print("Modal did not appear 2")
        
        
        # wait until the table is in the DOM and at least one row is rendered
        table = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "table.data-table.d-flex"))
        )

        # build a quick “label ➜ value” dictionary from the rows
        data = {}
        for row in table.find_elements(By.CSS_SELECTOR, "tr.data-table__row"):
            cells = row.find_elements(By.CSS_SELECTOR, "td.cell")
            if len(cells) >= 2:
                label = cells[0].text.strip()          # e.g. “Owner Name”
                value = cells[1].text.strip()          # e.g. “Bizier Brendan”
                data[label] = value

        # pull out the fields you care about
        OwnerName   = data.get("Owner Name")          # first owner on record
        billAddress     = data.get("Tax Billing Address")
        billCityState  = data.get("Tax Billing City & State", "")
        billZip    = data.get("Tax Billing Zip")

        # split city and state safely
        billCity, billState = ("", "")
        if "," in billCityState:
            city, state = [s.strip() for s in billCityState.split(",", 1)]
        
    
        # time.sleep(10)
        
        # billZip = get_table_value("Tax Billing Zip")
        # OwnerName = get_table_value("Owner Name")
        # billAddress = get_table_value("Tax Billing Address")
        # billCityState = get_table_value("Tax Billing City & State")
        # billCity, billState = billCityState.split(",")
        # billState = billState.strip()
        # billZip = get_table_value("Tax Billing Zip")
        
        # testing
        
        print(f"\nFound Stuff")
        print(f"    Name -> {OwnerName}")
        print(f"    BillAddy -> {billAddress}")
        print(f"    BillCityState -> {billCityState}")
        

        saleDate = WebDriverWait(driver, 45).until(EC.presence_of_element_located((
        By.XPATH,
        '//p[text()="Sale Date"]/following-sibling::span' )))
        
        saleDate = saleDate.text.strip()  # e.g. "12/14/2021"

        # match full name found to current name, and check if its past 9 months
        # same append to SameOwners
        if check_name(OwnerName, fullName, propFirstName, propLastName) and check_date(saleDate):
            
            SameOwners.append(i)
            print("Added: Known")
            print(f"Total -> {len(SameOwners)} ")

        # different send to NewOwner
        elif check_date(saleDate):
            NewOwners.append([OwnerName,
                              propAddy,
                              propCity,
                              propState,
                              propZip,
                              billAddress,
                              billCity,
                              billState,
                              billZip])
            print("Added: New Owner")
            print(f"Total -> {len(NewOwners)}")
            
        # Too Recent
        else: 
            
            TooRecent.append(i)
            print("Added: Too Recent")
            print(f"Total -> {len(TooRecent)} ")
            

    except Exception as e: 
        print(f"\nERROR ERROR ")
        print(e)
        print(f"found part     ->   {OwnerName, billAddress, billCity}")
        print(f"\n Curr string ->  {i}")
        print("\n")
        
        # implement checking and filtering if already got stuff
        
        errors.append(i)
        print("Added: Errors")
        print(f"Total -> {len(errors)} ")
        
        
        

        
    progress_bar.update(1)
progress_bar.close()
    
driver.quit()
    
    
# outputting -------------------------------
# print(NewOwners)
# print(SameOwners)

# New Contacts -> this the only one that is different
with open("realist/NewOwners.csv", "a", newline='') as outputfile:
    writer = csv.writer(outputfile)
    # writer.writerow(["Owner Name", "Property Address", "Property City", "Property State", "Property Zip", "Billing Address", "Billing City", "Billing State", "Billing Zip"])
    for i in NewOwners: 
        writer.writerow(i)
            
# Errors
header1 = ["Index", "Full Name", 
           "First Name", "Last Name", 
           "Property Address", "Property City", 
           "Property State", "Property Zip Code", 
           "Mailing Address", "Mailing City", 
           "Mailing State", "Mailing Zip Code", 
           "Primary Phone", "Phone 1", "Phone 2", 
           "Phone 3", "Email 1"]
with open("realist/errors.csv", "a", newline='') as outputfile:
    writer = csv.writer(outputfile)
    # writer.writerow(header1)
    for i in errors: 
        writer.writerow(i)
        

# Known Contacts
with open("realist/KnownContacts.csv", "a", newline='') as outputfile:
    writer = csv.writer(outputfile)
    # writer.writerow(header1)
    for i in SameOwners: 
        writer.writerow(i)


# Too Recent
with open("realist/TooRecent.csv", "a", newline='') as outputfile:
    writer = csv.writer(outputfile)
    # writer.writerow(header1)
    for i in TooRecent: 
        writer.writerow(i)
