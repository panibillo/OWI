/*
Version:    c5  
Date:       2025-09-21
Author:     William Olsen


Insert newer records from c5locs table into c5ix table.
Identify the newer records by setting field c5ix.UNUSED = 'from c5locs'

Apparently new records may be added to the GIS layers before they are added to 
the CWI tables.  Here they are added only to the c5ix table, and no analysis
is yet written to populate the other c5/c5 data tables.

The number of newer records in c5locs is sometimes 0, and typically not too 
large. 

--   Running this insert multiple times should be harmless, but if it is desired
-- to delete affected records from c5ix before running, then the ids have to 
-- also be deleted from o1id first, becuase of the Foreign Key relationship.
--   Run the following 2 queries in order. Both depend on identifying the  
-- records using c5ix.UNUSED = 'from c5locs'. 
DELETE FROM o1id 
  WHERE wellid IN(
    SELECT wellid 
	FROM c5ix 
	WHERE UNUSED = 'from c5locs')
;

DELETE from c5ix
  WHERE UNUSED = 'from c5locs'
;
*/
Insert into c5ix (
    wellid, RELATEID, COUNTY_C, UNIQUE_NO, WELLNAME,
    TOWNSHIP, RANGE, RANGE_DIR, SECTION, SUBSECTION, MGSQUAD_C,
    ELEVATION, ELEV_MC,
    STATUS_C, USE_C,
    LOC_MC, LOC_SRC, DATA_SRC,
    DEPTH_DRLL, DEPTH_COMP, DATE_DRLL,
    CASE_DIAM, CASE_DEPTH, GROUT,
    POLLUT_DST, POLLUT_DIR, POLLUT_TYP,
    STRAT_DATE, STRAT_UPD, STRAT_SRC, STRAT_GEOL, STRAT_MC,
    DEPTH2BDRK, FIRST_BDRK, LAST_STRAT, OHTOPUNIT, OHBOTUNIT,
    AQUIFER, CUTTINGS, CORE, BHGEOPHYS,
    GEOCHEM, WATERCHEM, OBWELL, SWL, DH_VIDEO,
    INPUT_SRC, UNUSED, ENTRY_DATE, UPDT_DATE, owi_remark)
SELECT
    L.wellid, L.RELATEID, L.COUNTY_C, L.UNIQUE_NO, L.WELLNAME,
    L.TOWNSHIP, L.RANGE, L.RANGE_DIR, L.SECTION, L.SUBSECTION, L.MGSQUAD_C,
    L.ELEVATION, L.ELEV_MC,
    L.STATUS_C, L.USE_C,
    L.LOC_MC, L.LOC_SRC, L.DATA_SRC,
    L.DEPTH_DRLL, L.DEPTH_COMP, L.DATE_DRLL,
    L.CASE_DIAM, L.CASE_DEPTH, L.GROUT,
    L.POLLUT_DST, L.POLLUT_DIR, L.POLLUT_TYP,
    L.STRAT_DATE, L.STRAT_UPD, L.STRAT_SRC, L.STRAT_GEOL, L.STRAT_MC,
    L.DEPTH2BDRK, L.FIRST_BDRK, L.LAST_STRAT, L.OHTOPUNIT, L.OHBOTUNIT,
    L.AQUIFER, L.CUTTINGS, L.CORE, L.BHGEOPHYS,
    L.GEOCHEM, L.WATERCHEM, L.OBWELL, L.SWL, L.DH_VIDEO,
    L.INPUT_SRC, L.UNUSED, L.ENTRY_DATE, L.UPDT_DATE,
    'From c5locs only' as owi_remark
FROM c5locs L
LEFT JOIN c5ix X
  ON L.wellid = X.wellid
  WHERE X.wellid IS NULL
;
