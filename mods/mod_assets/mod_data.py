apis = {}

apis["ASSETS"] = {
    "lists": ["ASSET LOCATIONS"],
    "cols": {
    "ASSETS_NAME": "STR",
    "ASSETS_TYPE": "STR",
    "ASSETS_MANUFACTURER": "STR",
    "ASSETS_PRODUCT_ID": "STR",
    "ASSETS_SERIAL_NUMBER": "STR",
    "ASSETS_QUANTITY": "INT",
    "ASSETS_LOCATION": "STR",
    "ASSETS_DESCRIPTION": "STR",
    },
    "query_cols": ["ASSETS_NAME","ASSETS_TYPE","ASSETS_MANUFACTURER","ASSETS_PRODUCT_ID","ASSETS_SERIAL_NUMBER","ASSETS_QUANTITY", "ASSETS_LOCATION", "ASSETS_DESCRIPTION"],
    "search_cols": ["ASSETS_NAME","ASSETS_TYPE","ASSETS_MANUFACTURER","ASSETS_PRODUCT_ID","ASSETS_SERIAL_NUMBER", "ASSETS_LOCATION", "ASSETS_DESCRIPTION"],
    "order_cols": ["ASSETS_LOCATION","ASSETS_NAME"]
}

apis["ASSET_LINKS"] = {
    "lists": [],
    "cols": {
        "ASSET_LINKS_NAME": "STR",
        "ASSET_LINKS_LINK": "STR",
        "ASSET_LINKS_ORDER": "FLOAT",
    },
    "query_cols": ["ASSET_LINKS_NAME","ASSET_LINKS_LINK","ASSET_LINKS_ORDER"],
    "search_cols": ["ASSET_LINKS_NAME","ASSET_LINKS_LINK"],
    "order_cols": ["ASSET_LINKS_ORDER","ASSET_LINKS_NAME"],
}

apis["ASSET_AUTHS"] = {
    "lists": [],
    "cols": {
    },
    "query_cols": ["PEOPLE_NAME_LAST","PEOPLE_NAME_FIRST"],
    "search_cols": ["PEOPLE_NAME_LAST","PEOPLE_NAME_FIRST"],
    "order_cols": ["PEOPLE_NAME_LAST","PEOPLE_NAME_FIRST",],
}