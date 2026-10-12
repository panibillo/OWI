# OWI Project Documentation

## General description

- A statewide database of wells is maintained by a consortium of Minnesota state agencies.
- The statewide database is named CWI.
- There is a public portal named MWI.
- CWI serves several purposes / user types:
    - Regulators, need a common source for well identity, location, and construction details.
    - Geologists, need a resource for drilling logs and their interpretations
    - Hydrogeologist, need a resource for static and dynamic water levels and well yield.
- Uses of CWI and MWI are constrained by limitations of their interfaces.
- OWI creates a local clone of the CWI database to overcome those limitations.

## The CWI database

- Data tables are named 'c5..'.  The previous versions were named 'c4..'.
- The main well table is c5ix.  
- The relational identifier for a well is 'wellid'.  It was formerly 'RELATEID'.
- Both wellid and RELATEID are equated with the public identifier "Minnesota Unique Well Number" (MNU)
- There are also a number of code tables for constants.

## The OWI identifier model and OWI versions

- The CWI identifier model fails when well records are de-duplicated and relational identifiers are lost.
    - Lost MNU identifiers are usually documented in table c5id
    - CWI does not enforce permanence or unique relationships of MNUs in its design
- OWI attempts to repair the identifier model in steps:
    - OWI version 3 (also 4.3) enforces permanence and uniqueness of MNU identifiers.
      It can fail from integrity errors when importing the existing CWI data.
    - OWI versions 0 to 2 (also 4.0 to 4.2) implement preparatory data cleanups, but do not enforce uniqueness of MNU identifiers
    - OWI version 40 is the first iteration of the MNU identifier model.
      It builds tables with the prefix 'o1' in addition to the c5 tables.
      It omits the unique constraints.
      'MUN' is an alternative abbreviation of 'MNU', the Minnesota Unique Well Number.
- Each version is a class in `src/OWI_config.py`.
- The active version is chosen near the bottom of `OWI_config.py`.
  The class `OWI_version` inherits from the chosen version class.
  The current choice is `OWI_version_40`.

## Running OWI

- This project runs inside the distrobox container `dbx-qgis`.
  The container provides the QGIS Python bindings.
- The virtual environment is `.venv-dbx`, in the project folder.
  Use `.venv-dbx/bin/python3` for all OWI scripts.
- From outside the container, prefix commands with `distrobox enter dbx-qgis --`.
- The entry point is `src/Run_new.py`.
  Steps are switched on and off with `if 1:` and `if 0:`.
- Run it from inside `src/`.
  The SQL file paths in `OWI_config.py` are relative, such as `../sql/...`.
- It stops if the output database already exists.
- Data directories are set in class `OWIfiles` in `OWI_config.py`.
- `demo_data/` holds small sample input files.
- There is no test suite.

## Credentials and outside services

- `src/OWI_logins.py` holds real FTP credentials.
  Never open it, print it, copy values from it, or add it to git.
- Never display credentials stored in the keyring.
- `RUN_download_cwi` contacts the state FTP server.
  Never run it without the User's explicit approval.

## AI assistance guidelines

Work in small, incremental steps.
Do not implement any new idea or new style without User's approval.
Do not commit without the User's approval.
Never push without the User's approval.

## Coding style

Copy my coding style. For example:
- Start each module with a docstring header: `'''Created on <date>` / `@author: bill'''`.
- Use `if 0:` and `if 1:` to switch blocks of code off and on.
- Import the configuration as `from OWI_config import OWI_version as C`.
Use OWI_sqlite.py for interacting with the database. (This may change, but not yet)
Avoid nesting list comprehensions.

## Writing style
Write clearly, using plain language, avoiding jargon.
Use U.S. English spelling.
Write in shorter declarative statements, building arguments logically step by step.
Pay attention to the ordering of arguments, the justification and validation of each statement.
Use hard linefeeds in LaTeX source, and in Python comments and docstrings, to separate each sentence or significant clause.
Do not break lines of Python code for this purpose.

## Always bound a long-running launch

**Never start a long-running process from an agent session without a wall-clock
cap.** Wrap it:

```bash
cd src && timeout -k 10 300 ../.venv-dbx/bin/python3 -u Run_new.py
```

`300` is the SIGTERM deadline in seconds; `-k 10` follows with SIGKILL ten
seconds later if the process ignores SIGTERM. Pick the number from what the run
should legitimately need, and prefer minutes over hours.

Why this is a rule and not a suggestion: In another project, an agent session launched
a python script as a background task and then ended. The process was reparented
to `systemd --user`, so nothing was left to stop it, and it burned 100% of a core
for four and a half days (4d16h of CPU, 59 billion `read()` calls, 1.0 GB RSS)
before anyone noticed. A test timeout would not have caught it — it was launched
as the *app*, not under a test runner. Only the shell-level cap closes that gap.

Two habits that go with it:

- **Add `-u`, or redirect to a file.** A killed process loses block-buffered
  stdout. The orphan above wrote a 0-byte log for four days because its output
  was still sitting in a pipe buffer, which destroyed the evidence.
- **Check for survivors before you finish.** `pgrep -af 'python3.*Run_new'`
  should come back empty.
