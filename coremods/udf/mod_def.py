mod_def = {}

mod_def["UDF"] = {
    "NAME": "UDF",
    "TABLE": "UDF",
    "ROW_NAME": "UDF_NAME",
    "UDF": 0,
    "NEW": 0,
    "ORDER": ["UDF_TABLE", "UDF_NUM"],
    "INDEX": [],
    "UNIQUE": [["UDF_TABLE", "UDF_NUM"], ["UDF_TABLE", "UDF_NAME"]],
    "CLIENT": {
        "NAME": "UDF",
        "MAJOR": 0,
        "MINOR": 1,
        "PARENT": None,
        "ICON": "database",
    },
    "AUTH": {
        "READ": 1,
        "WRITE": 1,
        "INSERT": 100,
        "DELETE": 100,
    }
    "COLS": [
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_TABLE",
         "HEADER": "TABLE",
         "TYPE": "CHAR",
         "SIZE": 25,
         "EDIT": 0,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 1,
            "WRITE": 1,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_NUM",
         "HEADER": "NUM",
         "TYPE": "INT",
         "SIZE": 2,
         "EDIT": 0,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 1,
            "WRITE": 1,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_CATEGORY",
         "HEADER": "CATEGORY",
         "TYPE": "CHAR",
         "SIZE": 25,
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 1,
            "WRITE": 1,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_NAME",
         "HEADER": "NAME",
         "TYPE": "CHAR",
         "SIZE": 50,
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 100,
            "WRITE": 100,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_TYPE",
         "HEADER": "TYPE",
         "TYPE": "SELECT",
         "OPTIONS": ["CHAR", "TEXT", "INT", "FLOAT", "BOOL", "LIST",
                     "ID", "FILE", "DATE", "TIMESTAMP"],
         "SIZE": 15,
         "EDIT": 0,
         "QUERY": 0,
         "SEARCH": 1,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": "CHAR",
         "NEW": 1,
         "AUTH": {
            "READ": 100,
            "WRITE": 100,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_LISTS_ID",
         "HEADER": "LIST",
         "TYPE": "ID",
         "ID_TABLE": "LISTS",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 100,
            "WRITE": 100,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_API",
         "HEADER": "API",
         "TYPE": "STR",
         "SIZE": 25,
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
         "INTERNAL": 0,
         "DEFAULT": None,
         "NEW": 0,
         "AUTH": {
            "READ": 100,
            "WRITE": 100,
         }
        },
        {
         "CATEGORY": "UDF",
         "NAME": "UDF_ENABLED",
         "HEADER": "ENABLED",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": 0,
         "NEW": 0,
         "AUTH": {
            "READ": 100,
            "WRITE": 100,
         }
        },
        {
         "CATEGORY": "AUTH",
         "NAME": "UDF_AUTH_READ",
         "HEADER": "AUTH READ",
         "TYPE": "INT",
         "SIZE": 5,
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": 100,
         "NEW": 0,
         "AUTH": {
            "READ": 200,
            "WRITE": 200,
         }
        },
        {
         "CATEGORY": "AUTH",
         "NAME": "UDF_AUTH_WRITE",
         "HEADER": "AUTH WRITE",
         "TYPE": "INT",
         "SIZE": 5,
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 1,
         "INTERNAL": 0,
         "DEFAULT": 100,
         "NEW": 0,
         "AUTH": {
            "READ": 200,
            "WRITE": 200,
         }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
