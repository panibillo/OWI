'''
Created on Nov 25, 2023

Dependencies:
    Python >= 3.7
    
The purpose of this module is to scrape the CODE tables from the CWI website
Scraping is tricky for several reasons:
o   The html pages do not have parts clearly labeled so that we can easily
    recognize components of interest.
o   The formatting of components is inconsistent
o   Naming of fields contains some typos, not matching to actual db fields.
 
This module is not laid out as a class, but as distinct methods.
 
@author: bill
'''

from bs4 import BeautifulSoup, element
import requests
import csv
import json 
import os

from OWI_sqlite import c4db, qmarks

from OWI_config import OWI_version as C 
# using  C.OWI_CODETABLES_JSON  and  C.OWI_CODETABLES_DB
    
CODETABLESURL = "https://mgsweb2.mngs.umn.edu/cwi_doc/cwiCodeTables.htm"
BASEURL       = "https://mgsweb2.mngs.umn.edu/cwi_doc/"


def read_codetables_from_web():
    """
    Read the CWI Code Tables index page, then each code table, dump to json
    
    Notes
    -----
    Read the list of code tables on the index page.
    For each table, read the table definition on the .asp page
       returns a dictionary with the following keys:
           {'tablename': tablename, 
            'createtable': createtable statement,
            'insert': insert statement,
            'colnames': list of column names,
            'foreignkeyclause': { 'child_table' : child table name
                                  'foreign_key_clause' : clause text)
    
    """
    import time
    codetabledict = {}
    response = requests.get(CODETABLESURL)
    soup = BeautifulSoup(response.text, 'html.parser')
        
    for tag in soup.find_all('a'):
        if not tag:
            continue
        try:
            page = tag.get('href',None)
            if page.endswith('.asp'):
                tablename = tag.text.strip()
                print (f">> Reading {tablename} from {page}")
                rv = process_table_page(page)
                codetabledict[tablename] = rv
                if len(rv['data']) == 0 or not rv['colnames']:
                    rv = process_table_page(page, verbose=2)
                    print ('~~~~~~~~~~~~ ERROR data = [] ~~~~~~~~~~~~')
                    raise ValueError
                time.sleep(0.1)
                
        except Exception as e:
            print (e)   
    
    with open(C.OWI_CODETABLES_JSON, 'w') as outfile: 
        json.dump(codetabledict, outfile, indent = 2)

    return codetabledict

def process_table_page(page='addr_typ.asp', verbose=0):  
    """
    Read tablename, col descriptions, and data from CWI Code Table page
    
    Arguments
    ---------
    page : str.  The final part of the url, 
                 eg. 'status.asp' for the STATUS table
    verbose: int, 0,1,...,5 Different levels for debugging html interpretations
    
    Returns
    -------
    dictionary : 
        { 'tablename'       : str: tablename,
          'createtable'     : str: CREATE TABLE statement,
          'insert'          : str: INSERT statement,
          'colnames'        : list: colnames,
          'foreignkeyclauses': list: [{'child':str (child tablename),
                                       'foreignkeyclause': str (clause) }...]
          'data'            : list: data rows, each row is a list
        }     

    Notes
    -----
    The html does not have good clues about what tag is what, so the logic here
    is based on the tables a formatted on the web page in Nov, 2023.
        'https://mgsweb2.mngs.umn.edu/cwi_doc/
    """
    def rfmt(b,c,r,d):  # For debugging messages: format 4 bools with hints.
        return f"(b{int(b)} c{int(c)} r{int(r)} d{int(d)})"

    url = BASEURL + page     
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    #print (soup.text)
    tablename  = False
    # codecol = False
    # desccol = False
    readbegun = False
    readcols = False
    readrelationships = False
    readdata = False
    coldefs = []
    relationships = []
    data = []
    #begun = (page != 'str_code.asp')
    
    if 1:
        for i,element in enumerate(soup.find_all("tr")):
            elementtext = element.text.strip()
            if verbose>=4: 
                print (f"-----A[{i}]\n{elementtext} ------------.")            
            
            if not elementtext:
                continue
            
            elements = [line.strip() for line in elementtext.split('\n')]
            if len(elements) > 4:
                continue
 
            # if not readbegun:
            #     if 'Str_code Table Description' in elements:
            #         begun = True
            #         tablename = 'Str_code'
            #     continue
            # if verbose>=3: print (f"B[{i}]----- {str(codecol)[:4]}.{str(desccol)[:4]}.{str(relationships)[:4]},{readdata}, \n", 
            # if verbose>=3: print (f"C[{i}]----- {str(readcols)[:5]}  {str(relationships)[:5]}  {readdata}, \n", 
            #                       '\n      >'.join(elements), '<-----------')
            if verbose>=3: print (f"-[{i}]----- {rfmt(readbegun, readcols, readrelationships, readdata)}, <<{elements}>> -----")
            
            if not readbegun:
                if 'Table Description' in elements[0]:
                    tablename = elements[0].split()[0].upper()
                    readbegun = True
                    if verbose>=3: print (f"D[{i}] tablename = {tablename}, readbegun={readbegun}")
                continue

            # if verbose==3: print (f"C[{i}]----- {str(readcols)[:5]}  {str(relationships)[:5]}  {readdata}, \n", 
            #                       '\n      >'.join(elements), '<-----------')

            if readcols==False and elements[0] == 'Column Name':
                readcols = True
                if verbose>=3: print (f"E[{i}] readcols = {readcols}")
                continue
            
            if readcols==True and elements[0] == 'Relationships':
                # if verbose>=3: print (f"R1[{i}] {elements}") 
                # Assume that the parent column in the relationship is coldefs[0][0]
                parent = f"{tablename}.{coldefs[0][0]}"
                if len(elements) == 3 and elements[-1].startswith('c5'):
                    relationships.append([parent, elements[-1]])
                readrelationships = True
                readcols = False
                if verbose>=3: print (f"F[{i}] readrelationships = {readrelationships}, {relationships}")
                continue
            
            if readcols==True:
                # if verbose>=3: print (f"D[{i}] {elements}")# :: {element}")
                coldefs.append(elements)
                if verbose>=3: print (f"G[{i}] readcols = {readcols}, {coldefs}")
                continue
            
            if readrelationships==True:
                # if verbose>=3: print (f"R2[{i}] {elements}") 
                if 2 <= len(elements) <= 3 and elements[-1].startswith('c5'):
                    relationships.append([parent, elements[-1]])
                    if verbose>=3: print (f"H[{i}] readrelationships = {readrelationships}, {relationships}")
                    continue
                elif ( len(elements) == 1 and
                       len(relationships) >= 1 and 
                       elements[-1].startswith('c5')):
                    relationships.append([parent, elements[-1]])
                    if verbose>=3: print (f"I[{i}] readrelationships = {readrelationships}, {relationships}")
                    continue

            if (not readdata 
                # A data element consisting of column names signals start of data
                # But the column names are entered inconsistently, so matching
                # is sensitive. The following combination works as of Nov. 2023. 
                and  elements[0].lower() == coldefs[0][0].lower() 
                and (len(elements) == 1  
                     or elements[-1].lower()[:4] == coldefs[-1][0].lower()[:4])
                    ): 
                # or (not readdata and elements[0]=='Code'):
                readrelationships = False
                readdata = True   
                if verbose >=2: print(f"J[{i}] Data started: {elements}~~{[d[0] for d in coldefs]}")
                continue
            
            elif (not readdata) and verbose>=2:
                try:
                    print(f"X[{i}] {elements}=?{[d[0] for d in coldefs]}")# :: {element}")
                except:
                    print(f"Y[{i}] {elements} :: {element}")
                continue
            
            if readdata:
                if len(elements)==1 and elements[0]=='Close':
                    break
                elif (2<=len(elements)<=3):
                    data.append(elements)
                elif tablename=='MNCITY' and len(elements)==len(coldefs):     
                    data.append(elements)
                else:
                    break
        
        create, insert, colnames = make_table_defs(tablename, coldefs)  
        fkclauses = make_foreignkey_clauses(relationships) 
        rv = {'tablename'       : tablename,
              'createtable'     : create,
              'insert'          : insert,
              'colnames'        : colnames,
              'foreignkeyclauses': fkclauses,
              'data'            : data}     
        if verbose>=1:
            print ('-- coldefs:', coldefs)
            print ('tablename -- \n', tablename)
            print ('createtable -- \n', create)
            print ('insert -- \n', insert)
            print ('colnames -- \n', colnames)
            print ('-- relationships :', relationships)
            print ('foreignkeyclauses --')
            for fkclause in fkclauses:
                print (  'child:', fkclause['child_table'])
                print (fkclause['foreign_key_clause'])
            print ('len(data) = ', len(data), 'e.g.', data[0])
        if verbose>=5:
            print ( 'data --')
            for row in data:
                print ( '  ',row)
            print ()

        return rv
    
def make_table_defs(tablename, coldefs):
    """
    
    coldefs should be like [[colname, coldef], ...]
    but sometimes is like [[colname,'',coldef], ...]
    """
    # print (f"make_table_def for {tablename}")
    typemap = {'CHAR':'TEXT', 'VARCHAR2':'TEXT'}
    colnames = []
    tablecols = []
    for col in coldefs:
        colname, coldef = col[0], col[-1]
        coltype = typemap.get(coldef.split()[0], 'TEXT')
        if 'primary key' in coldef.lower():
            tablecols.append(f"{colname:<12s} {coltype} UNIQUE NOT NULL") 
        else:
            tablecols.append(f"{colname:<12s} {coltype}") 
        colnames.append(colname)
    c = "CREATE TABLE IF NOT EXISTS %s (\n    %s\n);"%(tablename, ',\n    '.join(tablecols))
    i = f"INSERT OR IGNORE INTO {tablename} ({', '.join(colnames)}) VALUES ({qmarks(colnames)});"
    return c, i, colnames

def make_foreignkey_clauses(relationships):   
    """
    Create a foreign key constraint clause from the relationships tuple.
    
    Arguments
    ---------
    codetable: str,  name of the code table
    fkcol: str, name of the foreign key field in the code table
    relationships: iterable(str, str)     
        e.g. relationships = ['program.program_id', 'c5wl.program'] 
    
    The first str in relationships is the code table name + id field
    The second str in relationships is the child table name + id field
    (The child.fkcol refers to the codetable.fkcol)
    
    NOTE!  The fkcol of the codetable may be incorrectly defined in the 
    relationships tupple. It is more reliable to use the supplied fkcol which 
    is assumed to be the first column in the table def.
    
    In SQLite, a foreign key clause can only be declared at the time that a 
    table is created, so the user will have to copy the table and data to a temp
    table, then redefine the original table, and then copy the data back in.
    All after the code table is created, and all with 'PRAGMA FOREIGN_KEYS=off'
    """
    # t1,f1 = data table, t2,f2 = code table. t1.f1 references t2,d2
    clauses = []
    for relationship in relationships:
        pt,pf = relationship[0].split('.')  # parent_table, parent_field
        ct,cf= relationship[1].split('.')   # child_table, child_field
        # Make sure that the codetable is the parent, 
        # if ct.lower() == codetable.lower():  
        #     pt,pf, ct,cf= ct,cf, pt,pf
        # else:
        #     assert pt.lower() == codetable.lower()
        # pt = codetable  
        # pf = fkcol 
        clause = '\n'.join((f"    CONSTRAINT fk_{ct}_{cf} FOREIGN KEY (",
                            f"       {cf}",
                            f"       )",
                            f"       REFERENCES {pt}({pf})", 
                            f"           ON UPDATE CASCADE",
                            f"           ON DELETE RESTRICT"))
    #print (clause)
        clauses.append({'child_table': ct,
                        'foreign_key_clause': clause})
    return clauses


def write_codetable_to_csv(csvdir, tablename, tabledict):
    """
    Write CWI code table data to a csv file
    """
    if len(tabledict['data']) == 0:
        print (f"{tablename} missing data.")
    csv_name = os.path.join(csvdir, tablename + '.csv')
    #columns = (tabledict['codecol'][0], tabledict['desccol'][0])
    columns = [d[0] for d in tabledict['coldefs'] ]
    with open(csv_name, 'w', newline='') as csvfile:
        w = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        w.writerow(columns)
        for row in tabledict['data']:
            w.writerow(row)
    print (f"{tablename} written to {csv_name}")

def codetables_create_tables(codetabledict):
    """
    Run create table statements from codetabledict 
    """
    print (f"Running all CREATE TABLE statements in {C.OWI_CODETABLES_DB}")
    with c4db(db_name=C.OWI_CODETABLES_DB, commit=True) as db: 
        for tablename, tabledict in codetabledict.items():
            c = tabledict['createtable']
            db.query(c)
        db.commit_db('Finished')

def codetables_load_data(codetabledict):
    """
    Insert data to codetables from codetabledict 
    """
    with c4db(db_name=C.OWI_CODETABLES_DB, commit=True) as db: 
        for tablename, tabledict in codetabledict.items():
            print (f'Loading data into table {tablename}')
            i = tabledict['insert']
            for row in tabledict['data']:
                db.query(i, tuple(row))
        db.commit_db('Finished loading code table data')

def codetables_create_db():
    with open(C.OWI_CODETABLES_JSON, 'r') as f: 
        codetabledict = json.load(f)     
    codetables_create_tables(codetabledict)
    codetables_load_data(codetabledict)

def RUN_codetables():    
    read_codetables_from_web()
    codetables_create_db()
    
if __name__=='__main__': 
    if 0:
        RUN_codetables()
        
    if 0:
        # Reading in the code tables from the web and store in json file
        read_codetables_from_web()
    
    if 1:
        # Read json file, create code tables and load data
        codetables_create_db()
        
    if 0:
        # rv = process_table_page(page='status.asp', verbose=1)
        #rv = process_table_page(page='mncity.asp', verbose=1)   # 1 columns, column caps
        rv = process_table_page(page='str_code.asp', verbose=3)   # ? columns, column caps
        # rv = process_table_page(page='geocsrc.asp', verbose=2)
        # rv = process_table_page(page='loc_src.asp', verbose=2)
        # rv = process_table_page(page='program.asp', verbose=2)  # 3 columns, column caps
        # rv = process_table_page(page='str_geol.asp', verbose=2)  # 3 columns, column caps

    print (r'\\\\\\\\\\\\\\\\ DONE ////////////////////')
    
    
    