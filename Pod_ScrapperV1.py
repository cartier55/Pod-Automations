from bs4 import BeautifulSoup
import argparse
from pprint import pprint as pp
import re
"""
Collect Access Links and Hostname to Create Device Obj from AutoPod page
Usage:
    Pod_Scrapper_2.0.py {ouptut choice} {file.hmtl}
    Pod_Scrapper_2.0.py {ouptut choice} {file1.hmtl, file2.hmtl, file3.hmtl}
"""
def argInit():
    """
    Init function to parse command line args
    """
    outputs = {'var':scrapeToVar,'con':scrapeToConsole}
    parser = argparse.ArgumentParser(description='Tool to collect AutoPod information from cisco AutoPod page html files')
    parser.add_argument('output', type=str, default='var', choices=['var', 'con'], help='How you want output')
    parser.add_argument("htmlDocs", type=str, help="HTML File To Scrape", action="append" )
    args = parser.parse_args()
    func = outputs[args.output]
    func(args)
    # return args

def scrapeToConsole(files):
    """
    Printing devices objs to console
    """
    for filename in files.htmlDocs:
        devices = []
        html_doc = filename
        devices.append(re.split("\\\|\.", html_doc)[2])
        with open(html_doc) as html:
            soup = BeautifulSoup(html, 'html.parser')
            device_divs = soup.select("div.devices_row")
            for dd in device_divs:
                device = {
                "device_type":"cisco_ios_telnet",
                "host": '',
                "username":"admin",
                "password": "cisco!123", 
                "secret": "cisco!123", 
                "port":0}
                access_link1 = dd.select_one("table.access_links td a")['href']
                device['hostname'] = dd.select_one("td div").string
                device['host'] = re.split("//|:", access_link1)[2]
                device['port'] = re.split("//|:", access_link1)[3]
                device['access'] = access_link1
                devices.append(device)
            devices.append(re.split("\\\|\.", html_doc)[2])
            pp(devices)
            print("##########################################")

def scrapeToVar(files):
    """
    Saving devices objs to variable for output to other programs
    """
    Pods={}
    for filename in files.htmlDocs:
        devices = []
        html_doc = filename
        # print(html_doc)
        pods_key = (re.split("\\\|\.", html_doc)[2])
        # print(pods_key)
        with open(html_doc) as html:
            soup = BeautifulSoup(html, 'html.parser')
            device_divs = soup.select("div.devices_row")
            for dd in device_divs:
                device = {
                "device_type":"cisco_ios_telnet",
                "host": '',
                "username":"admin",
                "password": "cisco!123", 
                "secret": "cisco!123", 
                "port":0}
                access_link1 = dd.select_one("table.access_links td a")['href']
                devices.append(dd.select_one("td div").string)
                device['host'] = re.split("//|:", access_link1)[2]
                device['port'] = re.split("//|:", access_link1)[3]
                device['access'] = access_link1
                devices.append(device)
        Pods[pods_key] = devices
    return Pods


if __name__ == '__main__':
    argInit()
# scrapeToConsole(argInit())
# pod = scrapeToVar(argInit())
# print(pod)
# print(pod['AutoPod-1952'][0])