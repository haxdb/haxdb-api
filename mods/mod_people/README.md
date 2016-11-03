mod_people
===========

This module stores information about PEOPLE.  PEOPLE_COLUMNS may be defined and then values for those columns may be assigned to an PEOPLE entry and stored in PEOPLE_COLUMN_VALUES.


Database
--------

Creates the following tables:
- **PEOPLE**
- **PEOPLE_COLUMNS**
- **PEOPLE_COLUMN_VALUES**

Creates the following entries in *PEOPLE_COLUMNS*:  
- **FIRST_NAME**
- **LAST_NAME**
- **EMAIL**
- **DBA**
- **MEMBERSHIP**


API
---

- /PEOPLE/list
- /PEOPLE/new
- /PEOPLE/save
- /PEOPLE/delete
- /PEOPLE/download


- /PEOPLE_COLUMNS/list
- /PEOPLE_COLUMNS/categories
- /PEOPLE_COLUMNS/new
- /PEOPLE_COLUMNS/save
- /PEOPLE_COLUMNS/delete


