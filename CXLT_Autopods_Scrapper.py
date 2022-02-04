import os
import re
import time
import pprint as pp
import requests
import json
import argparse
from multiprocessing import cpu_count, Pool
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
from types import SimpleNamespace as sn
import urllib3
from Open_Pod_Page import Webdriver, Cisco_Login, Selenium_Cookies
import cookies
import pandas as pd
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


urls = ["https://cx-labs.cisco.com/graphql/", ]
Data = dict
def Main():
  parser = argparse.ArgumentParser(
          description='Tool to request legacy pod tool backend for pod infomation')
  parser.add_argument('pod_links', type=str,
                      help='txt file to list of pod links')
  args = parser.parse_args()
  start_time = time.time()
  cookies = Update_Cookies()
  pod_data = partial(Request_Pods,url=urls[0], cookies=cookies)
  pod_numbers = Read_AutoPods_CXLT(args.pod_links)
  print(f"pod_numbers:{len(pod_numbers)}")
  pods_data = []
  devices_data = []
  console_mappings = []
  access_links = []

  # No Optimization
  # for pod_num in pod_numbers:
  #   data = Request_Pods(pod_num, url)
  #   Parse_Data(data["data"]["podGetById"])
    
  # Multiprocessing
  # with Pool(8) as p:
  #   data = p.map(pod_data,pod_numbers)
  # print(f"data:{len(data)}")
  # print(type(data))
  # for d in data:
  #   Parse_Data(d["data"]["podGetById"])
  
  with ProcessPoolExecutor() as p:
    data = list(tqdm(p.map(pod_data,pod_numbers), total=len(pod_numbers)))
  print('[+]Done with requests')
  print(start_time - time.time())    
  for d in data:
    try:
      print(d['data']['podGetById']['id'])
    except TypeError:
      pp.pprint(d)
    (pod_data, pod_devices_data, console_data, access_methods) = Parse_Data(d["data"]["podGetById"])
    pods_data.append(pod_data)
    # break
    # print(pod_data)
    # break
    devices_data.extend(pod_devices_data)
    console_mappings.extend(console_data)
    access_links.extend(access_methods)
    # print(pod_data)
    # print('#' * 30)
    # pp.pprint(console_data)
  Data_Format(pods_data, devices_data, console_mappings, access_links)
  print(start_time - time.time())    

def Request_Pods( pod_number, url, cookies):
  payload = json.dumps({
    "operationName": "podGetById",
    "variables": {
      "withPortMappingAsset": False,
      "inclAssetReservations": False,
      "podId": f"{pod_number}",
      "stateFilters": [
        "ACTIVE",
        "FUTURE"
      ]
    },
    "query": "query podGetById($podId: ID!, $stateFilters: [ReservationState!], $withPortMappingAsset: Boolean = false, $inclAssetReservations: Boolean = false) {\n  podGetById(id: $podId) {\n    ... on Pod {\n      ...podFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment podFragment on Pod {\n  id\n  name\n  checkInWorkflowEnabled\n  description\n  status\n  site {\n    id\n    name\n    __typename\n  }\n  technologyTags {\n    id\n    name\n    description\n    __typename\n  }\n  contacts {\n    name\n    __typename\n  }\n  smes {\n    name\n    __typename\n  }\n  assets {\n    ...assetInterfaceFragment\n    __typename\n  }\n  pool {\n    ...assetPoolFragment\n    __typename\n  }\n  reservationPolicy {\n    ...reservationPolicyFragment\n    __typename\n  }\n  reservations(stateFilters: $stateFilters) {\n    ...podReservedFragment\n    __typename\n  }\n  allowedReservationPurposes\n  documentationLink\n  __typename\n}\n\nfragment assetInterfaceFragment on AssetInterface {\n  ...assetWithDeviceInfoFragment\n  assetAutomationConfiguration {\n    ...assetAutomationConfigurationFragment\n    __typename\n  }\n  children {\n    ...modulesFragment\n    __typename\n  }\n  location {\n    ...assetLocationFragment\n    __typename\n  }\n  powerMappings {\n    ...powerMappingsFragment\n    __typename\n  }\n  snmpSettings {\n    ...snmpSettingsFragment\n    __typename\n  }\n  accessMethods {\n    ...accessMethodFragment\n    __typename\n  }\n  consoleMappings {\n    ...consoleMappingFragment\n    __typename\n  }\n  ports {\n    ...assetPortFragment\n    __typename\n  }\n  reservations @include(if: $inclAssetReservations) {\n    results {\n      ...reservationCommonFragment\n      __typename\n    }\n    __typename\n  }\n  reservationPolicy {\n    ...reservationPolicyFragment\n    __typename\n  }\n  allowedReservationPurposes\n  ... on ConsoleServer {\n    reverseTelnetEnabled\n    reverseSshEnabled\n    minimumTtyLine\n    maximumTtyLine\n    enabled\n    __typename\n  }\n  ... on PDU {\n    ...pduFragment\n    __typename\n  }\n  __typename\n}\n\nfragment assetWithDeviceInfoFragment on AssetInterface {\n  archived\n  description\n  eitmsCode\n  eitmsId\n  enablePassword\n  username\n  password\n  existsInEitms\n  generatedName\n  id\n  isEitmsAsset\n  lastBarcodeScanAt\n  lastEitmsSyncAt\n  lastLabSyncAt\n  name\n  product {\n    id\n    automationConfiguration {\n      defaultPlatform\n      checkInWorkflowMaxDuration\n      automationConfigurations {\n        ...platformAutomationConfigurationFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  rackPosition\n  rackUnitHeight\n  serialNumber\n  status\n  eitmsType\n  vendor\n  parent {\n    id\n    __typename\n  }\n  pool {\n    ...assetPoolFragment\n    __typename\n  }\n  pod {\n    ...basicPodFragment\n    __typename\n  }\n  ... on Asset {\n    automationCapabilities {\n      ...automationCapabilitiesFragment\n      __typename\n    }\n    automationStatus {\n      ...syncTaskFragment\n      __typename\n    }\n    automatrixPortAssignments {\n      ...automatrixPortAssignmentFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment platformAutomationConfigurationFragment on PlatformAutomationConfiguration {\n  platform\n  saveConfigurationEnabled\n  loadConfigurationEnabled\n  changeCredentialsEnabled\n  changeImageEnabled\n  cleanDeviceEnabled\n  downloadFileEnabled\n  infoCollectorEnabled\n  labSyncEnabled\n  __typename\n}\n\nfragment assetPoolFragment on AssetPool {\n  id\n  name\n  description\n  gdp\n  myPermissions\n  __typename\n}\n\nfragment basicPodFragment on Pod {\n  id\n  name\n  status\n  checkInWorkflowEnabled\n  reservationPolicy {\n    ...reservationPolicyFragment\n    __typename\n  }\n  allowedReservationPurposes\n  reservations {\n    results {\n      ...reservationCommonFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment reservationPolicyFragment on ReservationPolicy {\n  id\n  name\n  minimumInitialReservation\n  maximumInitialReservation\n  maximumReservationExtension\n  maximumTotalReservation\n  allowReservationsIntoTheFuture\n  notificationRules {\n    beforeEnd\n    __typename\n  }\n  siteFilters {\n    ...siteSlectOptionsFragment\n    __typename\n  }\n  __typename\n}\n\nfragment siteSlectOptionsFragment on Site {\n  id\n  __typename\n}\n\nfragment reservationCommonFragment on ReservationInterface {\n  id\n  startDate\n  endDate\n  type\n  workspace {\n    ...reservationWorkspaceFragment\n    __typename\n  }\n  __typename\n}\n\nfragment reservationWorkspaceFragment on Workspace {\n  id\n  name\n  owner {\n    name\n    __typename\n  }\n  purpose\n  state\n  priority\n  __typename\n}\n\nfragment automationCapabilitiesFragment on AssetAutomationCapabilities {\n  __typename\n  lastModified\n  lastRunTaskId\n  clearLine\n  powerConnections\n  gatewayConnectivity\n  imageAvailability\n  downloadFile\n  cleanDevice\n  changeImage\n  saveLoadConfig\n  changeCredentials\n  subsystemRecovery\n  passwordRecovery\n}\n\nfragment syncTaskFragment on Task {\n  id\n  status\n  __typename\n}\n\nfragment automatrixPortAssignmentFragment on AutomatrixPortAssignment {\n  id\n  port {\n    ...automatrixPortFragment\n    __typename\n  }\n  asset {\n    id\n    __typename\n  }\n  assetPort\n  __typename\n}\n\nfragment automatrixPortFragment on AutomatrixPort {\n  id\n  port\n  enabled\n  node {\n    asset {\n      name\n      generatedName\n      __typename\n    }\n    domain {\n      id\n      __typename\n    }\n    __typename\n  }\n  assignments {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment assetAutomationConfigurationFragment on AssetAutomationConfiguration {\n  automationConfiguration {\n    ...platformAutomationConfigurationFragment\n    __typename\n  }\n  powerSchedulingDisabled\n  checkInWorkflowMaxDuration\n  checkInWorkflowEnabled\n  defaultSnapshot {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment modulesFragment on Asset {\n  id\n  eitmsType\n  name\n  generatedName\n  location {\n    ...assetLocationFragment\n    __typename\n  }\n  product {\n    id\n    __typename\n  }\n  serialNumber\n  eitmsCode\n  lastBarcodeScanAt\n  pool {\n    ...assetPoolFragment\n    __typename\n  }\n  __typename\n}\n\nfragment assetLocationFragment on Location {\n  __typename\n  ... on Site {\n    ...minimalSiteFragment\n    __typename\n  }\n  ... on Lab {\n    ...minimalLabFragment\n    __typename\n  }\n  ... on Aisle {\n    ...minimalAisleFragment\n    __typename\n  }\n  ... on AisleLocation {\n    ...minimalAisleLocationFragment\n    __typename\n  }\n}\n\nfragment minimalSiteFragment on Site {\n  id\n  name\n  __typename\n}\n\nfragment minimalLabFragment on Lab {\n  id\n  name\n  site {\n    ...minimalSiteFragment\n    __typename\n  }\n  services {\n    ntpService\n    dnsService\n    httpProxyService\n    ftpService\n    vpnService\n    ftpServiceUsername\n    ftpServicePassword\n    __typename\n  }\n  __typename\n}\n\nfragment minimalAisleFragment on Aisle {\n  id\n  name\n  lab {\n    ...minimalLabFragment\n    __typename\n  }\n  __typename\n}\n\nfragment minimalAisleLocationFragment on AisleLocation {\n  id\n  name\n  aisle {\n    ...minimalAisleFragment\n    __typename\n  }\n  __typename\n}\n\nfragment powerMappingsFragment on PowerMapping {\n  description\n  assetOutlet\n  pduOutlet\n  pdu {\n    ...pduFragment\n    location {\n      ...assetLocationFragment\n      __typename\n    }\n    product {\n      id\n      __typename\n    }\n    pool {\n      ...assetPoolFragment\n      __typename\n    }\n    ports {\n      ...assetPortFragment\n      __typename\n    }\n    accessMethods {\n      ...accessMethodFragment\n      __typename\n    }\n    __typename\n  }\n  status {\n    status\n    time\n    __typename\n  }\n  __typename\n}\n\nfragment pduFragment on PDU {\n  id\n  name\n  generatedName\n  enabled\n  position\n  maxOutputWatts\n  outlets\n  excludedOutlets\n  outletMappings {\n    description\n    pduOutlet\n    assetOutlet\n    status {\n      status\n      time\n      __typename\n    }\n    asset @include(if: $withPortMappingAsset) {\n      id\n      name\n      product {\n        id\n        __typename\n      }\n      maxWattDraw\n      archived\n      location {\n        ...assetLocationFragment\n        __typename\n      }\n      eitmsCode\n      reservations {\n        results {\n          ...reservationCommonFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment assetPortFragment on AssetPort {\n  id\n  name\n  interface {\n    address\n    recordName\n    parent {\n      network\n      gateway\n      __typename\n    }\n    vrf {\n      id\n      __typename\n    }\n    status\n    __typename\n  }\n  primary\n  __typename\n}\n\nfragment accessMethodFragment on AssetAccess {\n  __typename\n  description\n  name\n  password\n  port\n  type\n  url\n  username\n}\n\nfragment snmpSettingsFragment on SNMPSettings {\n  __typename\n  version\n  publicCommunity\n  privateCommunity\n  username\n  password\n}\n\nfragment consoleMappingFragment on ConsoleMapping {\n  __typename\n  description\n  consoleServer {\n    ...consoleServerFragment\n    __typename\n  }\n  assetPort\n  ttyLine\n}\n\nfragment consoleServerFragment on ConsoleServer {\n  __typename\n  enabled\n  id\n  maximumTtyLine\n  minimumTtyLine\n  ports {\n    ...assetPortFragment\n    __typename\n  }\n  location {\n    ...assetLocationFragment\n    __typename\n  }\n  accessMethods {\n    ...accessMethodFragment\n    __typename\n  }\n  reverseSshEnabled\n  reverseTelnetEnabled\n}\n\nfragment podReservedFragment on PodReservationPaginationResult {\n  pageInfo {\n    ...pageInfoFragment\n    __typename\n  }\n  results {\n    ...podReservationsFragment\n    __typename\n  }\n  errors {\n    fieldName\n    errorMessage\n    __typename\n  }\n  __typename\n}\n\nfragment pageInfoFragment on PagingInformation {\n  pageNumber\n  perPage\n  totalPages\n  totalResults\n  __typename\n}\n\nfragment podReservationsFragment on PodReservation {\n  id\n  startDate\n  endDate\n  workspace {\n    ...reservationWorkspaceFragment\n    __typename\n  }\n  createdByUser {\n    name\n    __typename\n  }\n  returnedByUser {\n    name\n    __typename\n  }\n  closureNotes\n  type\n  __typename\n}\n"
  })
  headers = {
    'authority': 'cx-labs.cisco.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'accept': '*/*',
    'content-type': 'application/json',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://cx-labs.cisco.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://cx-labs.cisco.com/pods/5',
    'accept-language': 'en-US,en;q=0.9'
  }
  response = requests.request("POST", url, headers=headers, data=payload, cookies=cookies, verify=False)
  data = json.loads(response.text)
  return data

def Read_AutoPods_CXLT(filename):
    pod_link_regex = re.compile(r'https://cx-labs.cisco.com/pods/(\d{1,4})')
    with open(filename, 'r+') as f:
        pod_file = f.read()
    pod_links = re.findall(pod_link_regex, pod_file)
    return pod_links

def Update_Cookies():
  filename = 'cookies.pkl'
  one_day_ago = (time.time() - 86400)
  if os.path.isfile(filename):
    if os.stat(filename).st_mtime <= one_day_ago:
      os.remove(filename)
      print('[-]Old Cookies\n[+]Starting Webdriver...')
      Collect_Cookies()
  else:
    print('[-]No Cookies File Found\n[+]Starting Webdriver...')
    Collect_Cookies()
  print('[+]Cookies Found')
  print('[+]Loading Cookies...')
  c = cookies.load_cookies(filename)
  return c

def Collect_Cookies():
  d = Webdriver(True)
  print('[+]Collecting Cookies...')
  Cisco_Login(d,"https://cx-labs.cisco.com/")
  print(Selenium_Cookies(d))
  ...

def Parse_Data(pod_data):
  removable_pod_keys = ['technologyTags','description','__typename','reservations','pool','allowedReservationPurposes','reservationPolicy','checkInWorkflowEnabled','smes','contacts']      #Not needed keys from the data obj recived from pod page
  
  for key in removable_pod_keys:    #Start of cleaning pod_data to only hold checkable info
    del pod_data[key]
  pod_data['site'] = pod_data['site']['name']   
  if pod_data['site'] == 'Richardson':
    pod_data['site'] = 'RCDN'
  pod_data['doc'] = pod_data['documentationLink']
  del pod_data['documentationLink']
  pod_data['total_devices'] = len(pod_data['assets'])


  devices_data = []     #List that will hold device objs for each device in a pod
  devices_console_data = []   #List that will hold console mapping objs for each devices console mappings
  devices_access_methods = []
  power_mappings = []   #List that will hold power mapping objs for each devices power mapings

  #Not needed keys from the data obj recived from pod page
  removable_device_keys = ['snmpSettings','eitmsId','pod','pool','archived','parent','eitmsType','rackUnitHeight','rackPosition','generatedName','children', '__typename', 'automatrixPortAssignments','automationStatus','automationCapabilities','allowedReservationPurposes','reservationPolicy','description','vendor','lastLabSyncAt','lastEitmsSyncAt','lastBarcodeScanAt','isEitmsAsset','existsInEitms','id']   
  
  #Creation of device data dict
  try:
    devices_raw_data = pod_data.pop('assets') #Hold raw assests list of dicts from orginal data obj from pod page
  except IndexError:
    print(f'[-]Pod-{pod_data["id"]} has no devices')
    return (pod_data,[],[],[])
  for device in devices_raw_data:     #Start of cleaning device_data to only hold checkable info
    for key in removable_device_keys:
      del device[key]
    device['pod'] = pod_data['id']
    device['access_links'] = len(device['consoleMappings']) + len(device['accessMethods'])
    if bool(device['accessMethods']) == False:
      del device['accessMethods']
    if bool(device['ports']) == False:
      del device['ports']
    device['platform'] = device['assetAutomationConfiguration']['automationConfiguration']['platform']
    del device['assetAutomationConfiguration']
    device['pid'] = device['product']['id']
    del device['product']
 
    try:
      device_console_data = device.pop('consoleMappings') #Creation of console mapping obj
      for console_data in device_console_data:    #Start of cleaning console_data to only hold checkable info
        console_data['user'] = device['username']
        console_data['pass'] = device['password']
        console_data['enable'] = device['enablePassword']
        console_data['pod'] = pod_data['id']
        console_data['device_id'] = device['eitmsCode']
        console_data['ip'] = console_data['consoleServer']['ports'][0]['interface']['address']
        console_data['hostname'] = console_data['consoleServer']['ports'][0]['interface']['recordName'].split('.')[0]
        del console_data['assetPort']
        del console_data['__typename']
        del console_data['consoleServer']

        if 'Console' in console_data['description']:
          console_data['protocol'] = 'telnet'
        del console_data['description']
        console_data['port'] = console_data['ttyLine']
        del console_data['ttyLine']
        if console_data['port'] < 100:
          console_data['port'] = console_data['port'] + 2000
      devices_console_data.extend(device_console_data)
    except KeyError:
      ...
    try:
      device_access_methods = device.pop('accessMethods')
      for access_method in device_access_methods:
        del access_method['__typename']
        del access_method['name']
        del access_method['description']
        access_method['pod'] = pod_data['id']
        access_method['protocol'] = access_method['type']
        del access_method['type']
        access_method['ip'] = access_method['url']
        del access_method['url']
        access_method['device_itm'] = device['eitmsCode']
      devices_access_methods.extend(device_access_methods)
    except  KeyError:
      print(f'[-]Device {device["eitmsCode"]} has no additional access methods')

    if 'pop' in device.keys():
      device.pop('powerMappings')
    if 'ports' in device.keys():
      device.pop('ports')
      # device_access_methods = ['No Access Methods']
    # finally:
      




    # print(device_console_data)

    # power_mappings.append(device.pop('powerMappings'))
    # Power Mappings Dont need to be handled atm 
    # Need
    # Pod Obj
    # Devices Obj
    # Creds Obj
    # Access Link Obj
    # device_power_mapping = device.pop('powerMappings') #Creation of power mapping dict
    # try:
    #   device_power_mapping = device_power_mapping[0]
    #   device_power_mapping = {'pdu':device_power_mapping['pdu']['name'],'outlet':device_power_mapping['pduOutlet']}
    # except IndexError:
    #   device_power_mapping = {'pdu':'No Mapping','outlet':'No Mapping'}


    # pp.pprint(device.keys())
    device['location'] = {'aisle':device['location']['aisle']['name'], 'rack':device['location']['name'] }
  #   print(device['ports'])
  #   print(device['pod'])
  #   print(device['platform'])
  # print(device)
    devices_data.append(device)
    # print(pod_data['id'])
    # print(device_power_mapping['outlet'])
    # print('test')
    # print(pod_data)
  # print('devices Len')
  # print(len(devices_data))
  return (pod_data, devices_data, devices_console_data, devices_access_methods)

def Data_Format(pods_data, devices_data, console_links, access_methods):
  # pd.set_option("display.width", 1000, "display.max_columns", 1000)
  pd.set_option("display.max_rows", 1000, "display.max_columns", 1000)
  pods_df = pd.DataFrame(pods_data)
  pods_df.rename(columns={'id':'pod'}, inplace=True)
  pods_df = pods_df[['pod', 'name','doc', 'site', 'total_devices']]
  # if len(devices_data) < 0:
  devices_df = pd.DataFrame(devices_data)
  devices_df = devices_df[['pod', 'eitmsCode', 'name', 'location', 'platform', 'status', 'serialNumber', 'pid', 'access_links']]
    # if len(console_links) < 0:
  console_links_df = pd.DataFrame(console_links)
  console_links_df = console_links_df[['pod', 'device_id', 'ip', 'hostname', 'protocol', 'port', 'user', 'pass', 'enable']]
      # if len(access_methods) < 0:
  access_methods_df = pd.DataFrame(access_methods)
  access_methods_df = access_methods_df[['pod', 'device_itm', 'ip', 'protocol', 'port', 'username', 'password']]
  # print('Pods')
  # print(pods_df)
  # print('#'*30)
  # print('Pod Devices')
  # print(devices_df)
  # print('#'*30)
  # print('Console Links')
  # print(console_links_df)
  # print('#'*30)
  # print('Access Methods')
  # print(access_methods_df)
        
   #spreadsheet creation
  pods_df.to_excel('CXLT_Compare_Pods.xlsx')
  # devices_df.to_excel('CXLT_Pods_Device.xlsx')
  # console_links_df.to_excel('CXLT_Console_Mappings.xlsx')
  # access_methods_df.to_excel('CXLT_Pods_Access_Links.xlsx')
  # pp.pprint(pods_data)
  print('Data Written To Excel Successfully')
  
  
  ...
if __name__ == '__main__':
  Main()