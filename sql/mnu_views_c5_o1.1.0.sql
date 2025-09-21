/* CWI SCHEMA

Version:    c4.4.0
Date:       2021-02-10
Author:     William Olsen

These are DDL statements for an SqlLite version of the CWI database.
These statements create views of the c4 data tables that expose the default Unique Well Number only, utilizing View v1idp

This version:
    - Contains the c4 data tables
    - Adds table c4locs for well coordinates.
    - Adds rowid and wellid to each c4 data table
    - Adds Foreign Key constraints to all tables, wellid -> c4ix(wellid)
    + Makes c4id into the main location for all well identifiers.
        + Add all Unique Well Numbers in c4ix to c4id.
        + Add conditional unique indices on c4id to enforce uniqueness.
        + Add Views on c4id to simplify using Unique Well Numbers for search
          and for export.
        + Data, as cloned from cwi, may not pass all integrity checks.

References:

sql/cwischema_c4_versions.txt

County Well Index, 2021, Database created and maintained by the Minnesota
Geological Survey, a department of the University of Minnesota,  with the
assistance of the Minnesota Department of Health.

https://www.sqlite.org

*/

-- A veiw of only MNU identifiers
CREATE VIEW IF NOT EXISTS v1idu AS
    SELECT * FROM o1id
    WHERE MNU in(1,2,3)
;

-- A view of only MNU singleton identifiers
CREATE VIEW IF NOT EXISTS v1ids AS
    SELECT * FROM o1id
    WHERE sMNU = 1
;

-- Cross reference map from Well Set identifiers to Individual Well
-- identifiers.  Lists Well Set identifiers next to each of their
-- individual well identifiers,
-- and the ID_TYPEs and ID_PROGs of all identifiers.
CREATE VIEW IF NOT EXISTS v1idsets AS -- mx: multi-well x-references
SELECT M.wellid AS Mwellid, 
       M.identifier AS Midentifier, 
       M.ID_TYPE AS MID_TYPE, 
       M.ID_PROG AS MID_PROG,
       I.identifier AS identifier, 
       I.wellid AS wellid, 
       I.ID_TYPE AS ID_TYPE, 
       I.ID_PROG AS ID_PROG
FROM o1id M
LEFT JOIN o1id X
  ON M.identifier = X.identifier
LEFT JOIN o1id I
  ON X.wellid = I.wellid
WHERE M.MNU IN (2,3)
  AND X.MNU = 9
  AND M.sMNU=1
  AND I.sMNU=1
ORDER BY M.identifier, I.wellid
;

-- views of tables that expose the sMNU values
CREATE VIEW IF NOT EXISTS vo1ix AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.COUNTY_C,
    A.WELLNAME,
    A.TOWNSHIP,
    A."RANGE",
    A.RANGE_DIR,
    A.SECTION,
    A.SUBSECTION,
    A.MGSQUAD_C,
    A.ELEVATION,
    A.ELEV_MC,
    A.STATUS_C,
    A.USE_C,
    A.LOC_MC,
    A.LOC_SRC,
    A.DATA_SRC,
    A.DEPTH_DRLL,
    A.DEPTH_COMP,
    A.DATE_DRLL,
    A.CASE_DIAM,
    A.CASE_DEPTH,
    A.GROUT,
    A.POLLUT_DST,
    A.POLLUT_DIR,
    A.POLLUT_TYP,
    A.STRAT_DATE,
    A.STRAT_UPD,
    A.STRAT_SRC,
    A.STRAT_GEOL,
    A.STRAT_MC,
    A.DEPTH2BDRK,
    A.FIRST_BDRK,
    A.LAST_STRAT,
    A.OHTOPUNIT,
    A.OHBOTUNIT,
    A.AQUIFER,
    A.CUTTINGS,
    A.CORE,
    A.BHGEOPHYS,
    A.GEOCHEM,
    A.WATERCHEM,
    A.OBWELL,
    A.SWL,
    A.DH_VIDEO,
    A.INPUT_SRC,
    A.UNUSED,
    A.ENTRY_DATE,
    A.UPDT_DATE
FROM c4ix A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1ad AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.NAME,
    A.ADDTYPE_C,
    A.HOUSE_NO,
    A.STREET,
    A.ROAD_TYPE,
    A.ROAD_DIR,
    A.CITY,
    A.STATE,
    A.ZIPCODE,
    A.ENTRY_DATE,
    A.UPDT_DATE,
    A.OTHER
FROM c4ad A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1an AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.C5AN_SEQ_NO,
    A.AZIMUTH,
    A.INCLIN,
    A.ANG_DEPTH
FROM c4an A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1c1 AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.DRILL_METH,
    A.DRILL_FLUD,
    A.HYDROFRAC,
    A.HFFROM,
    A.HFTO,
    A.CASE_MAT,
    A.CASE_JOINT,
    A.CASE_TOP,
    A.DRIVE_SHOE,
    A.CASE_TYPE,
    A.SCREEN,
    A.OHTOPFEET,
    A.OHBOTFEET,
    A.SCREEN_MFG,
    A.SCREEN_TYP,
    A.PTLSS_MFG,
    A.PTLSS_MDL,
    A.BSMT_OFFST,
    A.CSG_TOP_OK,
    A.CSG_AT_GRD,
    A.PLSTC_PROT,
    A.DISINFECTD,
    A.PUMP_INST,
    A.PUMP_DATE,
    A.PUMP_MFG,
    A.PUMP_MODEL,
    A.PUMP_HP,
    A.PUMP_VOLTS,
    A.DROPP_LEN,
    A.DROPP_MAT,
    A.PUMP_CPCTY,
    A.PUMP_TYPE,
    A.VARIANCE,
    A.DRLLR_NAME,
    A.ENTRY_DATE,
    A.UPDT_DATE
FROM c4c1 A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1c2 AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.CONSTYPE,
    A.FROM_DEPTH,
    A.TO_DEPTH,
    A.DIAMETER,
    A.SLOT,
    A.LENGTH,
    A.MATERIAL,
    A.AMOUNT,
    A.UNITS
FROM c4c2 A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1pl AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.PUMPTESTID,
    A.TEST_DATE,
    A.START_MEAS,
    A.FLOW_RATE,
    A.DURATION,
    A.PUMP_MEAS
FROM c4pl A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1rm AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.SEQ_NO,
    A.REMARKS
FROM c4rm A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1st AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.DEPTH_TOP,
    A.DEPTH_BOT,
    A.DRLLR_DESC,
    A.COLOR,
    A.HARDNESS,
    A.STRAT,
    A.LITH_PRIM,
    A.LITH_SEC,
    A.LITH_MINOR
FROM c4sts A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1wl AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.MEAS_TYPE,
    A.MEAS_DATE,
    A.MEAS_TIME,
    A.M_PT_CODE,
    A.MEAS_POINT,
    A.MEASUREMT,
    A.MEAS_ELEV,
    A.DATA_SRC,
    A.PROGRAM,
    A.ENTRY_DATE,
    A.UPDT_DATE
FROM c4wl A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;

CREATE VIEW IF NOT EXISTS vo1locs AS
SELECT
    A.rowid,
    A.wellid,
    S.IDENTIFIER,
    A.CWI_loc,
    A.COUNTY_C,
    A.UNIQUE_NO,
    A.WELLNAME,
    A.TOWNSHIP,
    A."RANGE",
    A.RANGE_DIR,
    A.SECTION,
    A.SUBSECTION,
    A.MGSQUAD_C,
    A.ELEVATION,
    A.ELEV_MC,
    A.STATUS_C,
    A.USE_C,
    A.LOC_MC,
    A.LOC_SRC,
    A.DATA_SRC,
    A.DEPTH_DRLL,
    A.DEPTH_COMP,
    A.DATE_DRLL,
    A.CASE_DIAM,
    A.CASE_DEPTH,
    A.GROUT,
    A.POLLUT_DST,
    A.POLLUT_DIR,
    A.POLLUT_TYP,
    A.STRAT_DATE,
    A.STRAT_UPD,
    A.STRAT_SRC,
    A.STRAT_GEOL,
    A.STRAT_MC,
    A.DEPTH2BDRK,
    A.FIRST_BDRK,
    A.LAST_STRAT,
    A.OHTOPUNIT,
    A.OHBOTUNIT,
    A.AQUIFER,
    A.CUTTINGS,
    A.CORE,
    A.BHGEOPHYS,
    A.GEOCHEM,
    A.WATERCHEM,
    A.OBWELL,
    A.SWL,
    A.DH_VIDEO,
    A.INPUT_SRC,
    A.UNUSED,
    A.ENTRY_DATE,
    A.UPDT_DATE,
    A.GEOC_TYPE,
    A.GCM_CODE,
    A.GEOC_SRC,
    A.GEOC_PRG,
    A.UTME,
    A.UTMN,
    A.GEOC_ENTRY,
    A.GEOC_DATE,
    A.GEOCUPD_EN,
    A.GEOCUPD_DA,
    A.RCVD_DATE,
    A.WELL_LABEL,
    A.SWLCOUNT,
    A.SWLDATE,
    A.SWLAVGMEAS,
    A.SWLAVGELEV
FROM c4locs A
LEFT JOIN v1ids S
  ON A.wellid = S.wellid
;



