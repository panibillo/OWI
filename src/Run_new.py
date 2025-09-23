"""
A driver to create a fresh local copy of cwi from scratch

Purpose
-------
    o   Create an all new sqlite database to mirror the CWI database as served   
        on the Minnesota Geologic Survey ftp site as the c5 data tables
    o   Download selected .zip files if the ftp site versions are newer
    o   Unzip any newer .zip files that have been downloaded
    o   Create or re-create the target sqlite database using a specified schema 
    o   Import the unzipped data to the sqlite database
Authors
-------
    William C. Olsen
    panibillo at gmail.com
    
Version
-------
    2021-10-14
"""
import os
from OWI_download_ftp import RUN_download_cwi
from OWI_import_csv import RUN_import_csv, RUN_import_swuds

from OWI_config import  OWI_version as C
if os.path.exists(C.OWI_DOWNLOAD_DB_NAME):
    raise NotImplementedError (f"WARNING: the file should not exist before running:\n{C.OWI_DOWNLOAD_DB_NAME}")
    

if 0: RUN_download_cwi()
RUN_import_csv()

if 0: RUN_import_swuds()

print ("/////////// DONE with Run_new.py ////////////")
