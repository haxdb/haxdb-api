apis = {}

apis["NODES"] = {
    "lists": [],
    "cols": {
        "NODES_PEOPLE_ID": "INT",
        "NODES_ASSETS_ID": "INT",
        "NODES_NAME": "STR",
        "NODES_DESCRIPTION": "STR",
        "NODES_IP": "STR",
        "NODES_EXPIRE": "INT",
        "NODES_READONLY": "BOOL",
        "NODES_DBA": "BOOL",
        "NODES_ENABLED": "BOOL",
        "NODES_QUEUED": "BOOL",
    },
    "query_cols": ["PEOPLE_NAME_LAST","PEOPLE_NAME_FIRST","NODES_NAME","NODES_EXPIRE","NODES_PEOPLE_ID","NODES_IP","NODES_READONLY","NODES_DBA","NODES_ENABLED","NODES_QUEUED"],
    "search_cols": ["PEOPLE_NAME_LAST","PEOPLE_NAME_FIRST","NODES_NAME","NODES_IP"],
    "order_cols": ["NODES_NAME"]
}

