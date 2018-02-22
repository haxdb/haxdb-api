mod_def = {}

mod_def["ASSETSENSORS"] = {
    "HEADER": "SENSORS",
    "NAME": "ASSETSENSORS",
    "ROWNAME": ["ASSETSENSORS_NAME"],
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["ASSETSENSORS_NAME"],
    "INDEX": [["ASSETSENSORS_ASSETS_ID"]],
    "UNIQUE": [],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": ["ASSETNODES"],
        "ICON": "dot-circle"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "NODE",
            "NAME": "ASSETSENSORS_NAME",
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
            "CATEGORY": "NODE",
            "NAME": "ASSETSENSORS_REFERENCE",
            "HEADER": "REFERENCE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
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
            "CATEGORY": "NODE",
            "NAME": "ASSETSENSORS_ASSETNODES_ID",
            "HEADER": "ASSET NODE",
            "TYPE": "ID",
            "ID_API": "ASSETNODES",
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
            "CATEGORY": "NODE",
            "NAME": "ASSETSENSORS_VAL",
            "HEADER": "VAL",
            "TYPE": "FLOAT",
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
    "CALLS": ["list", "view", "save", "new", "delete"]
}
