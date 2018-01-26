mod_def = {}

mod_def["MEMBERSHIPS"] = {
    "NAME": "MEMBERSHIPS",
    "ROW_NAME": ["MEMBERSHIPS_NAME"],
    "NEW": 1,
    "UDF": 10,
    "INDEX": [],
    "UNIQUE": [["MEMBERSHIPS_NAME"]],
    "CLIENT": {
        "MAJOR": 1,
        "MINOR": 0,
        "PARENT": None,
        "ICON": "id-card-o"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "MEMBERSHIP",
            "NAME": "MEMBERSHIPS_NAME",
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
            "CATEGORY": "MEMBERSHIP",
            "NAME": "MEMBERSHIPS_ACTIVE",
            "HEADER": "ACTIVE MEMBER",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "MEMBERSHIP",
            "NAME": "MEMBERSHIPS_RFID",
            "HEADER": "RFID",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
