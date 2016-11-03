mod_rfid
===========

This module provides API calls to facilitate authorization to assets based on RFID values.  

A register API call is added that will create a queued node and return an api_key.  If that node is then activated the api_key can be used to access the API.  This allows you to deploy RFID nodes without hardcoding api_keys for each one.

Once a node is created it can be assigned an asset.  The auth call can use the RFID value passed to match an entry from PEOPLE and see if they are also authorized to use the nodes assigned asset (entry in ASSET_AUTHS).


Database
--------

Creates the following entries in *PEOPLE_COLUMNS*: 
- **RFID**

Creates the following *LIST_ITEMS* for the *LISTS* entry *LOG ACTIONS*: 
- **AUTHENTICATE**
- **DENY**
- **ACTIVATE**
- **REGISTER**
- **DEACTIVATE**


API
---

- /RFID/asset/auth
- /RFID/asset/register
