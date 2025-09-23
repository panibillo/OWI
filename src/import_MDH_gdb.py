'''
Created on Jan 10, 2023

@author: bill

The purpose of this module is to create a database table of names and locations 
of wells that have been sealed but have not been entered in CWI.  

The means is by obtaining a copy of a GIS layer used by MDH Well Management that
includes those wells.  That layer:
    -   may have significant overlap with wells that are already in CWI.  
    -   does not have wellids
    -   cannot have wellids for wells not in CWI
    -   has a number of fields of unknown definition or unknown data quality.
The target shapefile has only been obtained from MDH Well Management one time, 
and by special request, so it is not guaranteed that the methods programmed in
this module will again run.

Method Run_analyze_Hnums is a work in progress. The ultimate intent is to 
automatically merge the sealing records into CWI:
    -   add sealing identifiers as needed to existing well records, and 
    -   add new well records to CWI tables for wells not yet entered in CWI. 

It is assumed that the GIS layer is in the form of a shape file.
It is assumed that the fields match the fields that are named in method:
    add_fields_to_MDHsealed()
  
'''
import datetime
import os
import shapefile

from OWI_sqlite import c5db, MNU_FORMAT, RELATEID_FORMAT

from OWI_config import OWI_version as C

if 1:
    DB_NAME = C.OWI_DOWNLOAD_DB_NAME
    TABLENAME = 'MDHsealed'
elif 1:
    DB_NAME = os.path.expanduser('~/R/cwi/OWI40_S.sqlite')
    TABLENAME = 'MDHsealed'
elif 0:
    DB_NAME = os.path.expanduser('~/data/MN/OWI/OWI40.sqlite')
    TABLENAME = 'MDHsealed'
print (f"USING DB_NAME: {DB_NAME}. Exists = {os.path.exists(DB_NAME)}")
print (f"USING Table : {TABLENAME}")

def isint(val):
    """
    Return True if val represents an integer (either numeric or text)
    """
    try:
        i = int(val)
        return True
    except:
        return False

    
def shp_generator(shpname):
    """
    Yield next row from a shapefile's attribute table as a tuple.
    
    The first column in a shapefile is an internal flag that is not of interest.
    The order and values of all other columns are preserved
    
    Returns
    -------
    tuple : (irec, UTME, UTMN, <all attribute fields ...>)
    """
    assert os.path.exists(shpname), f"Shape file not found {shpname}."

    with shapefile.Reader(shpname) as shpf: 
        s = shpf.shapes()
        n = len(s)
        keys = tuple((f[0] for f in shpf.fields[1:]))
        nullrecord = [None for k in keys]

        for i in range(n):
            try:
                s = shpf.shape(i)
                x,y = s.points[0][0], s.points[0][1] 
            except:
                x,y = None, None
            try:
                r = shpf.record(i)
                rec = tuple([i+1, x, y] + [r[k] for k in keys])
            except:
                rec = tuple([i+1, x, y] + nullrecord)
            yield rec

def RUN_import_sealings():    
    """
    Obtain geodatabase from MDH Well Management of Sealed wells & disclosures
    
    Extract the compressed geodatabase to its folder
    Run the GDAL conversion program on the command line:
        ogr2ogr geos_sealed_wells.shp  geos_sealed_wells.gdb 
        (i.e. ogr2ogr <destfile.ext> <sourcefile.ext>)
    Then run this routine to bring the shape file into sqlite
    
    If this does not work, see version in OWI_import_csv.py, prior to Nov/2023
    """
    # import chardet
    shpname = os.path.expanduser("~/data/MN/MDH/shp/geos_sealed_wells.shp")
    print (shpname)
    assert os.path.exists(shpname)
    assert os.path.exists(DB_NAME)

    db = c5db()
    if not os.path.exists(shpname):
        print (f"shapefile '{shpname}' not present for import to db")
        return
    
    # Peek into the shapefile to get the column names.
    # Change the name of column 1 to 'cwi_loc'
    d = {'D':'DATE',
         'N':'INT',
         'C':'TEXT'}
    with shapefile.Reader(shpname) as shpf: 
        cols    = ['irow','UTME','UTMN'] + [f[0]  for f in shpf.fields[1:]]
        coldefs = ['irow INT','UTME REAL','UTMN REAL'] \
                + [f"{f[0]} {d[f[1]]}" for f in shpf.fields[1:]]
        keys = tuple((f[0] for f in shpf.fields[1:]))
    
    # from chardet.universaldetector import UniversalDetector
    # 
    # detector = UniversalDetector()
    # detector.reset()
    # for line in open(shpname, 'rb'):
    #     detector.feed(line)
    #     if detector.done: break
    # detector.close()
    # print(detector.result)
    
    # return 
    # with shapefile.Reader(shpname) as shpf: 
    #     cols = tuple(['cwi_loc'] + [f[0] for f in shpf.fields[1:]])
    #     for f in shpf.fields:
    #         print (f)
    qmarks = db.qmarks(cols)
    cols = ', '.join(cols)
    cols = cols.replace('UNIQUE,','UNIQUE_NO,').replace('RANGE,','RNG,').replace('NAME,','ONAME,')
    coldefs = ', '.join(coldefs)
    coldefs = coldefs.replace('UNIQUE ','UNIQUE_NO ').replace('RANGE ','RNG ').replace('NAME ','ONAME ')
    
    delete = f"""DROP TABLE IF EXISTS MDHsealed;"""
    create = f"""CREATE TABLE IF NOT EXISTS MDHsealed(
                 {coldefs});"""
    
    insert = f"""insert into MDHsealed (
                 {cols}
                 ) values ({qmarks});""".replace('                 ','  ')
    print (create)
    print ('begin: ',insert)
    # return
    with c5db(db_name=DB_NAME, commit=True) as db:
        db.query(delete)
        db.query(create)
        with shapefile.Reader(shpname) as shpf: 
            db.cur.executemany(insert, shp_generator(shpname))
            
            # for x in shpf.iterShapes():
            #     print (x.points)
            #     break
            # s = shpf.shapes()
            # n = len(s)
            # errcount = 0
            # for i in range(n):
            #     try:
            #         r = shpf.record(i)
            #         print (r)
            #         return
            #     except Exception as e:
            #         print(f'+++ERROR AT {i}: {e}')
            #         errcount += 1
            #         # r = shpf.record(i)
            #         # print (r)
            # print ('errcount = ', errcount, '  out of',n)        
            # return
            #
            # for x in shpf.iterRecords():
            #     print (x, dir(x))
            # for srec in shpf.iterShpR:
            #     vals = tuple([srec.record[k] for k in keys])
            #     try:
            #         db.cur.execute(insert, vals) 
            #     except Exception as e:
            #         print (vals)
            #         print (e)
        #db.query(create)
        #db.cur.executemany(insert, shp_generator(shpname))
    print (f'completed import of shapefile {shpname}')


def add_fields_to_MDHsealed(db_name):
    """
    Add 3 fields to the MDH_sealed_table.
    
    DO NOT run with commit = False, the data is likely to be deleted.
    """
    queries = """
    PRAGMA foreign_keys = 0;
    @
    CREATE TABLE MDHsealed_temp_table AS SELECT *
                                              FROM MDHsealed;
    @
    DROP TABLE MDHsealed;
    @
    CREATE TABLE MDHsealed (
        irow       INT,
        wellid     INT,
        MNUNIQ     TEXT,
        WMWSR      TEXT,
        Hcandidate TEXT,
        mmid       INTEGER,
        idflag     INTEGER,
        UNIQUE_NO  TEXT,
        RELATEID   TEXT,
        UTMN       REAL,
        UTME       REAL,
        WELL_SNUM  INT,
        REP_STAT   TEXT,
        SEALED_D   DATE,
        ENTRY_D    DATE,
        SEAL_DEP   INT,
        SEAL_CAS   INT,
        OTHER_WELL TEXT,
        NOTES      TEXT,
        SEAL_ID    TEXT,
        WELL_LABEL TEXT,
        LOC_ID     INT,
        ONAME      TEXT,
        ADDR       TEXT,
        CITY       TEXT,
        STATE_ABB  TEXT,
        ZIP5_CODE  TEXT,
        LOC_DESC   TEXT,
        COUNTY_C   INT,
        TOWNSHIP   INT,
        TOWN_DIR   TEXT,
        RNG        INT,
        RANGE_DIR  TEXT,
        SECT       INT,
        SUBSECT    TEXT,
        PIN        TEXT,
        STATUS_C   TEXT,
        LCM_CODE   TEXT,
        DBNAME_ABB TEXT,
        ACCURACY   INT,
        GEOC_DATE  DATE,
        COMMENTS   TEXT
    );
    @
    INSERT INTO MDHsealed (
        irow,
        UNIQUE_NO,
        RELATEID,
        UTMN,
        UTME,
        WELL_SNUM,
        REP_STAT,
        SEALED_D,
        ENTRY_D,
        SEAL_DEP,
        SEAL_CAS,
        OTHER_WELL,
        NOTES,
        SEAL_ID,
        WELL_LABEL,
        LOC_ID,
        ONAME,
        ADDR,
        CITY,
        STATE_ABB,
        ZIP5_CODE,
        LOC_DESC,
        COUNTY_C,
        TOWNSHIP,
        TOWN_DIR,
        RNG,
        RANGE_DIR,
        SECT,
        SUBSECT,
        PIN,
        STATUS_C,
        LCM_CODE,
        DBNAME_ABB,
        ACCURACY,
        GEOC_DATE,
        COMMENTS
    )
    SELECT irow,
        UNIQUE_NO,
        RELATEID,
        UTMN,
        UTME,
        WELL_SNUM,
        REP_STAT,
        SEALED_D,
        ENTRY_D,
        SEAL_DEP,
        SEAL_CAS,
        OTHER_WELL,
        NOTES,
        SEAL_ID,
        WELL_LABEL,
        LOC_ID,
        ONAME,
        ADDR,
        CITY,
        STATE_ABB,
        ZIP5_CODE,
        LOC_DESC,
        COUNTY_C,
        TOWNSHIP,
        TOWN_DIR,
        RNG,
        RANGE_DIR,
        SECT,
        SUBSECT,
        PIN,
        STATUS_C,
        LCM_CODE,
        DBNAME_ABB,
        ACCURACY,
        GEOC_DATE,
        COMMENTS
    FROM MDHsealed_temp_table;
    @
    DROP TABLE MDHsealed_temp_table;
    @
    PRAGMA foreign_keys = 1;
    """
    
    # DO NOT run with commit = False, bad things can happen.
    with c5db(db_name, open_db=True, commit=True) as db:
        if 'wellid' in db.get_column_names('MDHsealed'):
            print (f'It appears fields are already added to db:\n  {db_name}')
            return
        for i,s in enumerate(queries.split('@')):
            line1 = s.split('\n')[1]
            print (f"Run query sequence {i}: {line1} ...")
            db.query(s)
    print (f'Table MDHsealed modified in {db_name}')    


def RUN_analyze_Hnums(db_name, commit=False):
    """
    Sequentially process the MDHsealed table, build relations to cwi tables.
    
    Critical identifier fields include:
    wellid, MNUNIQ, SEAL_ID, RELATEID, UNIQUE_NO
        wellid      to be filled. H-records missing from cwi assigned 8B nums.
        MNUNIQ      MNU : convert to std format
        SEAL_ID     MNU : convert to std format
        RELATEID    10 char, missing for H-numbers only. Generate from wellid
        UNIQUE_NO   10 char format, uses 'H000123456' for H nums
    """
    assert os.path.exists(db_name)
    if 0: add_fields_to_MDHsealed(db_name)
 
    MDHsealed = TABLENAME
    print (TABLENAME)
    # reformat H-numbers in columns 
    s1 = f"""UPDATE {MDHsealed} 
             SET MNUNIQ = MNU_FORMAT(Unique_no, 'ERROR')
             WHERE Unique_no IS NOT NULL;"""
    s2 = f"""UPDATE {MDHsealed} 
             SET WMWSR = MNUNIQ
             WHERE MNUNIQ LIKE('H%');"""
    # s3 = f"""UPDATE o1id 
    #          SET IDENTIFIER = MNU_FORMAT(IDENTIFIER, IDENTIFIER)
    #          WHERE ID_PROG in ('MNUNIQ', 'WMWSR');"""
    # s4 = f"""UPDATE o1id 
    #          SET IDENTIFIER = MNU_FORMAT(IDENTIFIER, IDENTIFIER)
    #          WHERE ID_PROG in ('WSERIES');"""
    with c5db(db_name, open_db=True, commit=commit) as db:
        return
        print ('tables = ', db.get_tablenames())
        n = db.query(f"select count(*) from {MDHsealed}")
        print (f"n = {n}")
        if 1:
            s1 = f"""UPDATE {MDHsealed} 
                     SET MNUNIQ = MNU_FORMAT(Unique_no, 'ERROR')
                     WHERE Unique_no IS NOT NULL;"""
            s1 = f"""UPDATE {MDHsealed} 
                     SET MNUNIQ = MNU_FORMAT(MNUNIQ, MNUNIQ)
                     WHERE MNUNIQ IS NOT NULL;"""
            s2 = f"""UPDATE {MDHsealed} 
                     SET WMWSR = MNU_FORMAT(WMWSR, WMWSR)
                     WHERE WMWSR IS NOT NULL;"""
            # s3 = f"""UPDATE o1id 
            #          SET IDENTIFIER = MNU_FORMAT(IDENTIFIER, IDENTIFIER)
            #          WHERE ID_PROG in ('MNUNIQ', 'WMWSR');"""
            # s4 = f"""UPDATE o1id 
            #          SET IDENTIFIER = MNU_FORMAT(IDENTIFIER, IDENTIFIER)
            #          WHERE ID_PROG in ('WSERIES');"""
            db.query(s1)
            db.query(s2)
            # db.query(s3)
            # db.query(s4)
        if 0:
            s1 = f"""UPDATE {MDHsealed} 
                     SET Hcandidate = MNU_FORMAT(Hcandidate, Hcandidate)
                     WHERE Hcandidate is not null;"""
            db.query(s1)
        if 0:
            s1 = f"""select B.utme, B.utmn, A.rowid 
                    from {MDHsealed} A
                    left join MDHsealed2 B
                      on A.rowid = B.rowid
                    where B.WELL_SNUM is  null;"""
            s2 = f"""select B.utme, B.utmn, A.rowid 
                    from {MDHsealed} A
                    left join MDHsealed2 B
                      on A.WELL_SNUM = B.WELL_SNUM
                    where B.WELL_SNUM IS NOT NULL;"""
            u0 = f"""update {MDHsealed}
                    set UTME= ?, UTMN=? 
                    where rowid = ?""" 
            for row in db.query(s1):
                db.query(u0, row)
            for row in db.query(s2):
                db.query(u0, row)
        
        if 0: # reinitialize wellids
            s0 = f"UPDATE {MDHsealed} SET wellid = NULL;"
            db.query(s0)
        
        if 0: # 1st pass match wellids
            s1 = f"""SELECT I.wellid, S.rowid  --38,229
                     FROM {MDHsealed} S
                     LEFT JOIN v1idu I
                       ON S.MNUNIQ = I.IDENTIFIER
                    WHERE I.IDENTIFIER IS NOT NULL;""" 
            u1 = f"""UPDATE {MDHsealed}
                     SET wellid = ?, mmid = 50
                     WHERE rowid = ?;"""
            data = db.query(s1)
            for row in data:
                db.query(u1, row)
        if 0: # 2nd pass
            s1 = f"""select I.wellid, A.rowid -- 17
                       from {MDHsealed} A
                       left join o1id I
                         on A.MNUNIQ = I.IDENTIFIER
                       where A.wellid is null 
                         AND i.WELLID IS NOT NULL;"""  
            u1 = f"""UPDATE {MDHsealed}
                     SET wellid = ?, mmid = 51
                     WHERE rowid = ?;"""    
            for row in db.query(s1):
                db.query(u1, row)
        if 0: # Flagging duplicate wellids: 
            s1 = f"""select A.rowid, B.rowid, A.MNUNIQ, B.MNUNIQ  -- 154 records
                   from {MDHsealed} A
                   left join MDHsealed B
                   on A.wellid = B.wellid
                   where A.MNUNIQ > B.MNUNIQ
                   order by A.MNUNIQ;"""
            u1 = f"""Update {MDHsealed}
                    set mmid = 52, mplan = 'ignore record'
                    where rowid = ?"""
            for row in db.query(s1):
                rowidB = row[1]
                db.query(u1, (rowidB,))  
        if 0: # create wellid numbers for regular MNUs not in CWI (not H numbers)
            u1 = f"""update {MDHsealed} -- 1849
                       set wellid = cast(MNUNIQ as Integer), mmid = 56
                       where NOT MNUNIQ like ('H%') 
                         and wellid is null;"""
        if 0: # create 8B numbers for H-records not in CWI
            u1 = f"""update {MDHsealed}  -- 222534 records
                     set wellid = 8000000000 + cast(substr(MNUNIQ, 2) AS INTEGER),
                     mmid = 58
                     where wellid is null 
                       and mmid is null;"""
            u2 = f"""update {MDHsealed} -- 220685
                     set RELATEID = cast(wellid as text)
                     where mmid = 58 and RELATEID is NULL;""" 
            u3 = """update MDHsealed  --4035
                     set RELATEID = substr('000000000'||cast(wellid as string),-10)
                     where RELATEID is NULL 
                       and wellid is not null;"""
            db.query(u1)
            db.query(u2)
            db.query(u3)
            
        if 0: # data cleanup
            u1 = """update MDHsealed -- 331 Records with long datetime in GEOC_DATE
                    set GEOC_DATE = substr(GEOC_DATE,0,11) 
                    where length(GEOC_DATE) > 10;"""
            db.query(u1)
            
            
        if 0: # Append records to c5 tables and o1id
            uu = """insert into c5ix  -- 222534
                          (wellid, owi_remark, UNIQUE_NO, RELATEID, STATUS_C, COUNTY_C, TOWNSHIP, [RANGE], RANGE_DIR, SECTION, SUBSECTION, LOC_MC  , LOC_SRC)
                    select wellid,'MDHsealed', MNUNIQ   , RELATEID, STATUS_C, COUNTY_C, TOWNSHIP, RNG    , RANGE_DIR, SECT   , SUBSECT   , LOC_DESC,'WM_gdb'
                    from MDHsealed 
                    where mmid in (56,58);
                    @
                    insert into c5locs  -- 222534
                          (wellid, CWI_loc   , UNIQUE_NO, RELATEID, STATUS_C, COUNTY_C, TOWNSHIP, [RANGE], RANGE_DIR, SECTION, SUBSECTION, LOC_MC  , LOC_SRC, UTME, UTMN, GEOC_DATE, WELL_LABEL)
                    select wellid,'MDHsealed', MNUNIQ   , RELATEID, STATUS_C, COUNTY_C, TOWNSHIP, RNG    , RANGE_DIR, SECT   , SUBSECT   , LOC_DESC,'WM_gdb', UTME, UTMN, GEOC_DATE, MNUNIQ
                    from MDHsealed 
                    where mmid in (56,58);
                    @
                    insert into c5ad ---222534 (Concatination works because fields use "" rather than NULL)
                          (wellid, owi_remark, RELATEID, OTHER)
                    select wellid,'MDHsealed', RELATEID, ADDR||'|'||CITY||'|'||STATE_ABB||'|'||PIN  
                      FROM MDHsealed 
                      WHERE mmid in (56,58);
                    @
                    insert into c5rm -- 18617
                          (wellid, owi_remark, RELATEID, SEQ_NO, REMARKS)
                    select wellid,'MDHsealed', RELATEID,      1, COMMENTS 
                      FROM MDHsealed 
                      WHERE mmid in (56,58)
                        AND COMMENTS >' ';
                    @
                    insert into o1id  -- 1849
                          (wellid, RELATEID, IDENTIFIER, MNU, sMNU, ID_TYPE, ID_PROG, mmid,mexplain,mplan,mresolved, mremark)
                    select wellid, RELATEID, MNUNIQ    ,   1,    1,'WM_gdb','MNUNIQ', mmid,mexplain,mplan,mresolved,'MDHsealed' 
                      FROM MDHsealed 
                      WHERE mmid in (56);
                    @
                    insert into o1id --220685
                          (wellid, RELATEID, IDENTIFIER, MNU, sMNU, ID_TYPE, ID_PROG, mmid,mexplain,mplan,mresolved, mremark)
                    select wellid, RELATEID, MNUNIQ    ,   1,    1,'WM_gdb', 'WMWSR', mmid,mexplain,mplan,mresolved,'MDHsealed' 
                      FROM MDHsealed 
                      WHERE mmid in (58);
                    @
                    insert into c5rm -- 1105
                          (wellid, owi_remark, RELATEID, SEQ_NO, REMARKS)
                    select wellid, 'MDHsealed', RELATEID, Bseq_no, COMMENTS 
                       from MDHsealed A 
                       left join (SELECT wellid as Bwellid, (COALESCE(MAX(SEQ_NO), 0) + 1) as Bseq_no
                                  from c5rm
                                  group by wellid) AS B
                         on A.wellid = B.Bwellid 
                       where A.mmid < 56
                         and A.COMMENTS >' '
                         and B.Bseq_no is not null;
                    @
                    insert into c5rm -- 28
                          (  wellid,  owi_remark,   RELATEID, SEQ_NO,   REMARKS)
                    select A.wellid, 'MDHsealed', A.RELATEID, 1     , A.COMMENTS 
                       from MDHsealed A 
                       left join c5rm B
                         on A.wellid = B.wellid 
                       where A.mmid < 56
                         and A.COMMENTS >' '
                         and B.wellid is null;""".replace('                    ','')
            for i,u in enumerate(uu.split('@')):
                print (f"Run query sequence {i} ...")
                db.query(u)

# def RUN_updatefromjoin():
#     """
#     After creating the joinednulls table, append those records to MDHsealed.
#
#     This just matches up the column names and generates the insert statement.
#     """
#     with c5db(db_name=DB_NAME, open_db=True, commit=False) as db:
#         srccols = db.get_column_names('joinednulls')
#         destcols = db.get_column_names('MDHsealed')
#         colmap = {}
#         incols = []
#         outcols = []
#         for dc in destcols: 
#             for sc in srccols:
#                 if sc.upper().endswith(dc.upper()):
#                     colmap[sc] = dc
#                     incols.append(f'[{sc}]')
#                     outcols.append(dc)
#                     break
#         for key, val in colmap.items():
#             print (key, val)
#         insert = f"""insert into MDHsealed
#                 {', '.join(outcols)}
#                 select  
#                 {', '.join(incols)} 
#                 from joinednulls;""".replace('               ','')
#         print (insert)
#
# def Hformat(Hnum):
#     rv = f"H{int(Hnum[1:]):d}"
#     return rv
# def RUN_analyze_Hnums():
#     s1 = r"""select rowid, WELL_LABEL, SEAL_ID, NOTES 
#             from MDHsealed
#             where Hcandidate is NULL 
#               and NOTES REGEXP '\W*\bWAS H[ -]?\d{5,9}\W*';"""
#     u1 = """UPDATE MDHsealed SET Hcandidate = ?, BO_remark = 'H1'where rowid = ?;"""
#     db_name=DB_NAME
#     db_name=os.path.expanduser("~/data/MN/OWI/OWI40.sqlite")
#     with c5db(db_name=db_name, open_db=True, commit=False) as db:
#         data = db.query(s1)
#         print (s1)
#         print (len(data))
#         icount = 0
#         for row in data:
#             rowid, wlabel, sealid, notes = row
#             w = notes.upper().replace(',',' ').replace('-',' ').replace('/',' ').replace('(',' ').split()
#             if not 'WAS' in w:
#                 continue
#             n = w.index('WAS')
#             print (row)
#             if (len(w) >= n+1
#                 and w[n] == 'WAS'
#                 and w[n+1][0] == 'H'
#                 and isint(w[n+1][1:])):
#                 H = Hformat(w[n+1])     #MNU_FORMAT(w[n+1], default_val=w[n+1])
#                 print (u1, (H, rowid), row)
#                 db.query(u1, (w[1], rowid))
#                 icount += 1
#     #print (s1)
#     print (len(data), icount)
        
if __name__=='__main__':
    # print (DB_NAME)
    if 0:
        RUN_import_sealings()
    if 0:
        add_fields_to_MDHsealed()
    if 0:
        #from process_MDHsealed import RUN_analyze_Hnums
        RUN_analyze_Hnums(db_name=DB_NAME, commit=False)
    
print (r'\\\\\\\\\\\\ DONE import_MDH_gdb.py //////////////')
