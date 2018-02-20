mod_def = {}

mod_def["LISTS"] = {
    "HEADER": "LIST",
    "NAME": "LISTS",
    "ROWNAME": ["LISTS_NAME"],
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["LISTS_NAME"],
    "INDEX": [],
    "UNIQUE": [["LISTS_NAME"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 1,
        "PARENT": [],
        "ICON": "list"
    },
    "AUTH": {
        "READ": 1,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "LIST",
            "NAME": "LISTS_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}

mod_def["LIST_ITEMS"] = {
    "HEADER": "ITEMS",
    "NAME": "LIST_ITEMS",
    "ROWNAME": ["LIST_ITEMS_NAME"],
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["LIST_ITEMS_LISTS_ID", "LIST_ITEMS_ORDER"],
    "INDEX": [],
    "UNIQUE": [["LIST_ITEMS_LISTS_ID", "LIST_ITEMS_NAME"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": ["LISTS"],
        "ICON": "key"
    },
    "AUTH": {
        "READ": 1,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "LIST ITEM",
            "NAME": "LIST_ITEMS_LISTS_ID",
            "HEADER": "LIST",
            "TYPE": "ID",
            "ID_API": "LISTS",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "LIST ITEM",
            "NAME": "LIST_ITEMS_NAME",
            "HEADER": "NAME",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "LIST ITEM",
            "NAME": "LIST_ITEMS_VALUE",
            "HEADER": "VALUE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "LIST ITEM",
            "NAME": "LIST_ITEMS_ENABLED",
            "HEADER": "ENABLED",
            "TYPE": "BOOL",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "NEW": 1,
            "DEFAULT": 0,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "LIST ITEM",
            "NAME": "LIST_ITEMS_ORDER",
            "HEADER": "ORDER",
            "TYPE": "FLOAT",
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "NEW": 0,
            "DEFAULT": 999.9,
            "AUTH": {
                "READ": 1,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
