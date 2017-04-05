mod_udf
===========

This module provides User Defined Fields for any table that table's mod provides configuration.
The table stores context (usually table name) and context_id (0 if not needed).

Once a column is created for a certain context data can then be saved to that column by calling the appropriate /save api call.
Data saved to a udf will be returned from the appropriate /list and /view calls.


Database
--------

Creates the following tables:
- **UDF**
- **UDF_DATA**


API
---

- /UDF/list
- /UDF/new
- /UDF/save
- /UDF/delete
