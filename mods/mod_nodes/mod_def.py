mod_def = {}

mod_def["NODES"] = {
    "NAME": "NODES",
    "TABLE": "NODES",
    "ROWID": "NODES_ID",
    "CONTEXT_ROW": None,
    "COLS": [
        {
         "NAME": "NODES_API_KEY",
         "HEADER": "API_KEY",
         "TYPE": "ASCII",
         "EDIT": 0,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_NAME",
         "HEADER": "NAME",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_DESCRIPTION",
         "HEADER": "DESCRIPTION",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_READONLY",
         "HEADER": "READONLY",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_DBA",
         "HEADER": "DBA",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_IP",
         "HEADER": "IP",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_EXPIRE",
         "HEADER": "EXPIRE",
         "TYPE": "TIMESTAMP",
         "EDIT": 0,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_ENABLED",
         "HEADER": "ENABLED",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "NODES_QUEUED",
         "HEADER": "QUEUED",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
    ],
    "ORDER": ["NODES_NAME"]
}
