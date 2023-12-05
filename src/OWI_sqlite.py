'''
Created on Sep 12, 2020

@author: Bill Olsen

A cwi clone database in sqlite.

Two service functions are included:

-   showprogress() : a semi-graphical progress indicator.
-   qmarks() : generate a string of "?" characters for use in queries.

Class c4db implements only variables and methods that are agnostic as to
the database schema and database engine.  

Class c4db inherits from class DB_SQLite.
DB_SQLite holds SQLite dependent methods, and inherits the context manager 
mixin class DB_context_manager.

Class DB_context_manager is a mixin class: 
    it adds functionality to a class that inherits it, 
    it has no __init__, and 
    it depends on some methods to be implemented by a class that inherits it. 

    Syntax options for the context manager:
        with c4db(db_name) as db:  
        with c4db(db_name, commit=True):
        with c4db(db_name, open_db=False):
    
    Defaults argument values: 
        open_db=True.  Explicitly call db.open_db() to open the connection
        commit=False.  Prohibit commits
        

Methods
-------
    with c4db() as db:     [context manager syntax]

    showprogress()
    qmarks() or c4db.qmarks()
    c4db.query()
    c4db.queryone()
    c4db.get_tablenames()
    c4db.get_viewnames()
    c4db.get_column_names()
    c4db.get_column_type_dict()

'''
import csv
import os
import re
import sqlite3 as sqlite
from collections import OrderedDict

# from OWI_config import OWI_DATA_TABLE_PREFIX

def showprogress(n, b=10):
    """
    Provide a semi-graphical progress indicator in the console
    
    Arguments 
    ---------
    n : integer. 
        Iteration counter
    b : integer. 
        if b>0: Iteration printing interval. (optional)
        if b=0: Terminates the progress indicator 
    
    Returns
    -------
    n+1    if b>0
    0      if b=0
        
    Usage
    ----- 
    icount = 0
    <begin loop>:
        <do stuff>
        icount = showprogress(icount, 500)
    showprogress(icount, 0)
    """
    if b==0:
        print ('!',n)
        return 0
    n += 1
    bbb, bb = 100*b, 10*b 
    if  n%bbb==0: print (',',n)
    elif n%bb==0: print (',',end='',flush=True)
    elif  n%b==0: print ('.',end='',flush=True)
    return n 

def qmarks(vals):
    '''
    Return a string of comma separated questionmarks for vals

    Questionmark parameter markers are used in pysqlite execute methods to 
    prevent sql injection. See the pysqlite documentation.
    
    Arguments
    vals : iterable (list or tuple), integer, or string.
           vals is interpreted to determine 'n' the number of '?' symbols 
           required.  As follows:
             iterable : n = len(vals)
             string   : n=1.
             int      : n = vals
    Examples
        vals = 'Bill'         n=1, return '?'
        vals = 4              n=4, return '?,?,?,?'
        vals = [4]            n=1, return '?'
        vals = (1,2,'Bill')   n=3, return '?,?,?'
        
    Notes: 
        The interpretation of 'n' from vals is pretty intuitive when vals is an
    iterable or an integer.  But the interpretation of n from other argument 
    types would be arbitrary, and not intuitive for users.  Therefore Other 
    non-iterable types are left to throw an error when len() is called.  But 
    strings have a len() method, so are treated as a special case that is 
    intepreted as signifying a single val.
        The qmarks method can be imported by itself, but is also made available
    as a method in class DB_SQLite.
    '''
    if isinstance(vals, str):
        return '?'
    elif isinstance(vals, int):
        return ','.join(vals * ['?'])
    else:
        return ','.join(len(vals) * ['?'])

def REGEXP(pattern, target_string):
    """ 
    Define a Regular Expression function that can be imported to sqlite.
    
    Returns True if pattern is matched in target_string, False if not matched.
    
    Usage:
    First instantiate the function in the sqlite connection:
        con = sqlite.connect(dbname)
        con.create_function("REGEXP", 2, REGEXP)
    
    Search using either of 2 syntax options: (ex. pattern is '^W/d' using '?') 
        
        syntax1  <string> REGEXP <pattern>
          ex1  = "SELECT * FROM <table> WHERE <field> REGEXP ?;"    

        syntax2  REGEXP(<pattern>, <string>)
          ex2  = "SELECT * FROM <table> WHERE REGEXP(?,<field>);"  

        data = cur.execute(query, ('^W/d', 1) ).fetchall()  -- pattern is '^W/d'
    """    
    try:
        return re.search(pattern, target_string, re.IGNORECASE) is not None
    except Exception as e:
        print(e)

def REGEXP1(pattern, target_string, group=None):
    """ 
    Define a Regular Expression function that can be imported to sqlite.
    
    Returns True if pattern is matched in target_string, False if not matched.
    
    Usage:
    First instantiate the function in the sqlite connection:
        con = sqlite.connect(dbname)
        con.create_function("REGEXP", 2, REGEXP)
    
    Search using either of 2 syntax options: (ex. pattern is '^W/d' using '?') 
        
        syntax1  <string> REGEXP <pattern>
          ex1  = "SELECT * FROM <table> WHERE <field> REGEXP ?;"    

        syntax2  REGEXP(<pattern>, <string>)
          ex2  = "SELECT * FROM <table> WHERE REGEXP(?,<field>);"  

        data = cur.execute(query, ('^W/d', 1) ).fetchall()  -- pattern is '^W/d'
    """    
    try:
        return re.search(pattern, target_string, re.IGNORECASE) is not None
    except Exception as e:
        print(e)

W_PATTERN = re.compile(r"^(W)(\d+$)")
CW_PATTERN = re.compile(r"^(\d\d)([W])(\d+$)") 
MNU_PATTERN = re.compile(r"^H?(\d+$)")
        
def WNUM_FORMAT(Wliteral, county_c, default_val=None):
    """
    Convert a W-number into standard 10-character W-number format.
       <2-digit county number code> + 'W' + <7-digit unique number>
    
    Arguments (Any of the arguments may be NULL.) :
    *   Wliteral : string.  e.g.  'W12345'
    *   county_co: integer (2-digit MN County Code)
    *   default_val: <any type> [optional] 
    
    Returns:
    A properly formatted W number if possible; else the default_val.
        
    If county_c is suppled and Wliteral contains a county code, then they are
    compared.  If they do not match then the default_val is returned. 
    
    Usage:
    First instantiate the function in the sqlite connection:
        con = sqlite.connect(dbname)
        con.create_function("WNUM_FORMAT", -1, WNUM_FORMAT)
    
    Examples:
        "SELECT WNUM_FORMAT('W12345',19)"               => "19W0012345"
        "SELECT WNUM_FORMAT('19W12345',19)"             => "19W0012345"
        "SELECT WNUM_FORMAT('19W0012345',19)"           => "19W0012345"
        "SELECT WNUM_FORMAT('19W12345',NULL)"           => "19W0012345"
        "SELECT WNUM_FORMAT('W12345',NULL)"             =>  NULL
        "SELECT WNUM_FORMAT('19W12345',82)"             =>  NULL
        "SELECT WNUM_FORMAT('19W12345',82,'19W12345')"  => "19W12345"
        "SELECT WNUM_FORMAT('H12345',19)"               =>  NULL
        "SELECT WNUM_FORMAT('H12345',19,NULL)"          =>  NULL
        "SELECT WNUM_FORMAT('H12345',19,'OOPS')"        => "OOPS"
    """
    try:
        s = Wliteral.upper().strip()
        # First attempt to match Wliteral formatted W#.
        u = W_PATTERN.findall(s)
        if u and len(u[0]) == 2:
            # return f"{Wliteral:10}  matches W_PATTERN=<{u}> "
            co = f"{int(county_c):02}"
            if len(co) == 2:
                return f"{co}W{int(u[0][1]):07}"
        else:
            # Second attempt to match Wliteral formatted #W#.
            v = CW_PATTERN.findall(s)
            if v and len(v[0]) == 3:  # v = [('19', 'W', '00001234')]
                #return f"{Wliteral:10}  matches CW_PATTERN=<{v}>"
                co = int(v[0][0])
                if 0 < co < 100:
                    if county_c is not None:
                        assert int(county_c) == co
                    return f"{int(v[0][0]):02}W{int(v[0][2]):07}"
                
        return default_val
        #return f"{Wliteral:10}  NO match"
    # try:
    #     i = Wliteral.upper().find('W') 
    #     if i == 0: 
    #         if county_c is None:
    #             return default_val
    #         c,n = county_c, int(Wliteral[i+1:])
    #     elif i > 0:
    #         c,n = int(Wliteral[:i]), int(Wliteral[i+1:])
    #         if county_c is not None:
    #             assert c == county_c
    #     if i<0:
    #         return default_val
    #     return f"{c:02d}W{n:07d}"
    except Exception as e:
        #print (e, Wliteral, county_c)
        return default_val

def RELATEID_FORMAT(Uliteral, default_val=None):
    """
    Convert a MNU identifier into a 10 character string RELATEID value.
    
    Arguments  
    ---------
    *   Uliteral : string/NULL.  e.g.  'H12345', '0012345', '19W00123'
    *   default_val: <any type> [optional] 
    
    Returns:
    --------
    RELATEID : str or default_val
    
    Rules:
        -   RELATEID should be a 10 character string
        -   May begin with 'H' followed by 9 digits
        -   May begin with ## + 'W' + 7 digits. Where ## is a 2-digit county code.
        -   Leading zeros are added to integers
    
    Examples:
        12345, '12345', '0012345', '0000012345'           =>  '0000012345'
        'H1234', 'H001234', 'H-1234', 'H#1234', '#H1234'  =>  'H000012345'
        '82W123', '82W000123', '82W0000123'               =>  '82W0000123'
        'W123', 'P123', '', NULL/None                     =>  default_val
    
    TODO:
        -   W number formatting should utilize WNUM_FORMAT, rather than being 
            re-written here.
        -   This version allows weird formats of input, with '#' and '-'. 
            There should be a version that catches and does not allow those.
    """
    try:
        val = str(Uliteral).upper().replace('-','').replace(' ','').replace('#','')
        assert 1 <= len(val) <= 10
        if (val.startswith('H')):
            assert len(val) >= 2
            return f"H{int(val[1:]):09d}"
        elif (val[2]=='W'):
            assert len(val) >= 4
            return f"{val[:2]}W{int(val[3:]):07d}"
        else:
            return f"{int(val):010d}"
    except:
        return default_val
    # try:
    #     rid = WNUM_FORMAT(Uliteral, None, None)
    #     return rid
    # except:
    #     pass
    # try:
    #     s = Uliteral.upper().strip()
    #     u = MNU_PATTERN.findall(s)
    #     if len(u) == 1:
    #         v = u[0]
    #         if not s.endswith(v):
    #             return default_val
    #         n = s.find(v)
    #         if n == 0:
    #             return str(int(v))
    #         elif n == 1:
    #             return f"{Uliteral[0]}{str(int(v))}"
    #     else:
    #         v = CW_PATTERN.findall(s)
    #         if v and len(v[0]) == 3:
    #             return f"{v[0][0]}W{str(int(v[0][2]))}" 
    #         else:
    #             return default_val 
    #     # else:
    #     #     print (f"MUN_FORMAT('{Uliteral}') ERROR: '{s}' => {u}")
    #     #     return default_val
    # except Exception as e:
    #     #print (e)
    #     return default_val        
    
def MNU_FORMAT(Uliteral, default_val=None):
    """
    Convert a MNU identifier into a standard format: no leading zeros.
    W-numbers are returned unmodified.
    
    Arguments  
    ---------
    *   Uliteral : string/NULL.  e.g.  'H00012345', '00001234'
    *   default_val: <any type> [optional] 
    
    Returns:
    A standardized format MNU if possible; else the default_val.
        
    Usage:
    First instantiate the function in the sqlite connection:
        con = sqlite.connect(dbname)
        con.create_function("MNU_FORMAT", -1, MNU_FORMAT)
    
    Examples:
        "SELECT MNU_FORMAT('H12345')"               => "H12345"
        "SELECT MNU_FORMAT('H0012345')"             => "H12345"
        "SELECT MNU_FORMAT('0052345')"              => "52345"
        "SELECT MNU_FORMAT('52345',NULL)"           => "52345"
        "SELECT MNU_FORMAT('5234x',NULL)"           =>  NULL
        "SELECT MNU_FORMAT('5234x')"                =>  NULL
        "SELECT MNU_FORMAT('GARBAGE','Trash')"      => 'Trash'
        
    Value of NULL when this is compiled in a SQL engine, is equivalent to 
    value of None when this is compiled in a Python engine.  The NULL in the 
    examples is a true SQL NULL type, and not a text "NULL"
    """
    try:
        s = Uliteral.upper().strip()
        u = MNU_PATTERN.findall(s)
        if len(u) == 1:
            v = u[0]
            if not s.endswith(v):
                return default_val
            n = s.find(v)
            if n == 0:
                return str(int(v))
            elif n == 1:
                return f"{Uliteral[0]}{str(int(v))}"
        else:
            v = CW_PATTERN.findall(s)
            if v and len(v[0]) == 3:
                return f"{v[0][0]}W{str(int(v[0][2]))}" 
            else:
                return default_val 
        # else:
        #     print (f"MUN_FORMAT('{Uliteral}') ERROR: '{s}' => {u}")
        #     return default_val
    except Exception as e:
        #print (e)
        return default_val    

class DB_context_manager():
    """ 
    A mixin class defining a context manager for a database. 
    
    The DB_context_manager mixin class defines 2 variables
        _context_connected   True if the db connection was open already
        _context_autocommit  If True, commit edits at exit.

    The database class inheriting DB_context_manager must define the following 
    methods:
        open_db()
        commit_db()
        close_db()
    
    The database class's commit_db() method should call context_permits_commit()
    prior to committing edits, and should not commit if not permitted.
        
    Usage:
        with mydb(commit=True) as db:    # _context_autocommit = True
        with mydb(commit=False) as db:   # _context_autocommit = False
        with mydb() as db:               # _context_autocommit = False

        When _context autocommit is True, edits will be committed when the 
    context is exited, AND the user can manually call commit_db() in code any 
    time while the context is still open.
        When _context autocommit is False, all calls to commit_db() are ignored.
    In this context, it is safe to play with the database because nothing will
    be committed.  BUT WARNING: a programmer can ignore _context_autocommit by  
    directly calling mydb.cur.commit().
    """   
    def __init__(self, commit=False):    
        self._context_connected = False
        self._context_autocommit = commit
    
    def __enter__(self):
        self._context_connected = self.open_db()  
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        if self._context_autocommit==True:
            OK = self.commit_db()
            print ('commit=',OK)
        # TODO: check logic of next statement. Should test be '== True:' ?
        if self._context_connected == False:
            self.close_db()
        self._context_connected = False
        self._context_autocommit = False
    
    def context_permits_commit(self):
        if self._context_autocommit == False:
            print ('Commit is forbidden by the context manager.')
        return self._context_autocommit

class DB_SQLite(DB_context_manager):
        
    def __init__(self, db_name=None, open_db=False, commit=False, converttypes=True):
        self.db_name = db_name
        self.qmarks = qmarks
        self.converttypes = converttypes  
        if open_db: 
            self.connection_open = self.open_db()
        else: 
            self.connection_open = False
        super().__init__(commit)
 
    def __str__(self):
        rv=(f"     database name:      {self.db_name}",
            f"     connection_open:    {self.connection_open}",
            f"    _context_connected:  {self._context_connected}",
            f"    _context_autocommit: {self._context_autocommit}")
        return '\n'.join(rv)

    def __repr__(self):
        rv = (f"DB_SQLite(db_name='{self.db_name}'," 
              f" open_db={self.connection_open}," 
              f" commit={self._context_autocommit})")
        return rv

    @staticmethod
    def qmarks(vals):
        return qmarks(vals)
    
    def open_db(self):
        """
        Open a connection to the db.
        
        Creates functions:
            REGEXP
            MNU_FORMAT
            WNUM_FORMAT
            
        Handles date-times using switch "detect_types"
            https://pynative.com/python-sqlite-date-and-datetime/
        
        """
        try:
            if self.converttypes:
                self.con = sqlite.connect(self.db_name,
                                          detect_types=sqlite.PARSE_DECLTYPES |
                                                       sqlite.PARSE_COLNAMES)
            else:
                self.con = sqlite.connect(self.db_name)
            self.con.execute('PRAGMA trusted_schema=OFF') # see https://www.sqlite.org/appfunc.html
            self.con.create_function("REGEXP", 2, REGEXP)
            self.con.create_function("WNUM_FORMAT", -1, WNUM_FORMAT)
            self.con.create_function("MNU_FORMAT", -1, MNU_FORMAT)

            self.cur = self.con.cursor()
            
            self.connection_open = True
        except:
            print (f"db_sqlite/db_open: ERROR - could not open database: {self.db_name}.")
            self.connection_open = False
        return self.connection_open
        
    def close_db(self, commit=None):    
        if commit==True:
            self.commit_db()
        if hasattr(self, 'cur'):
            self.cur.close()
            self.con.close()
        self.connection_open = False

    def commit_db(self, msg=''):
        if self.db_name == ':memory:':
            return True
        if self.context_permits_commit() == False:
            return False
        try:
            self.con.commit()
            if msg != '':
                print (f'>> Successful commit: {msg}')
            return True
        except Exception as e:
            print ('>> Exception attempting to commit. ' + msg)
            print(e)
            return False

    def vacuum(self):
        try:
            self.cur.execute('VACUUM')
            return True
        except Exception as e:
            print (e)
            return False
        
    def query(self, sql, vals=None, n=None):
        """ 
        Execute a query and return the result set
        """
        rv = []
        if vals is None:
            try:
                self.cur.execute(sql)
                #rv = self.cur.fetchall()
            except Exception as e:
                print(f"ERROR A: query failed\n{sql}\n{str(e)}\n===============") 
                return rv
        else:             
            try:
                self.cur.execute(sql, vals)
                #rv = self.cur.fetchall()
            except Exception as e1:
                try:
                    self.cur.execute(sql, tuple(vals))
                    #rv = self.cur.fetchall()
                except Exception as e2:
                    print(f"ERROR B: query failed\n{sql}")
                    print(f"{str(vals)[:60]}...,{str(vals)[-60:]}")
                    print(f">>err1: {str(e1)}\n--------------------")
                    print(f">>err2: {str(e2)}\n====================") 
                    return rv
        if n is None:
            rv = self.cur.fetchall()
        else:
            rv = self.cur.fetchmany(n)
        return rv            

    def queryone(self, sql, vals=None, default=None):
        """
        Execute a query and return first result tuple, or value.
        
        Returns
        -------
        If query returns multiple values per row: return first row as tuple.
        If query returns a one value per row: return the value (not as tuple)
        """
        rv = self.query(sql, vals=vals, n=1)
        if len(rv)==1:
            rv = rv[0]
            if len(rv)==1:
                return rv[0]
            else:
                return rv
        else:
            return default
    
    def get_tablenames(self):
        ''' Return a tuple of all Table names in the database'''
        data = self.cur.execute("select name from sqlite_master where type='table'").fetchall()
        rv = tuple(row[0] for row in data)
        return rv

    def get_viewnames(self):
        ''' Return a tuple of all View names in the database'''
        data = self.cur.execute("select name from sqlite_master where type='view'").fetchall()
        return tuple(row[0] for row in data)

    def get_column_names(self, table_name):
        """ Return a list of field_names table_name."""
        data = self.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
        return [str(f[1]) for f in data]

    def get_column_type_dict (self, table_name):
        """ 
        Return a dictionary of {field_name: field_type} for table_name.
        """
        data = self.cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
        return OrderedDict({str(f[1]) : str(f[2]) for f in data})

    def import_csv_to_table(self, table_name, csv_name, column_defs=None):
        """
        Import a csv file to a table in the currently open database.
        
        Arguments
        ---------
        table_name: str
        csv_name: str
        column_defs: dict {column_name:column_def}
        
        -   If the table does not exist, it is created using column_defs.
        
        -   Names of the columns in the csv file must match the column names in 
            the existing table, or column_defs, exactly
        
        -   If column_defs is None, then the table should already exist, and the 
            list of columns is read from the existing table.
        """
        raise NotImplementedError
        if not os.path.exists(csv_name):
            raise ValueError(
                f"The csv file is not found: {csv_name}")
            return False
        table_exists = table_name in self.get_tablenames()
        if not (table_exists or column_defs):
            raise ValueError(
                f"Table {table_name} is missing and cannot be created without column_defs")
            return False
        if not table_exists:
            colstr = ',\n    '.join([f"{k} {v}" for k,v in column_defs.items()])
            q = f"CREATE TABLE {table_name} (\n    {colstr}\n);"
            self.query(q) 
            self.commit_db(q)
            colnames = [c.lower() for c in column_defs.keys()]
        else:
            colnames = [c.lower() for c in self.get_column_names(table_name)]
        
        with open(csv_name, 'r') as fsrc:
            reader = csv.reader(fsrc)         
            header_row = True   
            collist = []  
            irow = 0
            s = f"INSERT INTO {table_name} ("
            for row in reader:   
                irow += 1   
                if header_row:    
                    for col in row:
                        col = col.strip() 
                        assert col.lower() in colnames, f'Column {col} in csv is not defined in {table_name}'
                        collist.append(col)  
                    colstr = ', '.join(collist)  
                    s = f"INSERT INTO {table_name} (\n  {colstr}\nVALUES ({self.qmarks(collist)});"
                else:
                    if len(row) == len(collist):
                        self.query(s, tuple(row))
            self.commit_db(f"{irow} rows read into {table_name} from {csv_name}.")
            return True
        
    def export_table_to_csv(self, table_name, csv_name, where=''):   
        """      
        Export [selected] records from table tablename to a csv file.
        
        Arguments
        ---------
        tablename : string. Name of a table in the database
        csv_name  : string. Filename of the csv file (with path)
        where     : string, Optional. Where clause. If where is empty then all
                    records are exported.   E.g.  where="where wellid = 123"
        
        Notes
        -----
        -   The csv file must not exist. If it already exists, simply abort.
        -   All columns are written in native order except rowid.
        -   The csv dialect is 'excel' with all non-numeric values quoted.
        """
        
        cols = self.get_column_names(table_name)
        if 'rowid' in cols:
            cols.remove('rowid')
        s = f"""select {', '.join(cols)} 
                from {table_name} {where} 
                order by wellid;""".replace('                ',' ')
        
        if os.path.exists(csv_name):
            raise NotImplementedError(
                'Overwriting existing csv files is not allowed: '+csv_name)
            return False
        with open(csv_name, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, 
                            dialect='excel')
#                            quoting=csv.QUOTE_NONNUMERIC)
            w.writerow(cols)
            for row in self.query(s):
                w.writerow(row)
        print (f"{table_name} written to {csv_name}")

class c4db(DB_SQLite): 
    def __init__(self, db_name=None, 
                       open_db=False, 
                       commit=False):
        
        DB_SQLite.__init__(self, db_name, open_db=open_db, commit=commit)
        
#         datatables = 'ix ad an c1 c2 id pl rm st wl locs'.split()
#         self.datatables = [f"{OWI_DATA_TABLE_PREFIX}{t}" for t in datatables]

    def __str__(self):
        rv=(f"c4db() a SQLite implementation of County Well Index",
            super().__str__() )
        return '\n'.join(rv)

    def __repr__(self):
        rv = (f"c4db(db_name='{self.db_name}'," 
              f" open_db={self.connection_open}," 
              f" commit={self._context_autocommit})")
        return rv

    def update_unique_no_from_wellid(self, tablename):
        """
        Update column UNIQUE_NO in table c5ix to remove leading zeros.
        
        Arguments
        ---------
        tablename: string.  value is either 'c4ix' or 'c4locs'
            
        Notes
        -----
        This routine does not issue a COMMIT
        
        Assumes that the wellid is equivalent to the Unique_no. That assumption
        should be true for versions of cwi through c4 and c5 at least.
        """
        assert tablename in ('c4ix c4locs')
        u = f"update {tablename} set UNIQUE_NO = cast(wellid as text);"     
        try:
            self.query(u)
            return True
        except Exception as e:
            print ('update_unique_no_from_wellid():\n  ', e)
            return False 

     
#     def set_triggers_enabled(self, enable):
#         assert isinstance(enable, bool)
#         if self.connection_open:
#             self.con.create_function("trigs_enabled", 0, self.
#         
# def triggers_on():      
#     return 1  
# def triggers_off():      
#     return 0  

if __name__=='__main__':
    if 1:
        DB_NAME = r'/home/bill/R/cwi/OWI40.sqlite'
        print (DB_NAME)
        con = sqlite.connect(DB_NAME)
        print(con.execute(r"SELECT 'H1234' REGEXP('^H?(\d+$)');").fetchall())
        # con.create_function("REGEXP", 2, REGEXP)
        # con.create_function("WNUM_FORMAT", -1, WNUM_FORMAT)
        # con.create_function("MNU_FORMAT", -1, MNU_FORMAT)

    
    
    if 0:
        # W_PATTERN = re.compile(r"(W)(\d+)")
        # CW_PATTERN = re.compile(r"(\d\d)([W])(\d+)") 
        # MNU_PATTERN = re.compile(r"^H?(\d+$)")

        for s in ('W001234',
                  'X001234',
                  '19W001234',
                  'H000123',
                  'H123',
                  '0000456',
                  '456',
                  'W1234',
                  '19W1234',
                  'TRASH',
                  '1234X',
                  ):
            print (f"MNU_FORMAT({s:>10}) = [{MNU_FORMAT(s, 'err'):>10}]"
                   f"  MNU: {str(MNU_PATTERN.findall(s)):18s}"   
                   f"  W: {str(W_PATTERN.findall(s)):18s}" 
                   f"  W2: {CW_PATTERN.findall(s)}")
    
    if 0:
        for args, result in (
            (('W12345',None)           ,  None       ),
            (('192W12345',None)        ,  None       ),
            (('3W12345',None)          ,  None       ),
            (('W12345',19)             , "19W0012345"),
            (('19W12345',19)           , "19W0012345"),
            (('19W0012345',19)         , "19W0012345"),
            (('19W12345',None)         , "19W0012345"),
            (('19W12345X',None)        ,  None       ),
            (('19W12345',82)           ,  None       ),
            (('19W12345',82,'CO ERR')  , "CO ERR"    ),
            (('H12345',19)             ,  None       ),
            (('H12345',19,None)        ,  None       ),
            (('12345',19,'OOPS')       , "OOPS"      )
            ):
            # if args[0] == 'W12345':
            #     print (args)
            wnum = WNUM_FORMAT(*args)
            print (f"WNUM_FORMAT{str(args):29} = {str(wnum):10}"
                   f"  {wnum == result}"
                   f"     MNU: {str(MNU_PATTERN.findall(args[0])):18s}"   
                   f"  W: {str(W_PATTERN.findall(args[0])):18s}" 
                   f"  W2: {CW_PATTERN.findall(args[0])}")

    if 0: 
        print ('Test of __str__() and __repr__()')
        COMMIT = False
        DB_NAME = ":memory:"
        print("\nDemonstrate opening c4db using a context manager")
        with c4db(db_name=DB_NAME, commit=COMMIT) as db:
            print (repr(db))
            print (db)
    
        print("\nDemonstrate opening and closing c4db without a context manager")
        db = c4db(db_name=DB_NAME, open_db=False,  commit=True)
        print (repr(db))
        print (db)
        db.close_db()
           
        print("\nDemonstrate opening DB_SQLite using a context manager")
        with DB_SQLite(db_name=DB_NAME) as db:
            print (repr(db))
            print (db)
    
        print("\nDemonstrate opening and closing DB_SQLite without a context manager")
        db = DB_SQLite(db_name=DB_NAME, open_db=True,  commit=False)
        print (repr(db))
        print (db)
        db.close_db()
    if 0:
        assert isinstance(True, bool)
        assert isinstance(False, bool)
        DB_NAME = ":memory:"
        
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        print (type(con), con)
        print (type(cur))
        # con.create_function("trig_enabled", 0, triggers_on)
        # cur.execute("select trig_enabled()" )
        # print ('ON?', cur.fetchone()[0])
        # con.create_function("trig_enabled", 0, triggers_off)
        # cur.execute("select trig_enabled()" )
        # print ('OFF?', cur.fetchone()[0])

        with c4db(db_name=DB_NAME, commit=True, open_db=True) as db:
            print (type(db.con), db.con)
            #print (type(db.cur))
            print (db.connection_open)
            print (db.get_tablenames())
            # db.con.create_function("trig_enabled", 0, triggers_on)
            # db.con.create_function("trig_enabled", 0, triggers_on)
            # v = db.queryone("trig_enabled()")
            # print ('ON?',v)
            # db.con.create_function('triggers_enabled', 0, triggers_off)
            # v = db.queryone("triggers_enabled()")
            # print ('OFF?',v)
    if 0:
        data = ('PILLSBURY GRAIN STATION (DNR OB 24004)',
                'DNR OB 59003-CALVIN BURGGRAAFF',
                'DNR OB 76036',
                'WONT MATCH',)
        pattern1 = 'DNR OB [0-9]{5}'
        pattern2 = 'DNR OB ([0-9]{5})'
        for target in data:
            try:
                rv1 = re.search(pattern1, target, re.IGNORECASE)
                rv2 = re.search(pattern2, target, re.IGNORECASE)
                print (100, rv1)
                print (101, rv2)
                print (dir(rv2))
                print ()
            except Exception as e:
                print (e)
            
        
    print ('\n',r'\\\\\\\\\\\\\\\\\\ DONE //////////////////')        
        