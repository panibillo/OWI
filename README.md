# OWI

An SQLite implementation of the Minnesota County Well Index (CWI) database. 

(Alternatively called OWIsqlite)

## Description

The purpose of this project is to replicate a functional CWI database using SQLite.
The target audience is persons or programs who have permission to download data from the CWI ftp website maintained by the Minnesota Geologic Survey.
Major project components include:
* A database class that interfaces to pysqlite3, implementing a context manager.
* A script to automate downloading and unzipping of files from an ftp site.
* A script to automate importing of the downloaded files into the sqlite database.
* A public config file defining paths, schema versions, and files.
* A non-public config file defining the download site and logins.

The initial software versions are suitable only for building a local database from scratch. There is no functionality for maintaining a local database by adding only new records or for updating only changed records.

This project defines both software versions and schema versions for the database.

The sqlite database is implemented in several schema versions. Each version is defined by a schema file (DDL file) in subdirectory sql.

The schema version numbering system for the different schemas remains tentative.  
Originally, all versions are identified as c4.[S].[V]  where S distinguishes major differences in the schema, and V distinguishes minor differences in the schema.

An outline of current versions is provided in cwischema_c4_versions.txt.

The user is responsible for obtaining the instructions and credentials for downloading the source data files from the source ftp site. Alternatively the user can obtain copies of the files another way, and skip the ftp download part of the scripts.

## Getting Started

### Dependencies

* Python >= 3.12

Standard library modules used include sqlite3, ftplib, zipfile and csv.

Third-party libraries (listed in `requirements.txt`):
* pyshp (imported as `shapefile`, for reading shape files)
* requests and beautifulsoup4 (scraping the CWI code tables)
* keyring (storing logins)
* distro
* openpyxl (only for converting .xlsx files to .csv)

Optional: `src/gpkg_tools.py` uses the QGIS Python bindings (`qgis.core`). QGIS is not
needed for anything else. It cannot be installed with pip; it comes from the OS
packages or the QGIS installer. See Setup B under Installing.

The following modules need to be installed in your environment(via pip)
* pyshp
* pandas 

This project is tested on Windows 10 and Ubuntu 20.04

### Installing

* Download the project files from GitHub.  Open a git Bash window and navigate to the parent folder where you want to install it. Then on the Bash line enter:

	git clone https://github.com/panibillo/OWI.git 

* Create a virtual environment in the project folder and install the libraries.
  Choose one of the two setups below.
  Folders named `.venv*` are ignored by git.
  Install the libraries only into the virtual environment. Never use `sudo pip` or `--break-system-packages`.

**Setup A: without QGIS.** Use this if you do **not** intend to import the `qgis` library (for example, to run `src/gpkg_tools.py`).

	Linux:

		python3.12 -m venv .venv
		.venv/bin/pip install -r requirements.txt

	Windows:

		py -3.12 -m venv .venv
		.venv\Scripts\pip install -r requirements.txt

**Setup B: with QGIS, in a distrobox (Linux).** Use this if you intend to import the `qgis` library.
  The QGIS Python bindings cannot be installed with pip.
  They must come from the system packages, so QGIS is installed inside a distrobox container, and the venv is allowed to see the container's system packages.
  The author's container is named `dbx-qgis`. It runs Ubuntu 24.04, with QGIS LTR installed from the QGIS repository `https://qgis.org/ubuntu-ltr`.
  See https://qgis.org/resources/installation-guide/ for the steps to add that repository.

		distrobox create --name dbx-qgis --image ubuntu:24.04
		distrobox enter dbx-qgis
		# inside the container: add the QGIS repository, then
		sudo apt install qgis python3-qgis python3-venv
		python3 -m venv --system-site-packages --prompt="owi@dbx" .venv-dbx
		.venv-dbx/bin/pip install -r requirements.txt
		.venv-dbx/bin/python3 -c "import qgis.core"   # should print nothing

  Run OWI scripts inside the container with `.venv-dbx/bin/python3`.
  From outside the container, prefix the command with `distrobox enter dbx-qgis --`.

* You are reponsible for getting instructions and credentials for downloading the data files from the ftp site. The needed information is described in file `OWI_logins__template.py`.  Make a copy of that file named `OWI_logins.py` and enter the information using normal Python syntax.  Do not share that file, and do not add to this repository.

Edit the file `OWI_config.py`:

* Create the needed folders, and adjust the paths in the config file.  It needs a little under 2 Gigabits to download and unzip the data, and create the database from scratch.  The script has been tested only running it with all manipulated folders defined on a RAM drive of 2Gigabyte size. *Backup your local version of this file, because it is part of the repo and git may overwrite your version!* 

* Select the version of the database schema that you wish to install by editing the if.. block naming the schemas.  The git repo is tagged with working schema versions.  As of Oct 20, 2021, the only tag is for version c4.3.0, which can be checked out with the tag name schema3.  That should work for schemas 0, 1, and 2 as well.  Schema 4 is still in development.  The schemas are briefly described in file `sql/cwischema_c4_versions.txt`, and are individually defined in the DDL files `cwischema_c4.V.v.sql`

	git checkout schema3 

### Executing program

Prepare for execution:

* Ensure that OWI_config.py and OWI_logins.py exist and have been edited for your installation.

* Ensure that there is sufficient disk space for downloading the data files, extracting the zip files, and creating the database from scratch.  That will take less than 2Gigabytes of disk space (as little as 1.7G?).

* Run the script

	Run_new.py

* If re-running the program with *data=True*, you must either:
    * first delete the existing database file, or
    * first delete the data in the affected tables.

* You can re-enter the scripts after partial completion, by editing and running either `OWI_import_csv.py` or `OWI_download_ftp.py`.  Depending on where you re-enter, you may not need to be delete the database - but you must know what you are doing to prevent duplicating data. 

* If you create the database on a RAM drive, you may want to save the finished database to a physical drive for later use. 


## Authors

William Olsen

## Version History

* Software version 0.1 
    * Initial Release, git tag `schema3`  
      * Schema versions c4.0.0 through c4.3.0 are working. 
      * Schema version c4.4.0 is partially working.  
      * Schema version c4.4.1 fails because of data constraint violations in the source data (as of October, 2023).


## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

The CWI database and the MWI website have been developed and maintained by many remarkable people who are remarkably dedicated to preserving and sharing well data in Minnesota.  These are maintained primarily by the Minnesota Geologic Survey and the Minnesota Department of Health, and with the help of numerous others. 
* [MWI map interface](https://mnwellindex.web.health.state.mn.us/)
* [MWI text search](https://mnwellindex.web.health.state.mn.us/mwi/)
* [CWI documentation](http://mgsweb2.mngs.umn.edu/cwi_doc/cwidoc.htm)