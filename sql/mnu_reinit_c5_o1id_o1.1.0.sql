/* CWI SCHEMA

Version:    c4.4.0
Date:       2022-04-30
Author:     William Olsen

Queries to reinitialize o1id so that it can be filled from scratch.
Table 01id_match is also emptied, and created if it is not present.
*/


delete from o1id;

-- Create a table for identifying and resolving wrong or complex relationships
-- 
create table if not exists o1id_match (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid1     INTEGER NOT NULL,
    wellid2     INTEGER,
	identifier1 TEXT,
	identifier2 TEXT,
	mmid        INTEGER,
	mexplain    TEXT,
    mplan       TEXT,
	mresolved	INTEGER,
	mremark 	TEXT
);

delete from o1id_match;

