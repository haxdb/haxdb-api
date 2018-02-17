mod_def = {}

mod_def["FILES"] = {
    "HEADER": "FILE",
    "NAME": "FILES",
    "ROWNAME": ["FILES_ID"],
    "NEW": 0,
    "UDF": 0,
    "ORDER": ["FILES_CONTEXT", "FILES_CONTEXT", "FILES_SUBCONTEXT"],
    "INDEX": [],
    "UNIQUE": [["FILES_CONTEXT", "FILES_CONTEXTID", "FILES_SUBCONTEXT"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": [],
        "ICON": "file"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "FILE",
            "NAME": "FILES_CONTEXT",
            "HEADER": "CONTEXT",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FILE",
            "NAME": "FILES_SUBCONTEXT",
            "HEADER": "SUBCONTEXT",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "FILE",
            "NAME": "FILES_CONTEXTID",
            "HEADER": "CONTEXTID",
            "TYPE": "INT",
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
            "CATEGORY": "FILE",
            "NAME": "FILES_DATA",
            "HEADER": "DATA",
            "TYPE": "FILE",
            "EDIT": 0,
            "QUERY": 0,
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
            "CATEGORY": "FILE",
            "NAME": "FILES_EXT",
            "HEADER": "EXT",
            "TYPE": "CHAR",
            "SIZE": 5,
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
            "CATEGORY": "FILE",
            "NAME": "FILES_MIMETYPE",
            "HEADER": "MIMETYPE",
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
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
