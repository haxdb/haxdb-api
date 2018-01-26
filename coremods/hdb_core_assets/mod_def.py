mod_def = {}

mod_def["ASSETS"] = {
    "NAME": "ASSETS",
    "ROW_NAME": "ASSETS_NAME",
    "NEW": 1,
    "UDF": 20,
    "ORDER": ["ASSETS_LOCATION, ASSETS_NAME"],
    "INDEX": [["ASSETS_LOCATION", "ASSETS_NAME"]],
    "UNIQUE": [["ASSETS_NAME"]],
    "CLIENT": {
        "MAJOR": 1,
        "MINOR": 0,
        "PARENT": None,
        "ICON": "key"
    },
    "AUTH": {
        "READ": 0,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": "NEW ASSET",
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_TYPE",
            "HEADER": "TYPE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": "WIDGET",
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_MANUFACTURER",
            "HEADER": "MANUFACTURER",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_MODEL",
            "HEADER": "MODEL",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_PRODUCT_ID",
            "HEADER": "PRODUCT ID",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_SERIAL_NUMBER",
            "HEADER": "SERIAL NUMBER",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_QUANTITY",
            "HEADER": "QTY",
            "TYPE": "INT",
            "SIZE": 10,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "NEW": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_LOCATION",
            "HEADER": "LOCATION",
            "TYPE": "LIST",
            "LIST_NAME": "ASSET LOCATIONS",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET",
            "NAME": "ASSETS_DESCRIPTION",
            "HEADER": "DESCRIPTION",
            "TYPE": "TEXT",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}

mod_def["ASSETURLS"] = {
    "NAME": "ASSETURLS",
    "ROW_NAME": "ASSETURLS_NAME",
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["ASSETURLS_ORDER", "ASSETURLS_NAME"],
    "INDEX": [],
    "UNIQUE": [["ASSETURLS_ASSETS_ID", "ASSETURLS_URL"],
               ["ASSETURLS_ASSETS_ID", "ASSETURLS_NAME"],
              ],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": "ASSETS",
        "ICON": "link",
    },
    "AUTH": {
        "READ": 1,
        "WRITE": 1,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "ASSET URL",
            "NAME": "ASSETURLS_ASSETS_ID",
            "HEADER": "ASSET",
            "TYPE": "ID",
            "API_ID": "ASSETS",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 1,
                "WRITE": 1,
            }
        },
        {
            "CATEGORY": "ASSET URL",
            "NAME": "ASSETURLS_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": "NEW URL",
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET URL",
            "NAME": "ASSETURLS_URL",
            "HEADER": "URL",
            "TYPE": "CHAR",
            "SIZE": 255,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET URL",
            "NAME": "ASSETURLS_ORDER",
            "HEADER": "ORDER",
            "TYPE": "FLOAT",
            "SIZE": 10,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "NEW": 0,
            "DEFAULT": 999.0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}

mod_def["ASSETAUTHS"] = {
    "NAME": "ASSETAUTHS",
    "ROW_NAME": "CALC_ASSETAUTHS_PEOPLE_ID",
    "NEW": 0,
    "UDF": 0,
    "ORDER": ["CALC_ASSETAUTHS_PEOPLE_ID"],
    "INDEX": [],
    "UNIQUE": [["ASSETAUTHS_ASSETS_ID", "ASSETAUTHS_PEOPLE_ID"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": "NODES",
        "ICON": "lock",
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "ASSET AUTH",
            "NAME": "ASSETAUTHS_ASSETS_ID",
            "HEADER": "ASSET",
            "TYPE": "ID",
            "API_ID": "ASSETS",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET AUTH",
            "NAME": "ASSETAUTHS_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "API_ID": "PEOPLE",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSET AUTH",
            "NAME": "ASSETAUTHS_ENABLED",
            "HEADER": "ENABLED",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "DEFAULT": 0,
            "NEW": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
