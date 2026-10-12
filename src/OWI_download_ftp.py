'''
OWI database

Dependencies:
    Python >= 3.7
    OWI_logins.py  

Some code is copied from convert_cwi_to_pandas.py by Randal Barnes     

The purpose of module OWI_download_ftp is to download specified zip files from  
the Minnesota Geologic Survey ftp site, and unzip the files.  

Method RUN_download_cwi demonstrates usage.

Manual download instruction:

'''

import os, shutil
import time
import datetime
from ftplib import FTP
import zipfile
import csv

import logging

from OWI_config import versioninfo


def xlsx_to_csv(xlsx_file, csv_file=None):
    """
    Converts an .xlsx file to .csv format on Ubuntu or any OS with Python.

    Parameters:
        xlsx_file (str): Path to the .xlsx file.
        csv_file (str, optional): Path to save the .csv file. Defaults to the same name as the .xlsx file in the same directory.

    Returns:
        bool: True on success.

    Requires openpyxl (imported here so the module loads without it).
    """

    # print (f"Found xlsx files rather than csv.\n > Converting: {xlsx_file}\n > To: {csv_file}")
    # Check if the .xlsx file exists
    if not os.path.exists(xlsx_file):
        raise FileNotFoundError(f"The file '{xlsx_file}' does not exist.")
    if csv_file is None:
        csv_file = os.path.splitext(xlsx_file)[0] + '.csv'

    # Read the Excel file and save it as CSV
    try:
        from openpyxl import load_workbook

        # Read the first sheet of the Excel file, row by row, into the CSV file
        wb = load_workbook(xlsx_file, read_only=True, data_only=True)
        try:
            with open(csv_file, 'w', newline='') as f:
                w = csv.writer(f)
                for row in wb.worksheets[0].iter_rows(values_only=True):
                    w.writerow(['' if v is None else v for v in row])
        finally:
            wb.close()
        assert os.path.exists(csv_file)
        #print(f" Converted '{xlsx_file}' to '{csv_file}'.")
    except Exception as e:
        raise RuntimeError(f"Failed to convert {xlsx_file} to CSV: {e}")
    
    return True



log = logging.getLogger('CWI_refresh')
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

__author__ = "William C Olsen"
__version__ = "2021-10-10"

def download_cwi_from_ftp( ftpaddr,
                           ftppath,
                           ftpuser, 
                           ftppass,
                           downloadpath,
                           downloadshppath,
                           downloadfiles):
    ''' 
    Download newer cwi files from ftp. Unzip. Return list of new files. 
    
    This function downloads and extracts cwi files from the MGS ftp site.
    File dates are compared, and the ftp download only progresses if the
    ftp version is newer.  
    
    The ftp login is found by RUN_download_cwi in the keyring,
    in environment variables, or by asking the user.
    The download targets are defined in OWI_config.py
    
    Notes on variable names:
        src is used for ftp source files
        dst is used for local copies of the files
    '''

    log.info(msg=('Downloading CWI sources from ftp site'))
    rv = []
    ftpstart = time.time()
    with FTP(ftpaddr) as ftp:
        if ftppass == '<ask>':
            import getpass
            ftppass = getpass.getpass(prompt=f'Enter password for ftp user "{ftpuser}": ')
            
        ftp.login(user=ftpuser, passwd=ftppass)
        log.debug(msg='ftp Log-in successful')
        
        # Get the modify dates of the files on the ftp site. Formatted as integer, e.g. 20170521081548
        dict_ftp_file_modify_times = {f[0].lower():int(float(f[1].get('modify'))) for f in ftp.mlsd(path=ftppath)}
        for key,val in dict_ftp_file_modify_times.items():
            print (val, key)
    
        os.makedirs(downloadpath, exist_ok=True)
        os.makedirs(downloadshppath, exist_ok=True)
        
        for fname in downloadfiles:
            key = fname.lower()
            if 'locs' in fname: 
                destfile = os.path.join(downloadshppath, fname)
            else:
                destfile = os.path.join(downloadpath, fname)
            if os.path.exists(destfile) and key in dict_ftp_file_modify_times:
                # Compare file times to see if a fresh download is needed
                mtime = datetime.datetime.fromtimestamp( os.path.getmtime(destfile) )
                desttime = int(mtime.strftime('%Y%m%d%H%M%S'))
                
                if dict_ftp_file_modify_times[key] < desttime:
                    log.info(f'{fname} is up to date. Download skipped.')
                    continue
                
            start = time.time()
            print( f"downloading {fname} ...", end='' )
            
            with open(destfile, 'wb') as localfile:
                try:
                    ftp.retrbinary('RETR '+ftppath+'/'+fname, localfile.write, 1024 )
                except Exception as e:
                    lines = ftp.retrlines('LIST')
                    print (lines)
                    print (f"ERROR downloading {ftppath+'/'+fname} to {destfile} : {e}")
                    continue
                    #raise e
                    
            duration = (time.time()-start)/60.0
            print( f"  ... DONE. completed in {duration:1.3f} minutes")
            rv.append (destfile)
            
            if '.zip' in fname:
                print(f"unzipping {destfile} ..." )
                
                with zipfile.ZipFile(destfile, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(destfile))  
                
                log.info(f'{fname} downloaded and unzipped.')
            else:
                log.info(f'{fname} downloaded.')
                
    # for basename in ('wells.', 'unloc_wells.', 'cwilocs.zip'):
    #     for f in os.listdir(downloadpath):
    #         if f.startswith(basename):
    #             src = os.path.join(downloadpath, f)
    #             dst = os.path.join(downloadshppath, f)
    #             try:
    #                 shutil.move (src, dst)
    #             except Exception as e:
    #                 print (f'Moving "{src}" to "{dst}"')
    #                 print (e)
    
    duration = (time.time()-ftpstart)/60.0    
    print(f"*** ftp download & unzip finished in {duration:1.3f} minutes ***" )  
    
    if 0:
        # As of Sept 2025, observed no .xlsx files in downloaded files. 
        # This block of code is commented out to prevent accidental errors.
        # If .xlsx files exist, they may be local products rather than new data.
        # Run this block only after re-analysis!
        for dirpath, dirnames, filenames in os.walk(downloadpath):
            for file in filenames:
                if file.endswith(".xlsx"):
                    xlsxname = os.path.join(dirpath, file)
                    csvname = xlsxname.replace(".xlsx",".csv")
                    if os.path.exists(csvname):
                        print(f"Found csv:  {csvname}")  
                        with open(csvname, 'r') as file:
                            for i, line in enumerate(file):
                                print(line.strip())
                                if i > 6:  # Stop after 7 lines
                                    break
                        print ()
    
                    else:
                        print(f"Found xlsx: {xlsxname}  Converting ...", end=" ")
                        ok = xlsx_to_csv(xlsxname, csvname)
                        assert ok, csvname
                        print (csvname)
                           
    return rv

class ftp_params:
    addr = None
    path = None
    user = None
    passwd = None

    def get_from_keyring(self):
        # Credentials are stored in the keyring by set_logins.py
        try:
            from set_logins import get_ftp_logins
            self.addr, self.path, self.user, self.passwd = get_ftp_logins()
        except Exception as e:
            raise ValueError(f"FTP parameters not found in keyring ({type(e).__name__}).")
        return

    def get_from_environment(self, prefix='OWI_FTP_'):
        import os
        self.addr = os.getenv(prefix + 'ADDRESS', self.addr)
        self.path = os.getenv(prefix + 'PATH', self.path)
        self.user = os.getenv(prefix + 'USERNAME', self.user)
        self.passwd = os.getenv(prefix + 'PASSWORD', self.passwd)

        if None in (self.addr, self.path, self.user, self.passwd):
            # reset to None if any are missing
            self.addr = None
            self.path = None
            self.user = None
            self.passwd = None
            raise ValueError("FTP parameters not fully set from environment variables.")
        return

    def get_from_user(self):
        import getpass
        self.addr = input("Enter the FTP address: ")
        self.path = input(f"Enter the FTP path:  {self.addr}/")
        self.user = input("Enter your FTP username: ")
        self.passwd = getpass.getpass(prompt=f'Enter password for ftp user "{self.user}": ')
        return

def RUN_download_cwi(C):
    # Look for the FTP parameters in the keyring,
    # then in environment variables,
    # and finally ask the user.
    params = ftp_params()
    try:
        params.get_from_keyring()
    except ValueError:
        logging.warning("Could not get FTP parameters from keyring. Trying environment variables.")
        try:
            params.get_from_environment()
        except ValueError:
            logging.warning("Could not get FTP parameters from environment variables. Asking user.")
            params.get_from_user()

    logging.debug("RUN_download_cwi()")
    logging.debug(versioninfo(C))
    
    logging.debug(f"OWI_DOWNLOAD_DIR = {C.OWI_DOWNLOAD_DIR}")
    logging.debug(f"OWI_DOWNLOAD_WELLSSHP_DIR = {C.OWI_DOWNLOAD_WELLSSHP_DIR}")
    logging.debug(f"OWI_DOWNLOAD_FILES = {C.OWI_DOWNLOAD_FILES}")
           
    # ftpaddr, ftppath, ftpuser, ftppass = L.get_ftp_logins('CWI_ftp', None)
    newfiles = download_cwi_from_ftp(
        ftpaddr = params.addr,
        ftppath = params.path,
        ftpuser = params.user, 
        ftppass = params.passwd,
        downloadpath = C.OWI_DOWNLOAD_DIR,
        downloadshppath = C.OWI_DOWNLOAD_WELLSSHP_DIR,
        downloadfiles = C.OWI_DOWNLOAD_FILES) 
    print ('New files created:\n   ' + '\n   '.join(newfiles))
    return newfiles


if __name__ == '__main__':
    from OWI_config import OWI_version_40 as C
    RUN_download_cwi(C)  
    
    print ('\n///////////// DONE ///////////////')