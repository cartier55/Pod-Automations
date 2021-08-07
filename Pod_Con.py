from netmiko import ConnectHandler as CH

def connect(device):
    try:
        conn = CH(**device)
        prompt = conn.find_prompt()
    except KeyboardInterrupt:
        print(f'[-]{device[host]}')
        print('[-]Connection Error')
    else:
        print('[+]Connected')
        print(prompt)
        return conn


# def main():
#     for device in devices:
#         connect(device)

# main()