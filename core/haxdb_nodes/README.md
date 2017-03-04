mod_nodes
===========

This module provides connectivity to the the API.  We define anything that connects to the API using an api_key as a node.  An api_key is automatically created and assigned to a node upon it's creation.


Database
--------

Creates the following tables:
- **NODES**


API
---

- /NODES/list
- /NODES/new
- /NODES/save
- /NODES/delete
