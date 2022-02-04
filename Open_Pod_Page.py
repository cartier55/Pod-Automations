from selenium import webdriver
import selenium
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import polling2
import pickle
import time
import creds
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import sys

# Setup webdriver
def Webdriver(headless):
    options=Options()
    if headless:
        options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    PATH = 'C:\Program Files\chromedriver.exe'
    s = Service(PATH)
    driver = webdriver.Chrome(service=s, options=options)
    return driver
    ...

def Selenium_Cookies(driver):
    cookies = {}
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie['name']] = cookie['value']
    filename = 'cookies.pkl'
    pickle.dump( cookies , open(filename,"wb"))
    return f'[+]Cookie File Saved {filename}'

def Cisco_Login(driver, cisco_site):
    try:
        driver.get(cisco_site)      # Open Cisco Site
    except selenium.common.exceptions.WebDriverException:
        sys.exit('[-]Webdriver Error: Try Connecting To VPN')
    driver.implicitly_wait(10)  # Set Global Wait

    # Input Elements Delerations
    userF = driver.find_element(By.ID,'userInput')
    passF = driver.find_element(By.ID,'passwordInput')
    nxt = driver.find_element(By.ID,'login-button')

    userF.send_keys(creds.user)
    nxt.click()
    passF.send_keys(creds.passwd)
    nxt.click()
    time.sleep(3)

    my_element_id = 'something123'
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    duo_push = WebDriverWait(driver, 100,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '#auth_methods > fieldset > div.row-label.push-label > button')))

    # duo_push = driver.find_element(By.CSS_SELECTOR,'#auth_methods > fieldset > div.row-label.push-label > button')
    # duo_push = driver.find_element_by_css_selector("#auth_methods > fieldset > div.row-label.push-label > button")
    duo_push.click()
    # time.sleep(2)
    title = polling2.poll(lambda: driver.title !=
                          'Two-Factor Authentication', step=0.5, timeout=100)
    
    return driver.title


# print(Cisco_Login(driver, "https://autopods.cisco.com/pods/lab/CX%20Labs%20RCDN%20(TS)"))
# print(Cisco_Login(driver, "https://cx-labs.cisco.com/pods/153"))

def Main(driver):
    start = time.time()
    print(Cisco_Login(driver, "https://cx-labs.cisco.com/pods/153"))
    print(Selenium_Cookies(driver))
    print(time.time() - start)
    ...

if __name__ == '__main__':
    Main(Webdriver(True))