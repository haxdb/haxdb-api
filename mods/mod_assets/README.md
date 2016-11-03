mod_assets
===========

This module adds tables and api calls meant to store assets.


Database
--------

Creates the following tables:
- **ASSETS**
- **ASSET_LINKS**
- **ASSET_AUTHS**

Creates the following entry in *LISTS*:
- **ASSET LOCATIONS**

API
---

- /ASSETS/list
- /ASSETS/view
- /ASSETS/new
- /ASSETS/delete

- /ASSET_LINKS/list
- /ASSET_LINKS/new
- /ASSET_LINKS/save
- /ASSET_LINKS/delete

- /ASSET_AUTHS/list
- /ASSET_AUTHS/new
- /ASSET_AUTHS/delete
