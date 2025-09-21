/* OWI SCHEMA

Version:    c4.4.0
Date:       2021-02-10
Author:     William Olsen

These are DDL statements for an SqlLite version of the OWI database.

This version:
    - Contains the c4 data tables
    - Adds table c4locs for well coordinates.
    - Adds rowid and wellid to each c4 data table
    - Adds Foreign Key constraints to all tables, wellid -> c4ix(wellid)
    - Adds owi_remark to c4 tables, to document changes from CWI original recs.
    + Makes o1id into the main table for all well identifiers.
        + Add all Unique Well Numbers in c4ix to o1id.
        + Add conditional unique indices on o1id to enforce uniqueness of
          the default identifier.
        + Add Views on o1id to simplify using Unique Well Numbers for search
          and for export. (Views are defined in mnu_views_c4.4.0)
        + Data, as cloned from cwi, may not pass all integrity checks.

References:

sql/cwischema_c4_versions.txt
TeX/MNU_model.ltx (.pdf)

County Well Index, 2021, Database created and maintained by the Minnesota
Geological Survey, a department of the University of Minnesota,  with the
assistance of the Minnesota Department of Health.

http://mgsweb2.mngs.umn.edu/cwi_doc/cwidoc.htm

https://www.sqlite.org

*/

CREATE TABLE c4ix (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    COUNTY_C    INTEGER,
    UNIQUE_NO    TEXT,
    WELLNAME    TEXT,
    TOWNSHIP    INTEGER,
    "RANGE"     INTEGER,
    RANGE_DIR   TEXT,
    SECTION     INTEGER,
    SUBSECTION  TEXT,
    MGSQUAD_C   TEXT,
    ELEVATION   INTEGER,
    ELEV_MC     TEXT,
    STATUS_C    CHAR,
    USE_C       TEXT,
    LOC_MC      CHAR,
    LOC_SRC     TEXT,
    DATA_SRC    TEXT,
    DEPTH_DRLL  REAL,
    DEPTH_COMP  REAL,
    DATE_DRLL   INTEGER,
    CASE_DIAM   REAL,
    CASE_DEPTH  REAL,
    GROUT       CHAR,
    POLLUT_DST  INTEGER,
    POLLUT_DIR  TEXT,
    POLLUT_TYP  TEXT,
    STRAT_DATE  INTEGER,
    STRAT_UPD   INTEGER,
    STRAT_SRC   TEXT,
    STRAT_GEOL  TEXT,
    STRAT_MC    CHAR,
    DEPTH2BDRK  REAL,
    FIRST_BDRK  TEXT,
    LAST_STRAT  TEXT,
    OHTOPUNIT   TEXT,
    OHBOTUNIT   TEXT,
    AQUIFER     TEXT,
    CUTTINGS    CHAR,
    CORE        CHAR,
    BHGEOPHYS   CHAR,
    GEOCHEM     CHAR,
    WATERCHEM   CHAR,
    OBWELL      CHAR,
    SWL         CHAR,
    DH_VIDEO    CHAR,
    INPUT_SRC   TEXT,
    UNUSED      CHAR,
    ENTRY_DATE  INTEGER,
    UPDT_DATE   INTEGER,
    owi_remark  TEXT,
    CONSTRAINT un_c4ix_wellid
        UNIQUE (wellid)
);

CREATE TABLE c4ad (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    NAME        TEXT,
    ADDTYPE_C   CHAR,
    HOUSE_NO    TEXT,
    STREET      TEXT,
    ROAD_TYPE   TEXT,
    ROAD_DIR    TEXT,
    CITY        TEXT,
    STATE       TEXT,
    ZIPCODE     TEXT,
    ENTRY_DATE  INTEGER,
    UPDT_DATE   INTEGER,
    OTHER       TEXT,
    owi_remark  TEXT,
    CONSTRAINT fk_c4ad_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4an (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    C5AN_SEQ_NO REAL,
    AZIMUTH     INTEGER,
    INCLIN      INTEGER,
    ANG_DEPTH   INTEGER,
    owi_remark  TEXT,
    CONSTRAINT fk_c4an_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4c1 (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    DRILL_METH  CHAR,
    DRILL_FLUD  CHAR,
    HYDROFRAC   CHAR,
    HFFROM      REAL,
    HFTO        REAL,
    CASE_MAT    CHAR,
    CASE_JOINT  CHAR,
    CASE_TOP    REAL,
    DRIVE_SHOE  CHAR,
    CASE_TYPE   CHAR,
    SCREEN      CHAR,
    OHTOPFEET   REAL,
    OHBOTFEET   REAL,
    SCREEN_MFG  TEXT,
    SCREEN_TYP  CHAR,
    PTLSS_MFG   TEXT,
    PTLSS_MDL   TEXT,
    BSMT_OFFST  CHAR,
    CSG_TOP_OK  CHAR,
    CSG_AT_GRD  CHAR,
    PLSTC_PROT  CHAR,
    DISINFECTD  CHAR,
    PUMP_INST   CHAR,
    PUMP_DATE   INTEGER,
    PUMP_MFG    TEXT,
    PUMP_MODEL  TEXT,
    PUMP_HP     REAL,
    PUMP_VOLTS  INTEGER,
    DROPP_LEN   REAL,
    DROPP_MAT   CHAR,
    PUMP_CPCTY  REAL,
    PUMP_TYPE   CHAR,
    VARIANCE    CHAR,
    DRLLR_NAME  TEXT,
    ENTRY_DATE  INTEGER,
    UPDT_DATE   INTEGER,
    owi_remark  TEXT,
    CONSTRAINT fk_c4c1_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4c2 (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    CONSTYPE    CHAR,
    FROM_DEPTH  REAL,
    TO_DEPTH    REAL,
    DIAMETER    REAL,
    SLOT        REAL,
    LENGTH      REAL,
    MATERIAL    CHAR,
    AMOUNT      REAL,
    UNITS       CHAR,
    owi_remark  TEXT,
    CONSTRAINT fk_c4c2_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4id (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    IDENTIFIER  TEXT,
    ID_TYPE     TEXT,
    ID_PROG     TEXT,
    MNU         INTEGER NOT NULL DEFAULT (0),
    sMNU        INTEGER NOT NULL DEFAULT (0),
	mmid        INTEGER,
	mexplain    TEXT,
    mplan       TEXT,
    mresolved   INTEGER,
	mremark 	TEXT
);

CREATE TABLE o1id (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    IDENTIFIER  TEXT    NOT NULL,
    ID_TYPE     TEXT,
    ID_PROG     TEXT,
    MNU         INTEGER NOT NULL DEFAULT (0),
    sMNU        INTEGER NOT NULL DEFAULT (0),
	mmid        INTEGER,
	mexplain    TEXT,
    mplan       TEXT,
	mresolved	INTEGER,
	mremark 	TEXT,
    CONSTRAINT fk_o1id_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_o1id_MNU
        CHECK (((sMNU = 0) AND (MNU BETWEEN 0 AND 20)) 
            OR ((sMNU = 1) AND (MNU IN (1,2,3))))
);		   
-- MNU values:   0 : not MNU (local identifiers, etc.)
--               1 : Regular Unique Well Number referencing a wellid that 
--                   describes a single well
--               2 : A Multiwell Record Number referencing a Multiwell wellid.
--                   Individual wells have no MNU identifiers nor wellids.
--               2 : A Multiwell Record Number referencing a Multiwell wellid.
--                   Individual wells also have MNU identifiers and wellids.
--               4 : Cross reference entry: from a Multiwell Record identifier 
--                   to an individual well wellid. Do not count as a well.
--               10-20 : Records needing various kinds of work. No Uniqueness 
--                   constraints. 

CREATE UNIQUE INDEX ux_o1id_IDENTIFIER__MNU
    ON o1id (identifier)
    WHERE MNU in (1,2,3)
;
 
CREATE UNIQUE INDEX ux_o1id_wellid__sMNU
    ON o1id (wellid)
    WHERE sMNU = 1
;
 
CREATE UNIQUE INDEX ux_o1id_id_identifier_MNU
    ON o1id(wellid, identifier)  
    WHERE  MNU IN (1,2,3,4,5)
;


CREATE TABLE c4pl (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    PUMPTESTID  INTEGER,
    TEST_DATE   INTEGER,
    START_MEAS  REAL,
    FLOW_RATE   REAL,
    DURATION    REAL,
    PUMP_MEAS   REAL,
    owi_remark  TEXT,
    CONSTRAINT fk_c4pl_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

--    CONSTRAINT un_c4rm_wellid_SEQ_NO
--        UNIQUE (wellid, SEQ_NO),
CREATE TABLE c4rm (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    SEQ_NO      INTEGER,
    REMARKS     TEXT,
    owi_remark  TEXT,
    CONSTRAINT fk_c4rm_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

--    CONSTRAINT un_c4st_wellid_DEPTH_TOP
--        UNIQUE (wellid, DEPTH_TOP),
--    CONSTRAINT un_c4st_wellid_DEPTH_BOT
--        UNIQUE (wellid, DEPTH_BOT),
CREATE TABLE c4st (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    DEPTH_TOP   REAL,
    DEPTH_BOT   REAL,
    DRLLR_DESC  TEXT,
    COLOR       TEXT,
    HARDNESS    TEXT,
    STRAT       TEXT,
    LITH_PRIM   TEXT,
    LITH_SEC    TEXT,
    LITH_MINOR  TEXT,
    owi_remark  TEXT,
    CONSTRAINT fk_c4st_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4wl (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    RELATEID    TEXT    NOT NULL,
    MEAS_TYPE   TEXT,
    MEAS_DATE   INTEGER,
    MEAS_TIME   INTEGER,
    M_PT_CODE   CHAR,
    MEAS_POINT  REAL,
    MEASUREMT   REAL,
    MEAS_ELEV   REAL,
    DATA_SRC    TEXT,
    PROGRAM     TEXT,
    ENTRY_DATE  INTEGER,
    UPDT_DATE   INTEGER,
    owi_remark  TEXT,
    CONSTRAINT fk_c4wl_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE c4locs (
    rowid       INTEGER PRIMARY KEY NOT NULL,
    wellid      INTEGER NOT NULL,
    CWI_loc     TEXT,
    RELATEID    TEXT,
    COUNTY_C    INTEGER,
    UNIQUE_NO   TEXT,
    WELLNAME    TEXT,
    TOWNSHIP    INTEGER,
    "RANGE"     INTEGER,
    RANGE_DIR   TEXT,
    SECTION     INTEGER,
    SUBSECTION  TEXT,
    MGSQUAD_C   TEXT,
    ELEVATION   REAL,
    ELEV_MC     TEXT,
    STATUS_C    TEXT,
    USE_C       TEXT,
    LOC_MC      TEXT,
    LOC_SRC     TEXT,
    DATA_SRC    TEXT,
    DEPTH_DRLL  REAL,
    DEPTH_COMP  REAL,
    DATE_DRLL   INTEGER,
    CASE_DIAM   REAL,
    CASE_DEPTH  REAL,
    GROUT       TEXT,
    POLLUT_DST  INTEGER,
    POLLUT_DIR  TEXT,
    POLLUT_TYP  TEXT,
    STRAT_DATE  INTEGER,
    STRAT_UPD   INTEGER,
    STRAT_SRC   TEXT,
    STRAT_GEOL  TEXT,
    STRAT_MC    TEXT,
    DEPTH2BDRK  REAL,
    FIRST_BDRK  TEXT,
    LAST_STRAT  TEXT,
    OHTOPUNIT   TEXT,
    OHBOTUNIT   TEXT,
    AQUIFER     TEXT,
    CUTTINGS    TEXT,
    CORE        TEXT,
    BHGEOPHYS   TEXT,
    GEOCHEM     TEXT,
    WATERCHEM   TEXT,
    OBWELL      TEXT,
    SWL         TEXT,
    DH_VIDEO    TEXT,
    INPUT_SRC   TEXT,
    UNUSED      TEXT,
    ENTRY_DATE  INTEGER,
    UPDT_DATE   INTEGER,
    GEOC_TYPE   TEXT,
    GCM_CODE    TEXT,
    GEOC_SRC    TEXT,
    GEOC_PRG    TEXT,
    UTME        REAL,
    UTMN        REAL,
    GEOC_ENTRY  INTEGER,
    GEOC_DATE   INTEGER,
    GEOCUPD_EN  INTEGER,
    GEOCUPD_DA  INTEGER,
    RCVD_DATE   INTEGER,
    WELL_LABEL  TEXT,
    SWLCOUNT    INTEGER,
    SWLDATE     INTEGER,
    SWLAVGMEAS  REAL,
    SWLAVGELEV  REAL,
    owi_remark  TEXT,
    CONSTRAINT un_c4locs_wellid
        UNIQUE (wellid),
    CONSTRAINT fk_c4locs_wellid
        FOREIGN KEY (wellid)
        REFERENCES c4ix (wellid)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

