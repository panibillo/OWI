'''
Created on Feb 2, 2023

@author: bill
'''
import datetime
import os
import shapefile

from OWI_sqlite import c5db

from OWI_config import  OWI_version as C

if 1:
    DBNAME = C.OWI_DOWNLOAD_DB_NAME
    TABLENAME = 'MDHsealed'
elif 1:
    DBNAME = os.path.expanduser('~/R/cwi/OWI40_S.sqlite')
    TABLENAME = 'MDHsealed'
elif 0:
    DBNAME = os.path.expanduser('~/data/MN/OWI/OWI40.sqlite')
    TABLENAME = 'MDHsealed'
print (f"USING DBNAME: {DBNAME}. Exists = {os.path.exists(DBNAME)}")
print (f"USING Table : {TABLENAME}")
# 
   
    


            
            
if __name__=='__main__':
    #RUN_import_sealings()
    #RUN_updatefromjoin()
    #RUN_analyze_Hnums(DBNAME, commit=False)
    db = c5db(db_name=DBNAME, open_db=True, commit=True)
    db.commit_db()
    db.close_db()
    
    
print (r'\\\\\\\\\\\\ DONE process_MDHsealed.py //////////////')
