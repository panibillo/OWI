'''
Created on Dec 16, 2021

@author: bill
'''
import os

def read_sql_file(sql_file): 
    """
    Read sql statments from an sql file.
    Returns a list of the statements in the order read.
    The statements are not checked for validity.
    """
    assert os.path.exists(sql_file), os.path.abspath(sql_file)

    with open(sql_file) as f:
        ftxt = f.read()    
    
    # The file is allowed to have 1 comment block before the sql statements.
    # So try splitting on the close comment symbol.
    try:  
        ftxt = ftxt.split('*/')[1] 
    except:
        pass
    #Split the text on the ';' symbol into distinct sql statements.
    statements = [t.strip() + ';' for t in ftxt.split(';')[:-1]]
    
    assert len(statements) >= 1
    return statements
     
       
def execute_statements_from_file(db, sql_file, verbose=False):
    """
    Read and execute a series of statements from an sql statement file
    
    This method does not handle statements that fail; an error occurs.
    """
    print (f"execute_statements_from_file: {sql_file}")
    print (f"   into {db.db_name}")
    statements = read_sql_file(sql_file)
    n = len(statements)
    for i,s in enumerate(statements):
        if verbose:
            print (f"> Satement {i} of {n} ...\n{s}")
        db.query(s)
        if verbose:
            print ("---------- done -----------")
    print (f"Finished all statments in {sql_file}")
