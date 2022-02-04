import pandas as pd
from tqdm import tqdm
import numpy as np

# cxlt_df = pd.read_excel('CXLT_Compare_Pods.xlsx')
# leg_df = pd.read_excel('Legacy_Pods.xlsx')

cxlt_df = pd.read_excel('CXLT_Pods_Device.xlsx')
leg_df = pd.read_excel('Legacy_Pods_Devices.xlsx')
pd.set_option( "display.max_rows", 20, 'display.max_columns', None)
print(cxlt_df.columns)
print(leg_df.columns)

def Compare_Devices(legacy_devices, cxlt_devices):
    cxlt_devices.rename(columns={'eitmsCode':'ITM', 'serialNumber':'serial'},inplace=True)
    legacy_devices.drop(['last_image','location'], axis=1, inplace=True)
    cxlt_devices.drop('location', axis=1, inplace=True)

    print(cxlt_devices.columns)
    print(legacy_devices.columns)

    cxlt_devices = cxlt_devices[['pod', 'ITM', 'name', 'platform', 'status', 'serial',
        'pid', 'access_links']]
    legacy_devices = legacy_devices[['pod', 'ITM', 'name', 'platform', 'status', 'serial',
        'pid', 'access_links']]
    # cxlt_devices.reset_index(drop=True,inplace=True)
    # legacy_devices.reset_index(drop=True,inplace=True)

    merged_data = cxlt_devices.merge(legacy_devices, on='name', how='outer')
    merged_data.replace(r'^\s+$', np.nan, regex=True)
    print('#'*40)
    # print(merged_data)
    # print(merged_data.columns)
    print(merged_data.head())
    updated_cxlt = merged_data.iloc[:,:8]
    updated_leg = merged_data.iloc[:,8:]
    print(updated_cxlt.head())
    print(updated_leg.head())
    # updated_cxlt= merged_data[['pod_x', 'ITM_x', 'name_x', 'platform_x', 'status_x', 'serial_x','pid_x', 'access_links_x']]
    # updated_leg = merged_data[['pod_y', 'ITM_y', 'name_y', 'platform_y', 'status_y', 'serial_y','pid_y', 'access_links_y']]
    # updated_leg.rename({'pod_y':'pod_x','ITM_y':'ITM_x', 'name_y':'name_x', 'platform_y':'platform_x', 'status_y':'status_x', 'serial_y':'serial_x','pid_y':'pid_x', 'access_links_y':'access_links_x' }, axis= 1,inplace=True)
    print(len(updated_leg.index))
    print(len(updated_cxlt.index))
    # updated_cxlt['pod_x'] = updated_cxlt['pod_x'].fillna(533)
    # print(updated_cxlt['pod_x'])
    # sorted_cxlt = updated_cxlt.sort_values(by=['pod_x'])
    # sorted_leg = updated_leg.sort_values(by=['pod_x'])
    merged_data.to_excel('Merged_pod_v2_devices.xlsx')
    # sorted_cxlt.to_excel('sorted_cxlt.xlsx')
    # sorted_leg.to_excel('sorted_leg.xlsx')
    # compared = updated_leg.compare(updated_cxlt, keep_shape=True)
    # print(compared)
    # compared.to_excel('Compared_v2_devices.xsls')
    ...


# leg_df.merge(cxlt_df, on='name').to_excel('Merged_pod_leg_left_devices.xlsx')
# print(cxlt_df.columns)
# print(leg_df.columns)
# print(cxlt_df)
# print(leg_df)
# print(leg_df.reset_index(drop=True).equals(cxlt_df.reset_index(drop=True)))
# print(leg_df.eq(cxlt_df))
# print(leg_df.compare(cxlt_df, align_axis=0) )#List diffrence on top of each other
# print(leg_df.compare(cxlt_df) )#List diffrence next to each other
# print(leg_df.compare(cxlt_df, keep_equal=True))#List everything, even the matches are shown
# print(leg_df.compare(cxlt_df, keep_shape=True))#List all colloums even the ones with mathcing data
# print(leg_df.compare(cxlt_df))#List all colloums even the ones with mathcing data
# print('shortand df')


# compared.dropna(subset=[('name', 'self'),('site', 'self'),('doc', 'self'),('total_devices', 'self')], inplace=True, how='all')
# print(compared.keys())
# # print(compared.keys())
# # print(compared.dropna(subset=['name'], axis=1))

def Compare_Pods(legacy_pods, cxlt_pods):
    compared = legacy_pods.compare(cxlt_pods, keep_shape=True)
    # compared.dropna(subset=[('pod', 'self'),('ITM', 'self'),('name', 'self'),('location', 'self'),('platform', 'self'),('status', 'self'),('serial', 'self'),('pid', 'self'),('access_links', 'self')], inplace=True, how='all')
    compared = compared.fillna('Match')
    compared.drop([('Unnamed: 0','self'),('Unnamed: 0','other')], axis=1, inplace=True)
    print(compared)
    compared.to_excel('Compared_Pods.xlsx')
    ...
    
Compare_Devices(leg_df,cxlt_df)