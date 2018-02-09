mod_def = {}

mod_def["ASSETNODES"] = {
    "HEADER": "ASSET NODES",
    "NAME": "ASSETNODES",
    "ROWNAME": "ASSETNODES_NAME",
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["ASSETNODES_NAME"],
    "INDEX": [["ASSETNODES_ASSETS_ID"]],
    "UNIQUE": [["ASSETNODES_NODES_ID"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": ["NODES", "ASSETS"],
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
            "NAME": "ASSETNODES_ASSETS_ID",
            "HEADER": "ASSET",
            "TYPE": "ID",
            "ID_API": "ASSETS",
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
            "CATEGORY": "ASSETNODE",
            "NAME": "ASSETNODES_NODES_ID",
            "HEADER": "NODE",
            "TYPE": "ID",
            "ID_API": "NODES",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "delete"]
}
