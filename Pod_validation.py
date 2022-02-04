from functools import reduce
import selenium
from selenium import webdriver
import time
import polling2
import argparse
import re
import itertools
import pandas as pd
import pprint as pp
import pickle
import json

# Initalizing Pod names list
# Will be used to find the correct pod in the legacy pod tool search results
raw_pod_names = list()

# Setup parser to accept pod names txt list
parser = argparse.ArgumentParser(
    description='Tool to find pod numbers by name')
parser.add_argument('pod_names', type=str,
                    help='txt file to list of pod names')
args = parser.parse_args()
raw = r'{}'.format(args.pod_names)

with open(raw, 'r') as r:
    for line in r:
        s_line = line.strip()
        s_line = ' '.join(s_line.split())
        raw_pod_names.append(s_line)

# Building Lookup Names List for searching Legacy Pod tool
lookup_names = [re.split(r'(?<=RCDN)\s', i) for i in raw_pod_names]
search_names = list()
for i in lookup_names:
    if len(i) > 1:
        search_names.append(i[1])
    else:
        search_names.append(i[0])

# Setup webdriver and open autopod richardson page
PATH = 'C:\Program Files\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.get("https://autopods.cisco.com/pods/lab/CX%20Labs%20RCDN%20(TS)")
# driver.add_cookie([{'domain': '.cisco.com', 'httpOnly': True, 'name': 'discovery', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'T1RLAQKrGWUkmkm7_oG9X-vmygD2TJxOURDUbGH46KXOuBzQQEP2SPI8AACAYJs_iqURledaBDYZsItkpQUriYbAiM9GUvCkdhubEjUIuN6V7wq0hTN4QeeUgaWv9gaC3lWeTabHSjicM8Rjh20EgEmwSsOHxJM0oZwg7ZH3nOULg80uCABthyKjuA5AEP_sssr7elf6Qy6XE_nNaBD8L1rFsAnpzPnBGQzkUfg*'}, {'domain': '.cisco.com', 'httpOnly': True, 'name': 'wamsessiontracker', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'T1RLAQLWlK2R0Meg5D1b_eFVfdmZSNdZVRBuE0hVcZJh6ild8cRKNwlMAACAoW9HTbSb10Kbkdoha8LsYZi00l_wCaBZSs8IX7DVKuvfqEKrfw1Ln9bSFAiHtnK2-sSWf4xibABPErIU92_UHcKOMXXTOzjoXvgodt0yXJ9NiHH85fmU9hhEqjF1Kyz2_mdv57OeajKL7hUclPFOVAQLOJ7oH-6oo3_rSCqWlxA*'},
#                   {'domain': 'autopods.cisco.com', 'expiry': 1640122276, 'httpOnly': False, 'name': 'CX/Autopods', 'path': '/', 'secure': True, 'value': 'APHderpIQRKwGr%2B%2Bju%2BDaUj2%2FqzR5KGR1SmHENOYZJ0%3D'}, {'domain': 'autopods.cisco.com', 'httpOnly': False, 'name': 'PHPSESSID', 'path': '/', 'secure': True, 'value': 'eq218fv4bdajha2jlj1pmnjrto'}, {'domain': '.cisco.com', 'httpOnly': False, 'name': 'authorization', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'LoggedIn'}, {'domain': '.cisco.com', 'httpOnly': False, 'name': 'anchorvalue', 'path': '/', 'secure': False, 'value': ''}])
# time.sleep(100)
# print(driver.get_cookies())

# Login Automation
userF = driver.find_element_by_id('userInput')
passF = driver.find_element_by_id('passwordInput')
nxt = driver.find_element_by_id('login-button')

# duo_push = driver.find_element_by_class_name('auth-button-positive')

userF.send_keys("carjames@cisco.com")
nxt.click()
time.sleep(1.5)
passF.send_keys("cJ24549bdedibdedi24549?")
nxt.click()
time.sleep(10)

# Searching for pod name


def Pod_Names(driver, search_names, raw_names):
    PODS = []
    for search_name, raw_name in zip(search_names, raw_names):
        search = polling2.poll(lambda: driver.find_element_by_css_selector(
            "div > input[name='search']"), step=0.5, timeout=100)
        search.send_keys(search_name)

        search_btn = driver.find_element_by_css_selector(
            'span > button.btn-default')
        search_btn.click()
        time.sleep(3)
        pod = {}
        while (bool(pod) == False):
            pods_tool_names = driver.find_elements_by_css_selector(
                "td > a[title = 'View Pod']")

            if len(pods_tool_names) == 0:
                pod = {'Name': raw_name, 'Pod Link': 'empty results'}
                PODS.append(pod)
                break

            for i in range(len(pods_tool_names)):
                if pods_tool_names[i].text == raw_name:
                    pod = {'Name': pods_tool_names[i].text, 'Pod Link': pods_tool_names[i].get_attribute(
                        'href')}
            # pod = {k: v for k, v in pod.items() if k == search_name}
            # pod = reduce(lambda)
            # PODS.update(pods)
            # with open(f"podsVer{i}.json", 'w') as pod:
            #     json.dump(pods, pod)
            # pickle.dump(pods, pod)
            # pod.write(str(pods))
            if len(driver.find_elements_by_css_selector("li[data-page = 'next'] > a")) > 0:
                page_nxt = driver.find_element_by_css_selector(
                    "li[data-page = 'next'] > a")
                page_nxt_class = page_nxt.find_element_by_xpath(
                    '..').get_attribute('class')
                if page_nxt_class == 'footable-page-nav disabled':
                    pod = {'Name': raw_name, 'Pod Link': 'couldnt find'}
                # print(len(pods))
                page_nxt.click()
                time.sleep(3)
            PODS.append(pod)
            # print(pod)
    return PODS


pod_results = Pod_Names(driver, search_names, raw_pod_names)

print(pod_results)
print(len(pod_results))
# pp.pprint(pods_tool_names[0].get_attribute('innerHTML'))


# 33
# for (s_name, r_name) in zip(search_names, raw_pod_names):
#     search = polling2.poll(lambda: driver.find_element_by_css_selector(
#         "div > input[name='search']"), step=0.5, timeout=100)
#     search.send_keys(s_name)

#     search_btn = driver.find_element_by_css_selector(
#         'span > button.btn-default')
#     search_btn.click()
#     time.sleep(3)
#     pods_tool_names = driver.find_elements_by_css_selector(
#         "td > a[title = 'View Pod']")
#     results_len = len(pods_tool_names)
#     i = 0
#     for pod_name in pods_tool_names:
#         i += 1
#         with open("results2.txt", 'a+') as r:
#             if pod_name.text == r_name:
#                 r.write(
#                     f"{pod_name.text}---{pod_name.get_attribute('href')}" + '\n')
#                 break
#             elif i == results_len:
#                 r.write(f"{pod_name.text}---No Link" + '\n')
##################################
# driver.get(pod_name.get_attribute('href'))

# duo_push = polling2.poll(lambda: driver.find_element_by_class_name(
#     'auth-button-positive'), step=0.5, timeout=60)
# duo_push.click()

# driver.get("https://google.com/")
