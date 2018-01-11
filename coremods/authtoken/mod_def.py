mod_def = {}

mod_def["AUTHTOKEN"] = {
    "TABLE": "AUTHTOKEN",
    "ROW_NAME": "AUTHTOKEN_TOKEN",
    "UDF": 0,
    "ORDER": [],
    "INDEX": [],
    "UNIQUE": [["AUTHTOKEN_TOKEN"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 1,
        "PARENT": None,
        "ICON": "key"
    },
    "COLS": [
        {
            "CATEGORY": "AUTHTOKEN",
            "NAME": "AUTHTOKEN_TOKEN",
            "HEADER": "TOKEN",
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
                "WRITE": 500,
            }
        },
        {
            "CATEGORY": "AUTHTOKEN",
            "NAME": "AUTHTOKEN_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "API_ID": "PEOPLE",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 500,
            }
        },
        {
            "CATEGORY": "AUTHTOKEN",
            "NAME": "AUTHTOKEN_EXPIRE",
            "HEADER": "EXPIRE",
            "TYPE": "TIMESTAMP",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 500,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
