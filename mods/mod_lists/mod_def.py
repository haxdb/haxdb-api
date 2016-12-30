mod_def = {}

mod_def["LISTS"] = {
    "NAME": "LISTS",
    "TABLE": "LISTS",
    "ROWID": "LISTS_ID",
    "COLS": [
        {
         "NAME": "LISTS_NAME",
         "HEADER": "NAME",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 1,
        },
        {
         "NAME": "LISTS_INTERNAL",
         "HEADER": "INTERNAL",
         "TYPE": "BOOL",
         "EDIT": 0,
         "QUERY": 0,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
    ],
    "ORDER": ["LISTS_NAME"]
}

mod_def["LIST_ITEMS"] = {
    "NAME": "LIST_ITEMS",
    "TABLE": "LIST_ITEMS",
    "ROWID": "LIST_ITEMS_ID",
    "CONTEXT_ROW": "LIST_ITEMS_LISTS_ID",
    "COLS": [
        {
         "NAME": "LIST_ITEMS_VALUE",
         "HEADER": "VALUE",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 1,
        },
        {
         "NAME": "LIST_ITEMS_DESCRIPTION",
         "HEADER": "DESCRIPTION",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "LIST_ITEMS_ENABLED",
         "HEADER": "ENABLED",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 0,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "LIST_ITEMS_ORDER",
         "HEADER": "ORDER",
         "TYPE": "FLOAT",
         "EDIT": 1,
         "QUERY": 0,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "LIST_ITEMS_INTERNAL",
         "HEADER": "INTERNAL",
         "TYPE": "BOOL",
         "EDIT": 0,
         "QUERY": 0,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
    ]
    "ORDER": ["LIST_ITEMS_ORDER", "LIST_ITEMS_NAME"]
}
