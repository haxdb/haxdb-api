mod_def = {}

mod_def["PEOPLE"] = {
    "TABLE": "PEOPLE",
    "ROW_NAME": ["PEOPLE_NAME_FIRST", "PEOPLE_NAME_LAST"],
    "NEW": 1,
    "UDF": 20,
    "ORDER": ["PEOPLE_NAME_LAST", "PEOPLE_NAME_FIRST"],
    "INDEX": [],
    "UNIQUE": [["PEOPLE_NAME_LAST", "PEOPLE_NAME_FIRST", "PEOPLE_EMAIL"]],
    "CLIENT": {
        "MAJOR": 1,
        "MINOR": 0,
        "PARENT": None,
        "ICON": "user"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "PERSON",
            "NAME": "PEOPLE_NAME_FIRST",
            "HEADER": "FIRST NAME",
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
            "CATEGORY": "PERSON",
            "NAME": "PEOPLE_NAME_LAST",
            "HEADER": "LAST NAME",
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
            "CATEGORY": "PERSON",
            "NAME": "PEOPLE_EMAIL",
            "HEADER": "EMAIL",
            "TYPE": "CHAR",
            "SIZE": 50,
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
            "CATEGORY": "PERSON",
            "NAME": "PEOPLE_MEMBERSHIP",
            "HEADER": "MEMBERSHIP",
            "TYPE": "ID",
            "API_ID": "MEMBERSHIPS",
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
            "CATEGORY": "PERSON",
            "NAME": "PEOPLE_DBA",
            "HEADER": "DBA",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 9999,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
