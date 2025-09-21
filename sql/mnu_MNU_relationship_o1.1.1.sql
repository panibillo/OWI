/* CWI SCHEMA

Version:    c4.4.0
Date:       2021-02-19
Author:     William Olsen

These are queries initialize, or reinitialize the o1id tables 

Assumed that they will be populated from scratch, so the cleanest thing is to
simply empty them.  The order of emptying considers foreign key relationships. 

*/

-- Create the code table for MNU identifier relationship types
CREATE TABLE MNU_relationship(
    rowid       INTEGER PRIMARY KEY NOT NULL,
    Code        INTEGER NOT NULL,
    Descrptn    TEXT    NOT NULL)
;
    
INSERT INTO MNU_relationship(Code, Descrptn)
VALUES
(0,'not a MNU identifier'),
(1,'MNU identifier for a standard well'),
(2,'MNU identifier for a set of wells where individual wells do not have wellids'),
(3,'MNU identifier for a set of wells where individual wells also have wellids'),
(4,'provisional MNU identifier where wellid represents a site'),
(8,'presumed identifier or assignment error'),
(9,'cross reference between IDENTIFIER for a well set and a wellid for an individual well')
;
