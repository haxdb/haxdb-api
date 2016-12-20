mod_rfid
===========

This module provides API calls to facilitate authorization to assets based on RFID values.  

It provides an api to access rfid settings/attributes for ASSETS.

It provies an api to store rfid keys for PEOPLE.

It provides a pulse command which asset nodes can call to with the current read rfid (or none if no rfid) and then react based on the return value.  If node is not registered and a dba rfid is provided the node will then be registered in the queue.  If the node is registered (and active) then success will return with a 1 (if the asset should be powered) or 0 (if it should not be powered).  message will be returned with either the asset's status or an appropriate message about authorization.


Database
--------

Creates the following tables:
 - ASSETS_RFID
 - PEOPLE_RFID

Creates the following *LISTS*:
 - ASSET STATUSES

Creates the following *LIST_ITEMS* for the LIST *ASSET STATUSES*:
 - OPERATIONAL
 - BORKEN

API
---

- /ASSETS_RFID/pulse

- /ASSETS_RFID/list
- /ASSETS_RFID/view
- /ASSETS_RFID/save

- /PEOPLE_RFID/list
- /PEOPLE_RFID/new
- /PEOPLE_RFID/save
- /PEOPLE_RFID/delete
