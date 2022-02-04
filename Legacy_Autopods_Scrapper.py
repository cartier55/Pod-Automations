from ntpath import join
import requests
import json
import pprint as pp
import pandas as pd
from types import SimpleNamespace as sn
import re
import argparse
import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from tqdm import tqdm

'''
This script will request the backend o
'''

url = "https://autopods.cisco.com/scripts/updates.php"


def Main():
    autopods = []
    access_links = []
    credentials = []
    parser = argparse.ArgumentParser(
        description='Tool to request legacy pod tool backend for pod infomation')
    parser.add_argument('pod_links', type=str,
                        help='txt file to list of pod links')
    args = parser.parse_args()
    start_time = time.time()
    pod_numbers = Read_AutoPods_Legacy(args.pod_links) #List of pod ID numbers
    pod_data = partial(Request_Pods, url = url)
    with ProcessPoolExecutor() as executor:
        data = list(tqdm(executor.map(pod_data, pod_numbers), total=len(pod_numbers)))
    for d in data:
        (pod, access, creds) = Parse_Autopods(d)
        autopods.append(pod[0])
        try:
            access_links.extend(access)
            credentials.extend(creds)
        except IndexError:
            print(f'No devices/access/creds{pod[0]["pod"]}')

    
    # for pod_num in pod_numbers:
    #     data = Request_Pods(pod_num, url)
    #     (pod, access, creds) = Parse_Autopods(data)
    #     autopods.append(pod[0])
    #     try:
    #         access_links.extend(access)
    #         credentials.extend(creds)
    #     except IndexError:
    #         print(f'No devices/access/creds{pod[0]["pod"]}')
 
    Data_Format(autopods, access_links, credentials)
    print(start_time-time.time())


    ...

def Request_Pods(pod_number, url):
    payload = f"handler=pod&action=get_pod_info&pod_id={pod_number}"
    headers = {
    'authority': 'autopods.cisco.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://autopods.cisco.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'omnitool_ticket_prod=C7BC227213CDF8AA_1248023; anchorvalue=; cdcUniqueKey=69d317cgeb7e4; CP_GUTC=173.37.111.75.1639082642464697; OptanonAlertBoxClosed=2021-12-13T21:43:08.489Z; devnet_language=en; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Dec+18+2021+12%3A32%3A31+GMT-0500+(Eastern+Standard+Time)&version=6.26.0&isIABGlobal=false&hosts=&consentId=03e57c55-c5a2-4016-a070-580a7eb7d0af&interactionCount=1&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&geolocation=US%3BNC&AwaitingReconsent=false; authorization=LoggedIn; CX/Autopods=CDlWtgSi64J3FmX3v%2FHVRU%2BTKzBY3Eg%2BzA5do7QiXCY%3D; PHPSESSID=h1g2vgbjtue68dp7ut1kqcrqkv; wamsessiontracker=T1RLAQJz2JLOa5sAH8pBsskEa9v50XzHJBCTwiKJY5gXblppsAe85K3DAACACG-twWTg57xVupScvtE5u0ZksMW-zOkVwbjvawZL9vKm1TxNmuQ1WJbXz-fUTTz8GKtnzXtReoVNDoPQxGyvtRZr_Y28HQCti-Szvb-LVC2gulX5biUfPWkHUcVBL0hlLiyekviWDyYnXgMRaL0ZUG94jMEj_BHmWVekp4df8_k*; discovery=T1RLAQKI9YFUOcnXtPETmnlJzTaJxmQgOhAA_ibbPxR_rIZeVAqVhZdZAACA4SIq5Ci-FD19xC0528KpKLr6ZnbQZBI-m4HPrLzhkBkvbF5l13OF9-tcmq14qSLxJe2flxONlesSfxJV1ZOk_yQ8DEGtFeCwOe_HnyWbnkcX0sqeHaHsHTo1CEP108I4J6aHRlfBhDO5tIWAmnhdbwjAs_9XsOXVhJML0GNS-Oo*'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
 
    return data


def Read_AutoPods_Legacy(filename):
    pod_link_regex = re.compile(r'https://autopods.cisco.com/pod/(\d{1,4})')
    with open(filename, 'r+') as f:
        pod_file = f.read()
    pod_links = re.findall(pod_link_regex, pod_file)
    
    return pod_links
    
        

def Parse_Autopods(data):
    # access_data = []
    pod_data = sn(**data['reply'])
    devices_data = [sn(**i) for i in pod_data.devices]
    if devices_data:
        access_data = []
        credentials_data = []    
        for device in devices_data: 
            accesses = [sn(**i) for i in device.accesses]
            creds_data = [sn(**i) for i in device.creds]
            access_data.extend(accesses)
            credentials_data.extend(creds_data)
    else:
        pod_info = [
        {
            "pod":pod_data.uid,
            'name':pod_data.name,
            'doc':pod_data.doc,
            'site':pod_data.site,
            'total_devices':len(pod_data.devices),
            'devices':[]
            }
    ]
        return(pod_info, [], [])

    pod_info = [
        {
            "pod":pod_data.uid,
            'name':pod_data.name,
            'docs':pod_data.doc,
            'site':pod_data.site,
            'total_devices':len(pod_data.devices),
            # 'devices':list(set([]))
            'devices':[]
            }
    ]


    for i in devices_data:
        pod_info[0]['devices'].append({
            'id':i.uid,
            'name':i.name,
            'location':i.location.split('-')[0],
            'ITM':i.itm,
            'platform':i.platform,
            'status':i.status.split('.')[0],
            'last_image':i.last_loaded_image,
            'serial':i.serial_number,
            'pid':i.pid,
            'pod':i.pod_id,
            'access_links':len(i.accesses)
            })

    try:
        access_links = []
        for i in access_data:
            access_links.append({
                'pod':pod_data.uid,
                'device_itm': next(filter(lambda ele: ele['id'] == i.device_id, pod_info[0]['devices']), None)['ITM'],
                'device_name': next(filter(lambda ele: ele['id'] == i.device_id, pod_info[0]['devices']), None)['name'],
                'creds_id':i.cred_chain_id,
                'hostname':i.hostname.lower(),
                'protocol':i.protocol,
                'port':i.port,
            })
        
            
        creds = []
        for i in credentials_data:
            creds.append({
                'pod':pod_data.uid,
                'creds_id':i.cred_chain_id,
                'user':i.username,
                'pass':i.password,
                'enable':i.enable_password,
                'device_itm': next(filter(lambda ele: ele['creds_id'] == i.cred_chain_id, access_links), None)['device_itm'],
                'device_name':next(filter(lambda ele: ele['creds_id'] == i.cred_chain_id, access_links), None)['device_name']
            })
    
    except UnboundLocalError:
        print(pod_data.uid)
    # telnet_mask = pd.DataFrame(access_links)['protocol'] == 'telnet'
    print('Console Links from parse func')
    # print(pd.DataFrame(access_links)[telnet_mask].reset_index())
    return (pod_info, access_links, creds)

def Data_Format(autopods, access_links, creds):
    # pd.set_option("display.max_columns", 1000, "display.width", 1000)
    pd.set_option("display.max_columns", 1000, "display.max_rows", 1000)
    pods_info = []
    devices_info = []
    for i in autopods:
        pod = {k: i[k] for k in i.keys() if k != 'devices'}
        pods_info.append(pod)
        for device in i['devices']:
            devices_info.append(device)
        
    pods_info_df = pd.DataFrame(pods_info)
    pods_devices_df = pd.DataFrame(devices_info)
    pods_links_df = pd.DataFrame(access_links)
    pods_creds_df = pd.DataFrame(creds)
    
    flex_pool_mask = pods_info_df['name'].str.contains('Flexpool|flexpool')
    # flex_pool_devices_mask = pods_console_df['pod']
    telnet_mask = pods_links_df['protocol'] == 'telnet'
    # access_mask = pods_links_df['protocol'] == 'telnet'

    pods_console_df = pd.merge(pods_links_df[telnet_mask], pods_creds_df)
    # pods_console_df_test = pd.merge(pods_links_df[telnet_mask], pods_creds_df, how='left')
    pods_access_df = pd.merge(pods_links_df[~telnet_mask], pods_creds_df) #Possible cause of missing rows

# CXLT DF Matching
    del pods_console_df['creds_id']
    del pods_access_df['creds_id']
    pods_info_df.rename(columns={'docs':'doc'})
    pods_access_df.rename(columns={'hostname':'ip'}, inplace=True)
    pods_devices_df = pods_devices_df[['pod', 'ITM', 'name', 'location', 'platform', 'status', 'last_image', 'serial', 'pid', 'access_links']]
    # print(pods_info_df[flex_pool_mask])
    # # print('##################################################################')
    # print('##################################################################')

    # print('Pod Devices')
    # print(pods_devices_df)
    # print('##################################################################')
    if 1>2:
        print('Console Links from data format func \n with duplicates')
        print(pods_console_df)
        print('##################################################################')
        print(pods_console_df_test)
        print('Console Links duplicates')
        pods_console_df_test.drop_duplicates(subset='device_itm', inplace=True)
        print(pods_console_df)
        print('##################################################################')
        print(pods_console_df_test)
        print('Creds df that is merged with access df')
        print(pods_creds_df)
    # # print('##################################################################')   
    # print('Other Access Links')
    flexpools = ['1935','1936','1937','1944','1946','1988','1993','2023','2366','2447']
    # flexpools = [str(i) for i in flexpools]
#Removing All Flexpods From Fin DF Of Access Links and Console Links
    pods_access_df = pods_access_df[pods_access_df.pod.isin(flexpools) == False]
    pods_console_df = pods_console_df[pods_console_df.pod.isin(flexpools) == False]

    pods_console_df.drop_duplicates(subset=['pod','device_itm','hostname','protocol','port'], inplace=True)
    pods_access_df.drop_duplicates(subset=['pod','device_itm','ip','protocol','port'], inplace=True)
    # print(pods_access_df)
    # print('##################################################################')

    #spreadsheet creation
    # pods_info_df.to_excel('Legacy_Pods.xlsx')
    # pods_devices_df.to_excel('Legacy_Pods_Devices.xlsx')
    pods_console_df.to_excel('Legacy_Console_Mappings_no_flex_v4.xlsx')
    pods_access_df.to_excel('Legacy_Pods_Access_Links_no_flex_v4.xlsx')
    print('Data Written To Excel Successfully')
    ...


if __name__ == '__main__':
    Main()

