mod_def = {}

mod_def["QUERY"] = {
    "TABLE": "QUERY",
    "ROW_NAME": "QUERY_NAME",
    "NEW": 1",
    "UDF": 0,
    "ORDER": ["QUERY_ORDER", "QUERY_NAME"],
    "INDEX": [],
    "UNIQUE": [["QUERY_CONTEXT", "QUERY_PEOPLE_ID", "QUERY_NAME"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": None,
        "ICON": "search"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "QUERY",
            "NAME": "QUERY_NAME",
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
            "CATEGORY": "QUERY",
            "NAME": "QUERY_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "ID-API": "PEOPLE",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 500,
            }
        },
        {
            "CATEGORY": "QUERY",
            "NAME": "QUERY_CONTEXT",
            "HEADER": "CONTEXT",
            "TYPE": "CHAR",
            "SIZE": 25,
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 500,
            }
        },
        {
            "CATEGORY": "QUERY",
            "NAME": "QUERY_QUERY",
            "HEADER": "QUERY",
            "TYPE": "CHAR",
            "SIZE": 255,
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "QUERY",
            "NAME": "QUERY_ORDER",
            "HEADER": "ORDER",
            "TYPE": "FLOAT",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 9999.9
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
