import netmiko
from netmiko import ConnectHandler as CH
from Pod_ScrapperV1 import scrapeToVar
from Pod_ScrapperV1 import argInit as Var
from Pod_Con import connect
import colorama
from colorama import Fore, Style, Back

colorama.init(autoreset=True)

# Device Obj Example
# test_device={
#          "device_type":"cisco_ios_telnet",
#          "host": "F241-04-13-COMM",
#          "username":"admin",
#          "password": "cisco!123", 
#          "secret": "cisco!123", 
#          "port":2005}

def Format(tn):
    print("[+]Starting Format Sequence.....")
    try:
        tn.enable()
        prompt = tn.find_prompt()
        hostname = prompt[0:-1]
        print(f"[+]{test_device['host']} ~~~ Connected ")
        print(f"[+]Hostname {hostname} ")
        output = tn.send_command_timing(command_string='format flash:', strip_prompt=True,strip_command=False)
        print("[+]Sending Format Command")
        if "[confirm]" in output:
            output = tn.send_command_timing(command_string='\n', strip_prompt=False,strip_command=False)
            print("◉")
        if "[confirm]" in output:
            output = tn.send_command_timing(command_string='\n', strip_prompt=False,strip_command=False)
            if "Format of flash: complete" in output:
                print("[+]Flash Formatted")
            else:
                print(output)
        print(tn.read_channel())
        # output = tn.send_command_timing('relo', strip_prompt=False, strip_command=False)
        # if "confirm" in output:
        #     tn.send_command_timing('\n', strip_prompt=False, strip_command=False)
        # print("[+]Reload command sent")
        # print('-----------------------------------------------')
    except:
        print("Error")

def Write_erase(tn):
    print("[+]Starting Write Erase Sequence.....")
    tn.enable()
    output = tn.send_command_timing("write erase", strip_prompt=False, strip_command=False)
    print("[+]Sending Erase Command")
    if "confirm" in output:
        output = tn.send_command_timing("\n", strip_prompt=False, strip_command=False)
    if "Erase of nvram: complete" in output:
        print("[+]Write Erased\n\n")
    

def Set_boot_var(tn, file):
    output = tn.send_config_set(["no boot system", f'boot system flash:{file}'], delay_factor=5)
    tn.enable()
    output = tn.send_command("sh boot")
    if f"BOOT variable = flash:{file};" in output:
        print("[+]Boot Var Updated")
    else:
        print('[-]Error Boot Var\n\n')
        print(output)

def Save_reload(tn):
    try:
        output = tn.save_config(delay_factor=5)
    except:
        output = tn.send_command_timing('wr', strip_prompt=False, strip_command=False)
        tn.send_command_timing('\n', strip_prompt=False, strip_command=False)
    if "[OK]" in output:
        print("[+]Config Saved")
        output = tn.send_command_timing('relo', strip_prompt=False, strip_command=False)
    if '[yes/no]' in output:
        tn.send_command_timing('yes', strip_prompt=False, strip_command=False)
        # output += tn.send_command_timing('\n', strip_prompt=False, strip_command=False)
        print('[+]Reload Initated')
    else:
        print(output)

def Hostname(tn, name):
    print('[+]Changing Hostname')
    tn.enable()
    try:
        tn.send_config_set([f'hostname {name}'],  strip_prompt=False, strip_command=False, cmd_verify=True, delay_factor=7)
        prompt = tn.find_prompt()
        if name in prompt:
            print('[+]Hostname Changed')
            try:
                output = tn.save_config(delay_factor=5)
            except:
                output = tn.send_command_timing('wr', strip_prompt=False, strip_command=False)
                tn.send_command_timing('\n', strip_prompt=False, strip_command=False)
            if "[OK]" in output:
                print("[+]Hostname Saved")
    except netmiko.ssh_exception.NetmikoTimeoutException as e:
        print("[-]Hostname Error")
        print(e)

def Special():
    devices = [{
         "device_type":"cisco_ios_telnet",
         "host": "F241-03-26-COMM",
         "username":"admin",
         "password": "cisco!123", 
         "secret": "cisco!123", 
         "port":2016}, {
         "device_type":"cisco_ios_telnet",
         "host": "F241-03-26-COMM",
         "username":"admin",
         "password": "cisco!123", 
         "secret": "cisco!123", 
         "port":2017},
        {"device_type":"cisco_ios_telnet",
         "host": "F241-03-26-COMM",
         "username":"admin",
         "password": "cisco!123", 
         "secret": "cisco!123", 
         "port":2017}]
    output = []
    for d in devices:
        try:
            tn = CH(**d)
        except:
            print('[-]Connection Error')
        else:   
            tn.enable()
            try:
                output.append(tn.send_command_timing('sh inter br | i up'))
            except:
                print('[-]Command Error')

    for i in output:
        print(i)

def Main():
    for i in range(6):
        try:
            tn = CH(**test_device)
            Write_erase(tn)
            Format(tn)
        except:
            print(f'Device on port {test_device["port"]} failed')
        nxt_port = {'port': test_device['port'] + 1}
        test_device.update(nxt_port)

# tn = CH(**test_device) 
# Set_boot_var(tn, "cat3k_caa-universalk9.16.12.05b.SPA.bin")
# Hostname(tn, 'F241.10.22-9300-106E')
# Save_reload(tn)
# name = 'F241.04.13-3850-1'
# for i in range(2):
#     tn = CH(**test_device) 
#     Hostname(tn, name)
#     test_device.update({'port':2004})
#     name = 'F241.04.13-3850-2'
# expect_string='Format operation will destroy all data in "flash:".  Continue? [confirm]
# Special()


# pod = scrapeToVar(Var())

# connect(pod['AutoPod-1952'][1])

if __name__ == '__main__':
    Main()