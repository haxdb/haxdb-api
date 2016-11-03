mod_logs
===========

This module provides tables and api for logging actions.  The node used to make log entries is detected by the api_key used.  If the node is tied to an asset then that information is also stored.


Database
--------

Creates the following tables:
- **LOGS**

Creates the following entries in *LISTS*: 
- **LOG ACTIONS**


API
---

- /LOGS/list
- /LOGS/new
