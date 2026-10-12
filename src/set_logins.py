'''
Created on Sep 16, 2025

@author: bill
'''
import keyring
import getpass

from OWI_logins import OWI_FTP_ADDRESS #, OWI_FTP_USERNAME, OWI_FTP_PATH

def set_ftp_logins():
    ftpsite = OWI_FTP_ADDRESS
    ftppath = input(f"Enter the FTP path:  {OWI_FTP_ADDRESS}/")
    username = input("Enter your FTP username: ")
    password = getpass.getpass("Enter your FTP password: ")
    
    
    if ftppath and username and password:
        data = '|'.join([ftppath, username, password])
        keyring.set_password('OWI_ftp', 'bill', data)
        print(f"Credentials stored in keyring for '{username}@{ftpsite}/{ftppath}'")
    else:
        print(f"Credentials not set")
        
def get_ftp_logins():
    data = keyring.get_password('OWI_ftp', 'bill')
    if 0: # for trouble shooting only. Do not normally display.
        print(f"CWI login saved in keyring = '{data}'")
    ftppath, username, password = data.split('|')
    return OWI_FTP_ADDRESS, ftppath, username, password

if __name__ == '__main__':
    set_ftp_logins()
