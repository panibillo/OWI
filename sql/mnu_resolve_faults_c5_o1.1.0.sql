/*

Version:    c5
Date:       2025-09-21
Author:     William Olsen

Automatically insert identifiers from c5id into o1id that have unverified and
problematic relations to wellids.  These include all of the identifiers 
identified in mnu_insert_01.1.0.sql that have MNU >1, and mmid not null.

Without these modifications, the data would violate data integrity rules for 
table o1id.  But these modified relationships are not verified, and are for 
demonstration purposes only.  The purpose is to test the complex identifier
relations permitted by the MNU identifier model as explained in MNU_Model.pdf.

For reference to un-modified data, use table c5id.

Several exploration queries are provided

select     mnu, smnu, id_type, id_prog, mmid, count(*) from o1id
  group by mnu, smnu, id_type, id_prog, mmid
  order by mnu, smnu, id_type, id_prog, mmid;

select     mnu, smnu, id_type, id_prog, mmid, mexplain, count(*) from c5id
  where mmid > 0
  group by mnu, smnu, id_type, id_prog, mmid, mexplain
  order by mnu, smnu, id_type, id_prog, mmid, mexplain;

select     mnu, smnu, id_type, id_prog, mmid, mexplain, mplan, mresolved, mremark, count(*) from c5id
  where mmid > 0
  group by mnu, smnu, id_type, id_prog, mmid, mexplain, mplan, mresolved, mremark
  order by mnu, smnu, id_type, id_prog, mmid, mexplain, mplan, mresolved, mremark;

*/

-- C5ID_KNOWN_XREFS
-- Records where the well is given 2 wellids in c5ix, and they are cross-referenced
-- in c5id by linking each identifier with the other wellid
-- Identified in c5id_match with wellid1 and wellid2.  Where wellid1 < wellid2.
-- Choose to retain wellid1 as correct and wellid2 as redundant.
-- W-series cross refs are assumed errors and not inserted.
--
-- 11.a
-- First the default identifiers as the numerically smaller wellid
-- IGNORE is required because analysis missed several triples.
INSERT OR IGNORE INTO o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mremark)
SELECT o.wellid1, c2.RELATEID, c.IDENTIFIER, c.ID_TYPE, c.ID_PROG,
  1 AS MNU, 1 AS sMNU, c.mmid, c.mexplain, 'cross referenced in CWI' as mremark
FROM o1id_match o
LEFT JOIN c5id c
  ON o.wellid2 = c.wellid 
LEFT JOIN c5id c2
  ON o.wellid1 = c2.wellid
WHERE c.mexplain = 'C5ID_KNOWN_XREFS'
  AND c.ID_PROG = 'MNUNIQ'
  AND c2.ID_PROG = 'MNUNIQ' ;

-- 11b
-- Second the cross references: larger wellid
-- IGNORE is required because analysis missed several triples.
INSERT OR IGNORE INTO o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mremark)
SELECT o.wellid1, c2.RELATEID, c2.IDENTIFIER, c2.ID_TYPE, c2.ID_PROG,
  1 AS MNU, 0 AS sMNU, c2.mmid, c2.mexplain, 'cross referenced in CWI' as mremark
FROM o1id_match o
LEFT JOIN c5id c
  ON o.wellid2 = c.wellid 
LEFT JOIN c5id c2
  ON o.wellid1 = c2.wellid
WHERE c.mexplain = 'C5ID_KNOWN_XREFS'
  AND c.mmid=11
  AND c2.mmid=11;

-- 12
-- C5ID_UNRESOLVED_MERGES: merge to serve as examples.
INSERT INTO o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mremark)
SELECT o.wellid1, c2.RELATEID, c2.IDENTIFIER, c2.ID_TYPE, c2.ID_PROG,
       12 AS MNU, 0 AS sMNU, c2.mmid, c2.mexplain, 'unconfirmed. example merge' as mremark
FROM o1id_match o
LEFT JOIN c5id c2
  ON o.identifier1 = c2.identifier
WHERE o.mmid = 12
  AND c2.mmid=12
  ;

-- 13
-- C5ID_UNRESOLVED_MERGES_WMWSR : presumed to be errors. IDENTIFIERs missing 'H'.
UPDATE c5id set mplan = 'Do not use. IDENTIFIER probably missing H'
where mmid = 13;

-- 14
-- C5ID_UNRESOLVED_MERGES_WSERIES : presumed to be errors. Cannot resolve using MWI.
UPDATE c5id set mplan = 'Do not use. IDENTIFIER prossibly mixed up'
where mmid = 14;

-- 15 
-- C5ID_BAD_LINKS_OR_REDUNDANT_WELLS : Leave unmerged as examples.
INSERT OR IGNORE INTO o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mplan, mremark)
SELECT wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  8, 0, mmid, mexplain, 'Resolve manually', 'See o1id_match for candidate match.'
FROM c5id
WHERE mmid = 15
;

-- 16
-- C5ID_1WELL_ASSIGNED_2HNUMBERS : Leave unmerged as examples.
INSERT OR IGNORE INTO o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mplan, mremark)
SELECT wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  8, 0, mmid, mexplain, 'Resolve manually', 'See o1id_match for matches.'
FROM c5id
WHERE mmid = 16
;

--17 
-- Records resembling H-records of well sets, where the individual wells have
-- individual wellids, and there is no wellid dedicated to the H number.
-- 17a create the cross reference entries in o1id, using MNU=9
-- Individual well wellid <-9-> well set IDENTIFIER
INSERT into o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mremark)
select wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  9 as MNU, 0 as sMNU, mmid, mexplain, 'unconfirmed' as mremark
from c5id where mmid=17;

-- 17b 
-- Create the well set entries in c5ix.
-- Use modified H-num as wellid: 8000000000 + numeric part of H-number.
-- Grab basic well information from the the first individual linked wellid.
INSERT INTO c5ix (
    wellid, unique_no, RELATEID, COUNTY_C, WELLNAME, 
    TOWNSHIP, RANGE, RANGE_DIR, SECTION, SUBSECTION, MGSQUAD_C,
    --ELEVATION, ELEV_MC, 
    STATUS_C, USE_C, 
    LOC_MC, LOC_SRC, DATA_SRC, 
    DEPTH_DRLL, DEPTH_COMP, DATE_DRLL, CASE_DIAM, CASE_DEPTH, GROUT, 
    --POLLUT_DST, POLLUT_DIR, POLLUT_TYP, 
    --STRAT_DATE, STRAT_UPD, STRAT_SRC, STRAT_GEOL, STRAT_MC, 
    DEPTH2BDRK, FIRST_BDRK, LAST_STRAT, OHTOPUNIT, OHBOTUNIT, AQUIFER  
    --CUTTINGS, CORE, BHGEOPHYS, GEOCHEM, WATERCHEM, OBWELL, SWL, DH_VIDEO, 
    --INPUT_SRC, UNUSED, ENTRY_DATE, UPDT_DATE
    , owi_remark
    )
select  S.wellid, S.unique_no, S.wellid as RELATEID, 
    COUNTY_C, 'well set' as WELLNAME, 
    TOWNSHIP, RANGE, RANGE_DIR, SECTION, SUBSECTION, MGSQUAD_C,
    --ELEVATION, ELEV_MC, 
    STATUS_C, USE_C, 
    LOC_MC, LOC_SRC, DATA_SRC, 
    DEPTH_DRLL, DEPTH_COMP, DATE_DRLL, CASE_DIAM, CASE_DEPTH, GROUT, 
    --POLLUT_DST, POLLUT_DIR, POLLUT_TYP, 
    --STRAT_DATE, STRAT_UPD, STRAT_SRC, STRAT_GEOL, STRAT_MC, 
    DEPTH2BDRK, FIRST_BDRK, LAST_STRAT, OHTOPUNIT, OHBOTUNIT, AQUIFER  
    --CUTTINGS, CORE, BHGEOPHYS, GEOCHEM, WATERCHEM, OBWELL, SWL, DH_VIDEO, 
    --INPUT_SRC, UNUSED, ENTRY_DATE, UPDT_DATE
    , 'Created 8B_number for sealing Set' AS owi_remark
from (select '8000' || substr(IDENTIFIER,2,6)  as wellid, 
              IDENTIFIER as unique_no, 
              min(wellid) as linkid
      from c5id
      where mmid=17  
      group by identifier) as S
left join c5ix x
  on S.linkid = x.wellid;
  
-- 17c Create well set entries in o1id for the well set IDENTIFIERS
-- use MNU=3 because the individual wells exist also.
-- This version creates 8-B wellid and 8-B RELATEID, but not 8-B IDENTIFIER.
INSERT into o1id(wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG,
  MNU, sMNU, mmid, mexplain, mplan, mremark) 
SELECT CAST('8000' || substr(IDENTIFIER,2,6) AS INTEGER)  as wellid,  	
       '8000' || substr(IDENTIFIER,2,6)  as RELATEID, 
       IDENTIFIER, 
       'SET' as ID_TYPE, 
       'WMWSR' as ID_PROG,
       3 as MNU, 1 as sMNU, 
       17 as mmid, 
       'C5ID_H_IS_MULTY_OR_BAD_REF' as mexplain, 
       'OWI synthetic wellid and RELATEID' as mplan,
       'unverified' as mremark
FROM c5id
WHERE mmid=17  
GROUP BY IDENTIFIER;

-- -- Inspect results of effort 17
-- select mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark, count(*) 
--   from c5id
--   where mmid=17
--   group by mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark
--   order by mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark;
-- 
-- select mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark, count(*) 
--   from o1id
--   where mmid=17
--   group by mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark
--   order by mnu, smnu, id_type, id_prog, mexplain, mplan, mresolved, mremark;
-- 
-- select WELLNAME, min(wellid), max(wellid), count(*)
--   from c5ix
--   where WELLNAME='well set';


-- Part 2: append remaining records from c5ix
-- (562532 records inserted, out of 563336 total in c5ix)
INSERT INTO o1id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, MNU, sMNU,
                  mmid)
SELECT x.wellid, x.RELATEID, x.UNIQUE_NO, 'c5ix', 'MNUNIQ', 1, 1, 1
--     , o.identifier, o.MNU, o.sMNU, o.mmid
FROM c5ix x
LEFT JOIN o1id_match m1
  ON x.UNIQUE_NO = m1.identifier1
LEFT JOIN o1id_match m2
  ON  x.UNIQUE_NO = m2.identifier2
left join o1id o
  on x.UNIQUE_NO = o.IDENTIFIER
where m1.wellid1 is null
  and m2.wellid2 is null
  and (o.wellid is null OR o.sMNU=0)
;

-- Part 2b: append remaining records from c5ix
-- 7 records
INSERT INTO o1id (wellid, RELATEID, IDENTIFIER, ID_TYPE, ID_PROG, 
                  MNU, sMNU, mmid, mexplain, mplan, mremark)
SELECT x.wellid, x.RELATEID, x.UNIQUE_NO, 'c5ix', 'MNUNIQ', 
       1, 1, i.mmid, i.mexplain, 'unconfirmed', 'resolution Part 2b'
FROM c5ix x
left join c5id i
  on x.unique_no = i.identifier
left join o1id o
  on x.Unique_NO = o.identifier
where x.wellid in (
    select distinct u.wellid 
    from v1idu u
    left join v1ids s
      on u.wellid = s.wellid
    where s.wellid is null)
and i.mnu > 0
and o.identifier is null
;

-- Format all H-numbers in o1id as Hnnnnnn  (H + 6 digits, zero padded)
UPDATE o1id 
SET IDENTIFIER = 'H' || substr('00000'||substr(IDENTIFIER,2,9),-6,6)  	
WHERE IDENTIFIER LIKE ('H%') and MNU=1;

-- Format all W-numbers in o1id in standard format
--  W-Format = (2-digit county code) + 'W' + (7-digits). E.g. '02W0034567'
UPDATE o1id 
SET IDENTIFIER = WNUM_FORMAT(A.identifier, x.county_c)
FROM o1id A
LEFT JOIN c5ix x
  ON A.wellid = x.wellid
WHERE (A.id_prog in ('WSERIES','WMWSR') 
       OR (A.id_type='CNTY' AND A.id_prog='ULID'))
  AND A.identifier REGEXP '\b\d?\d?W[-]?\d{5,8}\b';

