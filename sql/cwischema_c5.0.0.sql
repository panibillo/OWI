/* CWI SCHEMA

Version:    c4.0.0
Date:       2021-02-10
Author:     William Olsen

These are DDL statements for an SqlLite version of the CWI database.

This version:
    + Contains the c4 data tables

References:

sql/cwischema_c4_versions.txt

County Well Index, 2021, Database created and maintained by the Minnesota
Geological Survey, a department of the University of Minnesota,  with the
assistance of the Minnesota Department of Health.

https://www.sqlite.org

*/

CREATE TABLE c4ix (
    RELATEID    TEXT    NOT NULL,
    COUNTY_C    INTEGER,
    UNIQUE_NO   TEXT,
    WELLID      INTEGER,
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
    UPDT_DATE   INTEGER
);

CREATE TABLE c4ad (
    RELATEID   TEXT    NOT NULL,
    NAME       TEXT,
    ADDTYPE_C  CHAR,
    HOUSE_NO   TEXT,
    STREET     TEXT,
    ROAD_TYPE  TEXT,
    ROAD_DIR   TEXT,
    CITY       TEXT,
    STATE      TEXT,
    ZIPCODE    TEXT,
    ENTRY_DATE INTEGER,
    UPDT_DATE  INTEGER,
    OTHER       TEXT
);

CREATE TABLE c4an (
    RELATEID    TEXT    NOT NULL,
    C5AN_SEQ_NO REAL,
    AZIMUTH        INTEGER,
    INCLIN        INTEGER,
    ANG_DEPTH    INTEGER
);

CREATE TABLE c4c1 (
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
    UPDT_DATE   INTEGER
);

CREATE TABLE c4c2 (
    RELATEID    TEXT    NOT NULL,
    CONSTYPE    CHAR,
    FROM_DEPTH  REAL,
    TO_DEPTH    REAL,
    DIAMETER    REAL,
    SLOT        REAL,
    LENGTH      REAL,
    MATERIAL    CHAR,
    AMOUNT      REAL,
    UNITS       CHAR
);

CREATE TABLE c4id (
    RELATEID    TEXT    NOT NULL,
    IDENTIFIER  TEXT    NOT NULL,
    ID_TYPE     TEXT,
    ID_PROG     TEXT
);

CREATE TABLE c4pl (
    RELATEID    TEXT    NOT NULL,
    PUMPTESTID  INTEGER,
    TEST_DATE   INTEGER,
    START_MEAS  REAL,
    FLOW_RATE   REAL,
    DURATION    REAL,
    PUMP_MEAS   REAL
);

CREATE TABLE c4rm (
    RELATEID    TEXT    NOT NULL,
    SEQ_NO      INTEGER,
    REMARKS     TEXT
);

CREATE TABLE c4st (
    RELATEID    TEXT    NOT NULL,
    DEPTH_TOP   REAL,
    DEPTH_BOT   REAL,
    DRLLR_DESC  TEXT,
    COLOR       TEXT,
    HARDNESS    TEXT,
    STRAT       TEXT,
    LITH_PRIM   TEXT,
    LITH_SEC    TEXT,
    LITH_MINOR  TEXT
);

CREATE TABLE c4wl (
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
    UPDT_DATE   INTEGER
);



