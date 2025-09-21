CREATE TABLE o1sr (
    rowid    INTEGER PRIMARY KEY NOT NULL,
    wellid1  INTEGER NOT NULL,  -- Foreign key
    wellid2  INTEGER NOT NULL,  -- Foreign key  
    CONSTRAINT fk_o1sr_wellid1 FOREIGN KEY  
        (wellid1) REFERENCES c4ix (wellid) 
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_o1sr_wellid2 FOREIGN KEY  
        (wellid2) REFERENCES c4ix (wellid) 
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT un_o1sr_wellid12
        UNIQUE (wellid1,wellid2),
    CONSTRAINT chk_o1sr_wellidorder
        CHECK (wellid1 < wellid2)
);  

CREATE VIEW v1sr AS  
    SELECT rowid, wellid1, wellid2
    FROM o1sr
    UNION 
    SELECT rowid, wellid2 AS wellid1, wellid1 AS wellid2
    FROM o1sr;
    
select count(*), mmid, mexplain
  from o1id 
  group by mmid, mexplain;
select * from o1id
  where mmid = 17
  order by identifier, wellid;
  
--select Mwellid, wellid
select distinct Mwellid
from v1idsets
order by Mwellid;

--insert or ignore into o1sr(wellid1,wellid2)
--  select Mwellid, wellid from v1idsets
--  where Mwellid < wellid;
--insert or ignore into o1sr(wellid2,wellid1)
--  select Mwellid, wellid from v1idsets
--  where Mwellid > wellid;

--update c4ix set set_c=3
--  where wellid in (select Mwellid from v1idsets);
--update c4ix set set_c=2
--  where wellid in (select wellid from v1idsets);

select set_c, count(*) from c4ix group by set_c;

select * from c4ix where wellid = 80003436;
select * from o1id where wellid = 80003436;
select * from o1id 
  where wellid between 8000018636 and 8000385217
  order by wellid;
select wellid, unique_no, use_c, set_c
from c4ix where wellname = 'well set';
/*update c4ix set set_c = 3 
  where wellname = 'well set' 
    and wellid between 8000018636 and 8000385217; */
/*update c4ix set relateid = cast(wellid as text) 
  where wellid between 8000018636 and 8000385217; */

select S.wellid1, I.IDENTIFIER, X.wellid, X.unique_no, X.use_c, X.set_c
From o1sr S
left join c4ix X
  on S.wellid2 = X.wellid
left join o1id I 
  on S.wellid1 = I.wellid
order by S.wellid1, S.wellid2;

CREATE TABLE SET_CODES (
    Code       INTEGER PRIMARY KEY NOT NULL,
    Descrptn   TEXT 
);
INSERT INTO SET_CODES (Code, Descrptn)
VALUES
(   0 , 'Well entity is single well, and is not a member of another set.'),
(   1 , 'Well entity describes a set, and has no subsets or intersections.'),
(   2 , 'Well entity is single well, and also belongs to one or more sets.'),
(   3 , 'Well entity describes a set, and has subsets or intersections.'),
(   4 , 'Well entity describes a set, and every member is a single well with a wellid.');

select * from o1id where mnu=3;

SELECT V1.wellid1, X1.STATUS_C as status_1, I1.IDENTIFIER AS Hnum1,
       V1.wellid2, X2.STATUS_C as status_2, I2.IDENTIFIER AS Unum2
    FROM c4ix X1
    LEFT JOIN o1id I1
      ON X1.wellid = I1.wellid
    LEFT JOIN v1sr V1
      ON X1.wellid = V1.wellid1
    LEFT JOIN o1id I2
      ON V1.wellid2 = I2.wellid
    LEFT JOIN c4ix X2
      ON V1.wellid2 = X2.wellid
    WHERE X1.SET_C in (3,4)     -- sets with identified members 
      AND I1.ID_PROG = 'WMWSR'  -- sealing record for the set
      AND I2.ID_PROG = 'MNUNIQ'; -- sealing records for members

-- Vibe wire sets
-- Searched in the Remarks table for initial prospects. 
-- Prospects then searched by x,y distance, and studied.
SELECT * from c4rm where remarks like ('%VIBE WIRE%')
ORDER BY wellid, seq_no;

/*
207246 (331398, 331399) H295598
209826 (270224 270225 270226 270227), H269508
217868 (272095 272096 272097) H163638
201005 (272089 272090 272091) ?Hscan?
231849 (272093) ?Hscan?
231851 (272094) ?Hscan?
*/
/*
-- Identify set containers in c4ix 
update c4ix set set_c = 4 where wellid in (
      207246,
      209826,
      217868,
      201005,
      231849,
      231851);
update c4ix set set_c = 2 where wellid in (
      331398,331399,
      270224, 270225, 270226, 270227,
      272095, 272096, 272097,
      272089, 272090, 272091,
      272093,
      272094);
insert or ignore into o1sr (wellid1, wellid2)
  values (207246,331398), 
         (207246,331399),
         (209826,270224),
         (209826,270225),
         (209826,270226),
         (209826,270227),
         (217868,272095),
         (217868,272096),
         (217868,272097),
         (201005,272089),
         (201005,272090),
         (201005,272091),
         (231849,272093),
         (231851,272094);
*/
-- Show the set_id and member_id for all sets defined for 
-- entities with set_c=4 . Utilizes view v1sr so that 
-- set-wellid may be higher or lower than member-wellid.
select wellid1 as setid, wellid2 as memberid from v1sr
  where wellid1 in (select wellid 
                    from c4ix 
                    where set_c = 4)
  order by wellid1;






