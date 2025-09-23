'''
Created on Oct 10, 2020

NOTES
2025-09-21
    Realized that latest ftp download was not refreshing .csv files.
    But rather was refreshing .txt files.  Confirmed that .txt are formatted 
    identically as csv, though not sorted the same.
    
    Therefor introduced global config variable 
        OWI_config: OWI_DOWNLOAD_CWIDATACSV_EXT = '.txt' or'.csv'

@author: Bill
'''
import csv
import datetime
import os
import shapefile

from OWI_sqlfile import execute_statements_from_file
from OWI_sqlite import c5db

from OWI_config import OWI_version as C
from OWI_config import SWUDS_version_0 as S
from OWI_config import versioninfo

CSVEXT = C.OWI_DOWNLOAD_CWIDATACSV_EXT
"""
2025-09-21 new formatting notes:
    - c5 is the new data table prefix
    - txt is the current data table extension.  (csv files appear to be not maintained)
    - All files contain useless 'objectid' in column 1: ignore column 1
    - Most files contain useless empty c5xx_seq_no in column 2: ignore seq_no 
    - Most files contain wellid as last column.
    - Column names in c5 txt file headers are NOT capitalized, but otherwise 
      are identical to c4 column names with a few additions, and with moving the
      wellid column around.
    - TBD whether the wellid column is fully reliable.
"""
TXT_HEADS = {
"c5ad" : """objectid,c5ad_seq_no,relateid,name,addtype_c,house_no,street,
 road_type,road_dir,city,state,zipcode,entry_date,updt_date,other,wellid""",
"c5an" : """objectid,c5an_seq_no,relateid,azimuth,inclin,ang_depth,wellid""",
"c5c1" : """objectid,relateid,drill_meth,drill_flud,hydrofrac,hffrom,hfto,
 case_mat,case_joint,case_top,drive_shoe,case_type,screen,ohtopfeet,ohbotfeet,
 screen_mfg,screen_typ,ptlss_mfg,ptlss_mdl,bsmt_offst,csg_top_ok,csg_at_grd,
 plstc_prot,disinfectd,pump_inst,pump_date,pump_mfg,pump_model,pump_hp,
 pump_volts,dropp_len,dropp_mat,pump_cpcty,pump_type,variance,drllr_name,
 entry_date,updt_date,wellid""",
"c5c2" : """objectid,c5c2_seq_no,relateid,constype,from_depth,to_depth,diameter,
 slot,length,material,amount,units,wellid""",
"c5id" : """objectid,c5id_seq_no,relateid,identifier,id_type,id_prog,wellid""",
"c5ix" : """objectid,relateid,county_c,unique_no,wellname,
 township,range,range_dir,section,subsection,mgsquad_c,
 elevation,elev_mc,status_c,use_c,loc_mc,loc_src,data_src,
 depth_drll,depth_comp,date_drll,case_diam,case_depth,grout,
 pollut_dst,pollut_dir,pollut_typ,
 strat_date,strat_upd,strat_src,strat_geol,strat_mc,
 depth2bdrk,first_bdrk,last_strat,ohtopunit,ohbotunit,aquifer,
 cuttings,core,bhgeophys,geochem,waterchem,obwell,swl,dh_video,input_src,
 unused,entry_date,updt_date,geoc_type,gcm_code,geoc_src,geoc_prg,utme,utmn,
 geoc_entry,geoc_date,geocupd_entry,geocupd_date,rcvd_date,well_label,wellid,
 swlcount,swldate,swlavgmeas,swlavgelev,bdrkelev,ohtopelev,ohbotelev,botholelev,
 logurl,straturl""",
"c5pl" : """objectid,c5pl_seq_no,relateid,pumptestid,test_date,start_meas,
 flow_rate,duration,pump_meas,wellid""",
"c5rm" : """objectid,c5rm_seq_no,relateid,seq_no,remarks,wellid""",
"c5st" : """objectid,c5st_seq_no,relateid,depth_top,depth_bot,drllr_desc,
 color,hardness,strat,lith_prim,lith_sec,lith_minor,wellid,concat,
 stratcode_gen,stratcode_detail""",
"c5wl" : """objectid,c5wl_seq_no,relateid,meas_type,meas_date,meas_time,
 m_pt_code,meas_point,measuremt,meas_elev,data_src,program,entry_date,updt_date,
 wellid""",
}


""" 
Simple type checking, type converting, and text cleaning functions.
These are used for importing .csv files, and assume that the data in the .csv
files will conform to the anticipated data types.  No warnings or error messages
will be generated.
"""
DEFAULTWELLID = 9000000000
def safewellid(x):
    global DEFAULTWELLID
    try:
        val = int(x)
        assert val > 0
    except Exception as e:
        val = DEFAULTWELLID + 1
        print (f"++++ Assigning defualt wellid {val} to {x}.  {e}")
        DEFAULTWELLID += 1
    return val
    
def safeint(x):
    """
    A simple type check for integer: return x if int else None
    """
    try:    return int(x)
    except: return None
def safefloat(x):
    """
    A simple type check for float: return x if float else None
    """
    try:    return float(x)
    except: return None
def safetext(x):
    """
    A simple type check for text: return x if text else None
    """
    try:   
        rv = x.strip()
        if not rv:
            return None
        return rv
    except: 
        return None
class safedate():
    """
    A simple type check for date type: return x as date if possible, else None
    """
    def __init__(self, default='%m/%d/%Y'):
        self.fmt = default
        self.fmts = ( default,
                     '%m-%d-%Y',
                     '%Y/%m/%d',
                     '%Y-%m-%d',
                     '%Y%m%d')
    def date(self, x):
        """
        Return x as datetime if formatted as one of formats in self.fmts.
        
        Arguments:
        x : str
        
        Try to convert string x to a date using format self.fmt
        If that fails, try the other formats in self.fmts. If one succeeds,
        store the successful format in self.fmt for use on the next call.
        """
        try:
            return datetime.datetime.strptime(x,self.fmt).date()
        except:
            for fmt in self.fmts:
                try:
                    d=datetime.datetime.strptime(x,fmt).date()
                    self.fmt = fmt
                    return d
                except:
                    pass
        return None

def get_col_names_and_converters(db, table_name, csv_cols):
    """ 
    Return a list of column names, and a dict of type converter functions.
    
    Arguments
    ---------
    db: open SQLite database with open cursor
    table_name: str, a table that exists in the db
    csv_cols: iterable, list of column names
    
    Only include columns appearing in BOTH the table def and in csv_cols. 
    The csv DictReader method is case sensitive to the column names as entered
    in the csv file, while the sql queries are not case sensitive to the column 
    names.  Returned column names must match the case in csv_cols.
    
    Beginning 2025-09 observe changes in source file structure.
    Common changes:
        Columns 1 and 2 are  [objectid, c5xx_seq_no,]  neither of use.
        Wellid is moved to the final column
    Special cases:
        c5ix, c5st: wellid column is not at the end
        
    """
    data = db.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall() 
    utbl_cols = [c[1].upper() for c in data]
    ucol_types = [c[2].upper() for c in data]
    ucsv_cols = [c.upper() for c in csv_cols]
    col_names, dcol_func = [], {}

    for N,T in zip(utbl_cols, ucol_types):
        if not N in ucsv_cols:
            continue
        n = csv_cols[ucsv_cols.index(N)] 
        col_names.append(n)   
        if N == 'WELLID':
            dcol_func[n] = safewellid
        elif T[:4] == 'INTE':
            dcol_func[n] = safeint
        elif T == 'REAL':
            dcol_func[n] = safefloat
        elif T == 'TEXT':
            dcol_func[n] = safetext
        elif T == 'CHAR':
            dcol_func[n] = safetext
        elif T == 'DATE':
            dcol_func[n] = safedate().date
        else:
            raise NotImplementedError(f'type {T} is not implemented for table {table_name} in column {n}')
    return col_names, dcol_func

def csv_generator(csvname, col_names, colfunc):
    """ 
    Yield next line from csv file as a tuple of type converted values
    
    Arguments:
    csvname   : Filename of an existing csv file to be read.
    col_names : Column names as entered in csv header (may be subset or reordered)
    col_func  : Dictionary of type conversion functions 
    
    Notes:
    -   The yielded values are ordered as in col_names.
    -   The yielded values are type converted using functions in colfunc.
    -   Both col_names and the keys used in col_func must match csv header  
        entries exactly, including case.
    """
    # with open(csvname, 'r', encoding='ascii') as datafile:
    with open(csvname, 'r') as datafile:
        reader = csv.DictReader(datafile)
        for line in reader:
            yield tuple(colfunc[col](line[col]) for col in col_names)

def csv_wellid_generator(csvname, col_names, colfunc, MNUcol='RELATEID'):
    """ 
    Yield next line from csv file as a tuple of type converted values
    
    Arguments:
    csvname   : Filename of an existing csv file to be read.
    col_names : Column names as entered in csv header (may be subset or reordered)
    col_func  : Dictionary of type conversion functions 
    
    Notes:
    -   The yielded values are ordered as in col_names.
    -   The yielded values are type converted using functions in colfunc.
    -   Both col_names and the keys used in col_func must match csv header  
        entries exactly, including case.
    -   Sets wellid to Null if the MNUcol cannot be converted to an integer. 
    """
    with open(csvname, 'r') as datafile:
        defaultid = 777000000
        reader = csv.DictReader(datafile)
        for line in reader:
            wellid = safeint(line[MNUcol], default=defaultid)
            if wellid == defaultid: 
                defaultid += 1
            yield tuple([wellid]+[colfunc[col](line[col]) for col in col_names])
         
def shp_locs_generator(shpname):
    """
    Yield next row from a shapefile's attribute table as a tuple.
    
    The first column in a shapefile is an internal flag that is not of interest.
    It is replaced with a text value of either 'loc' or 'unloc' depending on
    whether 'unloc' appears in shpname. 
      
    The order and values of all other columns are preserved
    
    The coordinates are not read from the shape, but are assumed entered 
    correctly in attribute fields.
    """
    if 'unloc' in shpname:
        cwi_loc = 'unloc'
    else:
        cwi_loc = 'loc'
    assert os.path.exists(shpname), f"Shape file not found {shpname}."

    with shapefile.Reader(shpname) as shpf: 
        keys = tuple((f[0] for f in shpf.fields[1:]))

        for srec in shpf:
            yield tuple([cwi_loc] + [srec.record[k] for k in keys])

class cwi_csvupdate():
    """ Methods for importing csv files into OWI database tables. """
    
    def __init__(self,
                 cwidatacsvdir,
                 locsdir):
        self.cwidatacsvdir = cwidatacsvdir
        self.locsdir = locsdir
        self.data_table_suffixes = 'ix id ad an c1 c2 pl rm st wl'.split()
        self.data_table_names = [f'c5{x}' for x in self.data_table_suffixes]
        self.locs_table_name = 'c5locs'

        assert os.path.exists(self.cwidatacsvdir), f"Missing {self.cwidatacsvdir}"
        assert os.path.exists(self.locsdir), f"Missing {self.locsdir}"
    
    def delete_table_data(self, db, 
                          tables=None):    
        """
        Delete all from the c5* data and locs tables. Preparing to import.
        
        Arguments
        ---------
        db     : an open database instance
        tables : either None, or a string including 'data' and/or 'locs' 
        """
        dodata = tables is None or 'data' in tables
        dolocs = tables is None or 'locs' in tables
        if dodata:
            for t in self.data_table_names:
                csvname = os.path.join(self.cwidatacsvdir, f'{t}{CSVEXT}')
                if not os.path.exists(csvname):
                    print(f'Missing {csvname}, Table {t} not refreshed')
                    continue
                db.query(f"DELETE FROM {t};")
            print ('data files emptied')
        if dolocs:
            for fname, val in(('wells.shp',       'loc'  ), 
                              ('unloc_wells.shp', 'unloc')):
                shpname = os.path.join(self.locsdir, fname)
                if os.path.exists(shpname):
                    db.query (f"DELETE FROM c5locs where cwi_loc = '{val}';",)
                    print (f"DELETE FROM c5locs where cwi_loc = '{val}';")
                else:
                    print(f'Missing {shpname}, {val} records not refreshed')
        db.commit_db()
        db.vacuum()
                 
    def import_data_from_csv(self, db, schema_has_constraints, 
                             table_names=None):    
        """ 
        Create c5 tables in an sqlite db, and read in data from csv files
 
        Notes
        ----- 
        Assumes that the csv files have already been downloaded and extracted.
            fullset/cwi_CSV.zip
        Assumes that data tables have been created.
        Skips any table that already has at least 1 record in it.
        Some details and steps will depend on the c5version selected, described
           below.
         
        schema_versions and constraints
        -------------------------------
        c5.0.# & c5.1.# define the tables exactly as MGS (except c5locs).
        c5.2.# & up add column wellid to every table.
        c5.3.# & up may put foreign key and unique constraints on the wellid
                 column, so the row generator must supply the wellid at the 
                 time that a record is created.
        """
        if table_names is None: 
            table_names = self.data_table_names 
            
        #table_names = ['c5ix', 'c5id', 'c5ad', 'c5an', 'c5c1', 'c5c2', 'c5pl', 'c5rm', 'c5st', 'c5wl', ]
        
        existing_tables = db.get_tablenames()

        for table_name in table_names:
            assert table_name in existing_tables, f'{table_name} missing from db'
            print (f'OK {table_name}')
            
            n = db.cur.execute(f"select count(*) from {table_name};").fetchone()[0]
            if n>0:
                print (f"skipping {table_name}, {n} records already in db.")
                continue
                        
            csvname = os.path.join(self.cwidatacsvdir, f'{table_name}{CSVEXT}')
            xlsname = csvname.replace(CSVEXT,'.xlsx')
            if os.path.exists(xlsname) and not os.path.exists(csvname):
                raise NotImplementedError
                # ok = xlsx_to_csv(xlsname, csvname)
            
            assert os.path.exists(csvname), csvname

            ok = self.force_to_ascii(csvname)
            
            with open(csvname, 'r') as f:
                headers = f.readline()
            csv_cols = headers.replace('"',' ').replace(',',' ').split()
         
            col_names, col_convert = get_col_names_and_converters(db, table_name, csv_cols)
            
            if schema_has_constraints and not 'WELLID' in headers.upper():
                insert = (f"INSERT INTO {table_name}\n"
                          f" (wellid, {', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks( len(col_names) + 1 )});")
                csvgen = csv_wellid_generator
            else:
                insert = (f"INSERT INTO {table_name}\n"
                          f" ({', '.join(col_names)})\n"
                          f" VALUES ({db.qmarks(col_names)});")
                csvgen = csv_generator
            print ('begin: ',insert)
            db.cur.executemany(insert, csvgen(csvname, col_names, col_convert))
            print (f"Completed table {table_name}") 
    

    def import_locs_from_csv(self, db, schema_has_constraints):
        """
        If locs is supplied as a csv file rather than shapefile(s), then read it
        in like the other data tables.
        """
        csvname = os.path.join(self.cwidatacsvdir, f'c5locs{CSVEXT}') 
        if os.path.exists(csvname):
            self.import_data_from_csv( db, schema_has_constraints, 
                                       table_names=('c5locs',) )
            print (f"c5locs table was imported from csv file: {csvname}")
            return True
        return False
      
    def import_cwi_locs(self, db):
        """
        Import the shapefiles into table c5locs. 
        
        There is one shapefile for located wells (wells.shp) and another for
        unlocated wells (unloc_wells.shp). Both are read into a single table,
        c5locs. Their origin  is distinguished by the value in a newly added
        column 'cwi_loc' with values of either 'loc' or 'unloc'.
        
        All columns defined in the shapefiles should have matching named columns
        in c5locs.

        The shapefiles have many columns that either reproduce data in c5ix
        or other tables, or summarize multiple values as a single value.
        """
        fnames = ['wells.dbf', 'unloc_wells.dbf']
        for fname in fnames:
            shpname = os.path.join(self.locsdir, fname)
            if not os.path.exists(shpname):
                print (f"shapefile '{shpname}' not present for import to db")
                continue
            
            # Peek into the shapefile to get the column names.
            # Change the name of column 1 to 'cwi_loc'
            with shapefile.Reader(shpname) as shpf: 
                cols = tuple(['cwi_loc'] + [f[0] for f in shpf.fields[1:]])
            qmarks = db.qmarks(cols)
            insert = f"""insert into {self.locs_table_name} (
                         {', '.join(cols)}
                         ) values ({qmarks});""".replace('                         ','  ')

            print ('begin: ',insert)
            db.cur.executemany(insert, shp_locs_generator(shpname))
            print (f'completed import of shapefile {shpname}')

    def populate_wellid_and_index(self, db, haslocs):
        """
        Set the wellid values in all data tables.
        The wellid values should also be equivalent to RELATEID.
        Table locs, if present, already has wellids.
        """
        table_names = list(self.data_table_names)
        if haslocs: table_names.append('c5locs')
        u = """UPDATE {tablename}
               set wellid = cast(RELATEID as integer)
               where wellid is null;""".replace('               ',' ')
        s = """create index if not exists idx_{tablename}_wellid 
               on  {tablename}(wellid);""".replace('               ',' ')
        for tablename in table_names:
            print (f'populating and indexing wellid in table {tablename} ...')
            db.query(u.format(tablename=tablename))
            db.query(s.format(tablename=tablename))
        print (f"Completed updating wellid in table {tablename}")

    def force_to_ascii(self, fname):
        """ 
        Remove any non-ASCII characters from the csv files.
        
        This is a crude fix that deletes information.  But experience shows that the
        only data affected in Dec 2021 was a single address with encoded '1/2' 
        symbol.
        """
        try:
            with open(fname, 'rb') as source_file:
                contents = source_file.read()
            with open(fname, 'w+b') as dest_file:
                dest_file.write(contents.decode('ascii','ignore').encode('ascii','ignore'))
            return True
        except Exception as e:
            print (f"Error forcing {fname} to ASCII")
            print (e)
            return False

def refresh_table(table_name):
    from OWI_sqlite import c5db 
    Cz = cwi_csvupdate( C.OWI_DOWNLOAD_CWIDATACSV_DIR,
                        C.OWI_DOWNLOAD_WELLSSHP_DIR)
    with c5db(db_name=C.OWI_DOWNLOAD_DB_NAME, commit=True) as db:
        if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = False')
 
        db.query(f"Delete from {table_name};")
        Cz.import_data_from_csv( db, C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS,
                                 table_names= [table_name])
        db.commit_db(msg='Imported data from csv files.')
        
        # Cz.import_data_from_csv(table_names = [table_name])
    
def RUN_import_csv(C,              # OWI_version
                   data=True, 
                   locs=True,
                   wellids=True,
                   resume_MNU_at = 0):
    """ 
    Demonstrate full import from csv files (and shape files). 
    Creates a new OWI.sqlite.  Does not update an existing OWI.sqlite

    Arguments
    ---------
        data :    boolean, default=True
                  Data tables are touched only if True
        
        locs :    boolean, default=True
                  locs table is touched only if True
        
        wellids:  boolean, default=True
                  wellids are created if OWI_SCHEMA_HAS_LOCS
                  unique numbers reformatted if OWI_REFORMAT_UNIQUE_NO
        
        resume_MNU_at: int, default=0
                  Resume processing at step n in OWI_MNU_INSERT
                  (n should be shown in prior output)
                
    Prerequisites
    -------------
        - OWI_config.py defined files and directories:
        - OWI_DOWNLOAD_DB_NAME        
            - must not exist or is completely empty of data tables.
        - OWI_DB_SCHEMA               must exist: named schema file.
        - OWI_DOWNLOAD_DIR            must exist: wells.shp and unloc_wells.shp 
        - OWI_DOWNLOAD_CWIDATACSV_DIR must exist: cwidata .csv files
        
    IMPORTANT!!!!!
    --------------
    -   If it runs incompletely or with errors, the final state may be faulty.
    -   If it runs incompletely or with errors, you can try to comment out
        sections below that have been complete in order to only run the 
        incomplete portions. The logic allows limited user control from this
        method, but does not recognize when steps have been completed.  For 
        example, reading in csv files twice will just create duplicate records.
    """
    from OWI_sqlite import c5db 

    if resume_MNU_at > 0:
        assert data == False, 'option data should be False if resum_MUN_at > 0'
        assert locs == False, 'option locs should be False if resum_MUN_at > 0'
        assert wellids == False, 'option wellids should be False if resum_MUN_at > 0'
       
    if C.OWI_SCHEMA_HAS_DATA_CONSTRAINTS:
        print('Warning. The CWI data files do not pass UNIQUE constaints')
        #raise NotImplementedError('Data constraints models are not implemented')

    Cz = cwi_csvupdate( C.OWI_DOWNLOAD_CWIDATACSV_DIR,
                        C.OWI_DOWNLOAD_WELLSSHP_DIR)
    
    create = not os.path.exists(C.OWI_DOWNLOAD_DB_NAME)
    
    print (f"Importing data to {C.OWI_DOWNLOAD_DB_NAME}")
    with c5db(db_name=C.OWI_DOWNLOAD_DB_NAME, commit=True) as db:
        
        if create: 
            print (f"creating tables, constraints, and views from {C.OWI_DB_SCHEMA}")
            execute_statements_from_file(db, C.OWI_DB_SCHEMA, verbose=True)

        if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = False')
 
        if data: 
            Cz.delete_table_data(db, 'data')
            Cz.import_data_from_csv( db, C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS)
            db.commit_db(msg='Imported data from csv files.')
        
        if locs and C.OWI_SCHEMA_HAS_LOCS: 
            Cz.delete_table_data(db,'locs')
            if not Cz.import_locs_from_csv(db, C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS):
                Cz.import_cwi_locs(db)
            db.commit_db(msg='Imported c5locs from files.')
        
        if wellids:
            if C.OWI_SCHEMA_HAS_WELLID:
                Cz.populate_wellid_and_index(db, C.OWI_SCHEMA_HAS_LOCS)
                db.commit_db(msg='Popula/home/bill/R/cwi/OWI40.sqliteted wellid in c5 data tables.')
            
            
            if C.OWI_REFORMAT_UNIQUE_NO:
                """ Removes leading 0's from identifiers in c5ix.UNIQUE_NO and
                    c5locs.UNIQUE_NO.  This is really optional.
                """
                print (f"OWI_REFORMAT_UNIQUE_NO: {C.OWI_REFORMAT_UNIQUE_NO}, data:{data}, locs:{locs}")
                if data:
                    db.update_unique_no_from_wellid('c5ix')
                    db.commit_db(msg='Reformatted unique_no in c5ix')
                if locs and C.OWI_SCHEMA_HAS_LOCS:
                    db.update_unique_no_from_wellid('c5locs')
                    db.commit_db(msg='Reformatted unique_no in c5locs')
 
        if C.OWI_SCHEMA_IDENTIFIER_MODEL == 'MNU':
            for sqlfiles in C.OWI_MNU_INSERT[resume_MNU_at:]:
                if not isinstance(sqlfiles, (list, tuple)):
                    sqlfiles = [sqlfiles]
                for sqlfile in sqlfiles:
                    execute_statements_from_file(db, sqlfile)
                    fname = os.path.basename(sqlfile)
                    db.commit_db(msg=f'MNU model commands: {fname}')
                # Resumat: (remember to set data, locs, wellids = False)
                #       0:  mnu_MNU_relationship_o1.1.1.sql
                #       1:  insert_c5locs_to_c5ix.sql
                #       2:  mnu_clean_c5id_o1.1.0.sql
                #       3:  mnu_reinit_o1id_o1.1.1.sql     
                #       4:  mnu_analyze_faults_o1.1.1.sql 
                #       5:  mnu_resolve_faults_o1.1.1.sql
        
        # if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS and C.OWI_SCHEMA_HAS_LOCS:
        #     Cz.append_c5locs_to_c5ix(db)
        #     db.commit_db()
            
        if C.OWI_SCHEMA_HAS_FKwellid_CONSTRAINTS:
            db.query('PRAGMA foreign_keys = True')


def import_swuds_full(self, db, csvname, table_name='r1ap_full'):
    """
    Import the swuds csv file into r1ap without modification.
    """
    existing_tables = db.get_tablenames()
    assert table_name in existing_tables,  f'{table_name} missing from db'

    assert os.path.exists(csvname), csvname
    with open(csvname, 'r') as f:
        headers = f.readline()
    csv_cols = headers.replace('"',' ').replace(',',' ').split()

    col_names, col_convert = get_col_names_and_converters(db, table_name, csv_cols)
    insert = (f"INSERT INTO {table_name}\n"
              f" (wellid, {', '.join(col_names)})\n"
              f" VALUES ({db.qmarks( len(col_names)+1 )});")
    
    db.cur.executemany(insert, csv_wellid_generator(csvname, col_names, col_convert, MNUcol = 'well_number'))
    print (f"Completed importing table {table_name}") 
    
    for u in ('update r1ap_full set unique_no = well_number;',
              'update r1ap_full set apid = rowid;' 
              ):
        db.query(u)
    print (f"Completed updating table {table_name}") 
        

def RUN_import_swuds(create=False):

    if 1:
        csvname = S.OWI_DOWNLOAD_APPROPRIATIONS_CSV
        db_name = C.OWI_DOWNLOAD_DB_NAME
    elif 0:
        # Testing
        csvname = r'F:\Bill\Workspaces\Py1\OWIsqlite\demo_data\mpars_demo.csv'
        db_name = r'F:\Bill\Documents\GW\CWI\c5db.sqlite'

    with c5db(db_name=db_name, commit=True) as db:
        if create:
            execute_statements_from_file(db, S.OWI_SWUDS_SCHEMA)
        import_swuds_full(db, csvname)


if __name__ == '__main__':
    print (versioninfo(C))
    RUN_import_csv(C)  # re-imports all tables from csv. 
    
    # RUN_import_csv(tables = 'data')
    # refresh_table('c5ix')
    # RUN_import_csv(data=False, 
    #                locs=False,
    #                wellids = False,
    #                resume_MNU_at=0)
    #RUN_import_swuds(create=True)
            
    print ('\n',r'\\\\\\\\\\\\\\\ DONE (OWI_import_csv.py) ///////////////')    
        
