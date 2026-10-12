"""
A driver to create a fresh local copy of cwi from scratch

Purpose
-------
    o   Create an all new sqlite database to mirror the CWI database as served
        on the Minnesota Geologic Survey ftp site as the c5 data tables
    o   Download selected .zip files if the ftp site versions are newer
    o   Unzip any newer .zip files that have been downloaded
    o   Create or re-create the target sqlite database using a specified schema
    o   Import the unzipped data to the sqlite database
Authors
-------
    William C. Olsen
    panibillo at gmail.com

Version
-------
    2021-10-14
"""
import os
import argparse
import logging

from OWI_download_ftp import RUN_download_cwi
from OWI_import_csv import RUN_import_csv, RUN_import_swuds

# Import the OWI version selected in OWI_config.py
from OWI_config import  OWI_version as C
# Alternatively import a specific version by name, e.g.:
# from OWI_config import  OWI_version_42 as C

from OWI_config import versioninfo

# Options used when they are not given on the command line.
# They are the defaults of the command line options.
# Edit them here to run without command line options, e.g. from Eclipse.
OPT_LOG = "INFO"
OPT_DRY_RUN = False
OPT_SKIP_DOWNLOAD = True
OPT_SKIP_IMPORT_CSV = False
OPT_SKIP_IMPORT_SWUDS = True
OPT_OVERWRITE_EXISTING_DB = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a fresh local copy of cwi from scratch"
    )
    parser.add_argument(
        "--log",
        type=str,
        default=OPT_LOG,
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=OPT_DRY_RUN,
        help="Display run configuration",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        default=OPT_SKIP_DOWNLOAD,
        help="Skip the download step",
    )
    parser.add_argument(
        "--skip-import-csv",
        action="store_true",
        default=OPT_SKIP_IMPORT_CSV,
        help="Skip the import csv step",
    )
    parser.add_argument(
        "--skip-import-swuds",
        action="store_true",
        default=OPT_SKIP_IMPORT_SWUDS,
        help="Skip the import swuds step",
    )
    parser.add_argument(
        "--overwrite-existing-db",
        action="store_true",
        default=OPT_OVERWRITE_EXISTING_DB,
        help="Overwrite existing database if it exists",
    )
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log.upper(), None))

    logging.debug(f"Starting Run_new with args: {args}")

    print(versioninfo(C)) 
    if args.dry_run:
        exit()

    if os.path.exists(C.OWI_DOWNLOAD_DB_NAME):
        if args.overwrite_existing_db:
            logging.info (f"Overwriting existing database file:\n{C.OWI_DOWNLOAD_DB_NAME}")
            os.remove(C.OWI_DOWNLOAD_DB_NAME)
        else:
            logging.fatal(f"the file should not exist before running:\n{C.OWI_DOWNLOAD_DB_NAME}")
            exit(1)

    if 1:
        print(versioninfo(C))

    try:

        if not args.skip_download:
            RUN_download_cwi(C)

        if not args.skip_import_csv:
            RUN_import_csv(C)

        if not args.skip_import_swuds:
            RUN_import_swuds()

        print ("/////////// DONE with Run_new.py ////////////")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.fatal(e)
