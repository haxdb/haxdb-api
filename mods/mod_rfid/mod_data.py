apis = {}

apis["ASSETS_RFID"] = {
    "lists": [],
    "cols": {
        "ASSETS_RFID_AUTO_LOG": "BOOL",
        "ASSETS_RFID_REQUIRE_AUTH": "BOOL",
        "ASSETS_RFID_AUTH_TIMEOUT": "INT",
        "ASSETS_RFID_AUTH_PEOPLE_ID": "INT",
        "ASSETS_RFID_AUTH_START": "INT",
        "ASSETS_RFID_AUTH_LAST": "INT",
        "ASSETS_RFID_STATUS": "STR",
        "ASSETS_RFID_STATUS_DESC": "STR",        
    },
    "required": [],
    "query_cols": ["ASSETS_RFID_AUTO_LOG","ASSETS_RFID_REQUIRE_AUTH","ASSETS_RFID_AUTH_TIMEOUT","ASSETS_RFID_AUTH_PEOPLE_ID","ASSETS_RFID_AUTH_START","ASSETS_RFID_AUTH_LAST","ASSETS_RFID_STATUS","ASSETS_RFID_STATUS_DESC","PEOPLE_FIRST_NAME","PEOPLE_LAST_NAME"],
    "search_cols": ["ASSETS_RFID_STATUS","ASSETS_RFID_STATUS_DESC","PEOPLE_FIRST_NAME","PEOPLE_LAST_NAME"],
    "order_cols": ["ASSETS_RFID_STATUS"]
}

apis["PEOPLE_RFID"] = {
    "lists": [],
    "cols": {
        "PEOPLE_RFID_RFID": "STR",
    },
    "required": [],
    "query_cols": ["PEOPLE_RFID_PEOPLE_ID","PEOPLE_RFID_RFID"],
    "search_cols": ["PEOPLE_LAST_NAME","PEOPLE_FIRST_NAME","PEOPLE_RFID_RFID"],
    "order_cols": ["PEOPLE_LAST_NAME", "PEOPLE_FIRST_NAME"],
}