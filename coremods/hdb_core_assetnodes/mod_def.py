mod_def = {}

mod_def["ASSETNODES"] = {
    "HEADER": "ASSET NODES",
    "NAME": "ASSETNODES",
    "ROWNAME": ["ASSETNODES_NAME"],
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["ASSETNODES_NAME"],
    "INDEX": [["ASSETNODES_ASSETS_ID"]],
    "UNIQUE": [["ASSETNODES_API_KEY"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 1,
        "PARENT": ["ASSETS"],
        "ICON": "cube"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_API_KEY",
            "HEADER": "API KEY",
            "TYPE": "CHAR",
            "SIZE": 50,
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
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_IP",
            "HEADER": "IP",
            "TYPE": "CHAR",
            "SIZE": 20,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_ASSETS_ID",
            "HEADER": "ASSET",
            "TYPE": "ID",
            "ID_API": "ASSETS",
            "EDIT": 1,
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
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_ENABLED",
            "HEADER": "ENABLED",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_RESTRICTED",
            "HEADER": "RFID REQUIRED",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_APPROVAL",
            "HEADER": "APPROVAL REQUIRED",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_PEOPLE_ID",
            "HEADER": "OPERATOR",
            "TYPE": "ID",
            "ID_API": "PEOPLE",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "delete", "register",
              "pulse", "sense", "auth"]
}
