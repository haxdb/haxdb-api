mod_def = {}

mod_def["NODES"] = {
    "NAME": "NODES",
    "ROWNAME": "NODES_NAME",
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["NODES_NAME"],
    "INDEX": [],
    "UNIQUE": [],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 1,
        "PARENT": None,
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
            "CATEGORY": "NODE",
            "NAME": "NODES_API_KEY",
            "HEADER": "API_KEY",
            "TYPE": "CHAR",
            "SIZE": 50,
            "EDIT": 0,
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
            "CATEGORY": "NODE",
            "NAME": "NODES_NAME",
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
            "NAME": "NODES_DBA",
            "HEADER": "DBA",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 99999,
            }
        },
        {
            "CATEGORY": "NODE",
            "NAME": "NODES_IP",
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
            "CATEGORY": "NODE",
            "NAME": "NODES_EXPIRE",
            "HEADER": "EXPIRE",
            "TYPE": "TIMESTAMP",
            "EDIT": 1,
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
        {
            "CATEGORY": "NODE",
            "NAME": "NODES_ENABLED",
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
            "CATEGORY": "RELATIONSHIP",
            "NAME": "NODES_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "ID_API": "PEOPLE",
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
            "CATEGORY": "RELATIONSHIP",
            "NAME": "NODES_ASSETS_ID",
            "HEADER": "ASSET",
            "TYPE": "ID",
            "ID_API": "ASSETS",
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
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
