mod_def = {}

mod_def["AUTHTOKEN"] = {
    "NAME": "AUTHTOKEN",
    "TABLE": "AUTHTOKEN",
    "PARENT_TABLE": None,
    "ROW_NAME": None,
    "DEFAULT_COLS": ["AUTHTOKEN_TOKEN",
                     "AUTHTOKEN_PEOPLE_ID",
                     "AUTHTOKEN_EXPIRE"],
    "UDF": {},
    "ORDER": [],
    "INDEX": [],
    "UNIQUE": [["AUTHTOKEN_TOKEN"]],
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
            "ID": "PEOPLE"
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
    }
}
