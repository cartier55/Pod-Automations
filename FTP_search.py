from ftplib import FTP
import argparse
from types import SimpleNamespace
user='calo'
passwd='calo'
host='10.122.153.158'

def main():
    parser = argparse.ArgumentParser(description='Enter File To Search Calo FTP Server For')
    parser.add_argument('filename', type=str, help='File To Search For', action='append')
    parser.add_argument('-H', '--Host', dest='Host', default='10.122.153.158', type=str, help=f'FTP Server Default {host}')
    args = parser.parse_args()
    # if args.Host:
    #     host = args.Host
    # else:
    #     print('Deafault Host')
    # print(args.filename)
    Search(args)
      

def Search(args):
    ftp = FTP(args.Host)
    ftp.login(user=user, passwd=passwd)
    dir = ftp.nlst()
    for line in dir:
        if args.filename[0] in line:
            print(f'[+]{line} is avaliable on {args.Host} FTP Server')
            ftp.quit()
            break
        else:
            continue
    print(f'[-]{args.filename[0]} is not available on {args.Host}')

def Download():
    ftp = FTP(host)
    ftp.login(user=user, passwd=passwd)
    ftp.retrbinary('hello.txt', print)



'cat9k_iosxe.17.03.03.SPA.bin'

main()
# Download()