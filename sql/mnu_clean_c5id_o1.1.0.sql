/* CWI SCHEMA

Version:    c4.4.0
Date:       2021-02-19
Author:     William Olsen

Queries to clean up and/or initialize table c4id in two scenarios:
1)  Clean up tasks needed immediately after c4id is first imported from the 
	CWI original version, and before MNU analysis can be done.
2)  Re-initialization tasks needed when MNU analysis will be re-done from the
    beginning.
*/

-- Remove records from c4id where the IDENTIFIER is null.
Delete from c4id 
where IDENTIFIER is Null;
;

-- Initialize the MNU flags, part 1.
update c4id
    set MNU = 0, sMNU = 0, 
    mexplain=NULL, mmid=NULL, mplan=NULL, mresolved=NULL, mremark=NULL
;

-- Initialize the MNU flags, part 21.
update c4id
    set MNU = 1
    where ID_PROG in ('MNUNIQ','WMWSR','WSERIES')
;

-- Remove identifiers from c4id where the identifier is equivalent to the 
-- wellid, and the id_prog is one of the Unique Well Number types. Every wellid 
-- must also exist in c4ix, and those will be imported to o1id later along with 
-- all of the other wellids in c4ix, presumably with ID_PROG='MNUNIQ'.
Delete from c4id 
where MNU = 1
  and cast(wellid as text) = IDENTIFIER 
;
