from os import device_encoding, name
import selenium
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from time import sleep
import time
from selenium.webdriver.common.keys import Keys
import colorama
from colorama import Fore, Back, Style
import re
import argparse
from types import SimpleNamespace
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


# url = "https://calo-new.cisco.com/#/tools/start_here"
creds = {
    "username":"Carjames",
    "password":"cJ24549bdedibdedi24549?"
}
creds = SimpleNamespace(**creds)

check = 0 
TEST_DEVICE = "02B3ABE"
PATH = "C:\Program Files (x86)\chromedriver.exe"
OT6 = "https://calo-new.cisco.com/#/tools/start_here"
GOOGLE = "https://www.google.com/"
colorama.init(autoreset=True)

parser = argparse.ArgumentParser(description='''
Console Mapper.py

Automates cisco OT6 device mapping process
''')
parser.add_argument('file', type=str, help="Formated file of itms#, location, and port#")
parser.add_argument('-C', dest='Chk', default=False, action='store_true', help="Flag to check COMM ports against file")
args = parser.parse_args()
start = time.time()
# args = SimpleNamespace(**{'file':'test.txt', 'Chk':False}) #For Testing
driver = webdriver.Chrome(PATH)
wait  = WebDriverWait(driver, 20)
comm_wait  = WebDriverWait(driver, 5)


def main():
    """
    1)Read in ConsoleMap.txt files with ITMS#, Location Info, Port#
    2)Start console mapping process for every device in ConsoleMap.txt by sending varibale obj to login()
    3)Check for -C flag to only check console ports
    """

    # Reading Formted File With Devices and Console Information
    filename = args.file
    with open(filename, 'r+') as f:
        file = f.read()

    # Creating regexs for parsing formated file for information
    location_regex = re.compile(r'(LAB:)(.*)', re.I)
    itms_regex = re.compile(r'[a-z0-9]{7}', re.I)
    port_regex = re.compile(r'\[\d\d\]|\[\d\]')
    comm_regex = re.compile(r'4300|2900|2800', re.I)

    # Temp holder for device information
    dev_pod = []
    # dev_pod = SimpleNamespace(**dev_pod)

    # Parsing Formated File for information
    dev_pod_devices = re.findall(itms_regex, file)
    ports = re.findall(port_regex, file)
    lab = re.search(location_regex, file)
    comm = re.search(comm_regex, file)
    for i, port in enumerate(ports):
        ports[i] = port[1:-1]
    
    # Organizing device obj
    for d, p in zip(dev_pod_devices, ports):
        dev_pod.append({'loco':lab.group(2), 'device':d, 'port':p, 'comm':comm.group()})

    devices = [] # Final holder for devices objs
    # Final formating of devices information into dev obj
    for p in dev_pod:
        # print(p)
        dev = commAddy(p)
        devices.append(dev)

    login()

    #  Main loop
    for dev in devices:
        search(dev)
        ...
    end = time.time()
    driver.quit()
    print(f'{Fore.MAGENTA}{Style.BRIGHT}{end - start}')
    ...

def commAddy(dev_pod_obj):
    dev_pod_obj = SimpleNamespace(**dev_pod_obj)

    if dev_pod_obj.comm == '4300':
        if len(dev_pod_obj.port) == 2 or dev_pod_obj.port == '9':
            dev_pod_obj.port = f'20{int(dev_pod_obj.port) + 1}' 
        elif len(dev_pod_obj.port) == 1:
            dev_pod_obj.port = f'200{int(dev_pod_obj.port) + 1}' 
    elif dev_pod_obj.comm == '2900':
        if len(dev_pod_obj.port) == 2 or dev_pod_obj.port == '9':
            dev_pod_obj.port = f'20{int(dev_pod_obj.port) + 2}' 
        elif len(dev_pod_obj.port) == 1:
            dev_pod_obj.port = f'200{int(dev_pod_obj.port) + 2}' 
    elif dev_pod_obj.comm == '2800':
        if len(dev_pod_obj.port) == 2 or dev_pod_obj.port == '9':
            dev_pod_obj.port = f'20{int(dev_pod_obj.port) + 65}' 
        elif len(dev_pod_obj.port) == 1:
            dev_pod_obj.port = f'200{int(dev_pod_obj.port) + 65}' 
    addy = 'telnet://F' + dev_pod_obj.loco + '-COMM:' + dev_pod_obj.port
    dev = {
        'loco':addy, 
        'device':dev_pod_obj.device,
        'port': dev_pod_obj.port
    }
    return dev

def login():
    """
    Login to calo OT6 page
    
    driver = webdriver.Firefox(PATH)
    driver = webdriver.Edge(PATH)
    """
    driver.get(OT6)
    print(driver.title)
    # sleep(3)
    userb = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    passb = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    userb.send_keys(creds.username)
    passb.send_keys(creds.password)
    driver.find_element_by_css_selector('div.clearfix > button.width-35').click()
    return

def search(dev):
    """
    Select Quick Find serach bar enter first device itms# and search
    """
    dev = SimpleNamespace(**dev)
    # sleep(2)
    # driver.implicitly_wait(30)
    quick_search = wait.until(EC.presence_of_element_located((By.ID, 'nav-search-input')))
    ActionChains(driver).move_to_element(quick_search).click(quick_search).perform()
    try:
        quick_search.send_keys(dev.device)
        quick_search.send_keys(Keys.RETURN)
    except:
        try:
            sleep(3)
            quick_search.send_keys(dev.device)
            quick_search.send_keys(Keys.RETURN)
        except:
            print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Search Error')
            return
    curComm(dev)
    return

def curComm(dev):
    """
    Find the current telnet console address
    """
    sleep(3)
    
    try:
        telnet_comm = comm_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href*="telnet"]'))).text
    except:
        try:
            print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Error Finding Comm Trying Again... ')
            telnet_comm = comm_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href*="telnet"]'))).text
        except:
            print(f"{Fore.RED}{Style.BRIGHT}[-]Error {dev.device} No Active Console")
            if not args.Chk:
                blocked = accessMeth()
                if blocked:
                    print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Console Mapping Locked')
                    return
                formEntry(dev)
                return
            else:
                return
    else:
        if telnet_comm == dev.loco:
            print(f'{Fore.GREEN}{Style.BRIGHT}[+]{dev.device} Console Match')
            if not args.Chk:
                blocked = accessMeth()
                if blocked:
                    print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Console Mapping Locked')
                    return
                formEntry(dev)
                return
            else:
                return
        else:
            print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Console Discrepancy')
            if not args.Chk:
                blocked = accessMeth()
                if blocked:
                    print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Console Mapping Locked')
                    return
                formEntry(dev)
                return
            else:
                return
    

def accessMeth():
    """
    Go to access methods page to change console port
    """
    url = re.split('/(?=[a-zA-z0-9#])',driver.current_url ) #Split the url so the slashs are removed
    url[-2] = 'access_methods'
    driver.get('/'.join(url))
    try:
        driver.find_element_by_css_selector('div[id*="fatal_error_message"]')
    except:
        return
    else:
        return 1

def formEntry(dev):
    """
    Find form entry 1 for console access port inside of form_area table body
    """
    # sleep(5)
    form_entry_1 = ''
    form_entries = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody[id$="form_area"] > tr[id*="form_entry"]'))) #Find the tr entries for the form_area table 
    # Select first form entry or new form entry
    for i in form_entries:
        try:
            if i.get_attribute('id') == "1_form_entry":
                form_entry_1 = i
                break
            if i.get_attribute('id') == "New_form_entry":
                form_entry_1 = i
                break
        except:
            print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Error Form Entry')

    try:
        # Find td with console addresse inside form entry 1
        form_data = form_entry_1.find_elements_by_css_selector('td > input.form-control')

        #Find Current Console addresse
        try:
            cur_console = form_data[-1].get_attribute('value')
            if cur_console == '':
                raise Exception
            print(f'{Fore.GREEN}{Style.BRIGHT}[+]{cur_console} Current Console') #Prints the current console addresse
        except:
            print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} No Console')
        
        # Add name to console entry 
        form_data[0].clear()
        form_data[0].send_keys('Console')

        # Change protocol dropdown element to console
        proto_dropdown = Select(driver.find_element_by_css_selector('select[id*="connection_protocol"]'))
        proto_dropdown.select_by_visible_text('Console')
        # proto_dropdown.select_by_visible_text('SSH')
        
        #Change the console address
        form_data[-1].clear() #Clears the console address form td
        form_data[-1].send_keys(dev.loco) #Enters data for the console addresse

        #Save Console Addresse Changes
        submit_console = driver.find_element_by_css_selector('center > button.btn-white')
        submit_console.click()
        print(f"{Fore.BLUE}{Style.BRIGHT}[+]{dev.device} Console Saved")
    except:
        print(f'{Fore.RED}{Style.BRIGHT}[-]{dev.device} Form Error')

main()