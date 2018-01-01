mod_def = {}

mod_def["FIELDSET"] = {
    "TABLE": "FIELDSET",
    "ROW_NAME": "FIELDSET_NAME",
    "NEW": 1",
    "UDF": 0,
    "ORDER": ["FIELDSET_ORDER", "FIELDSET_NAME"],
    "INDEX": [],
    "UNIQUE": [["FIELDSET_CONTEXT", "FIELDSET_PEOPLE_ID", "FIELDSET_NAME"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": None,
        "ICON": "columns"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "ID-API": "PEOPLE",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 500,
            }
        },
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_CONTEXT",
            "HEADER": "CONTEXT",
            "TYPE": "CHAR",
            "SIZE": 25,
            "NEW": 1,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_COLS",
            "HEADER": "COLS",
            "TYPE": "TEXT",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FIELDSET",
            "NAME": "FIELDSET_ORDER",
            "HEADER": "ORDER",
            "TYPE": "FLOAT",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 9999.9,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
