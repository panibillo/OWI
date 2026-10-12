'''
Created on Oct 10, 2021

Private FTP login values for the CWI download.
User should obtain values from the Minnesota Geologic Survey.
Copy this file in the src directory as OWI_secrets.py, and enter the values.
OWI_secrets.py is named in .gitignore.
Do not share it, and do not add it to the repository.

Values left as empty strings are ignored.
Then the FTP login is looked up in the keyring, then in environment variables,
and finally the user is asked.
See class ftp_params in OWI_download_ftp.py.

@author: Bill
'''

# Keyring entry where the FTP login is stored
CWI_FTP_KEYRING_SERVICE = ""
CWI_FTP_KEYRING_USER = ""

# The ftp address
CWI_FTP_SITE = ""

# Path on the ftp address where the download files are found
CWI_FTP_DATA_PATH = ""

# ftp login information
CWI_FTP_USER = ""
CWI_FTP_PASS = ""
