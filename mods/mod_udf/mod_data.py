apis = {}

apis["UDF_DEF"] = {
    "lists": [""],
    "cols": {
    "UDF_DEF_NAME": "STR",
    "UDF_DEF_TYPE": "STR",
    "UDF_DEF_LISTS_ID": "INT",
    "UDF_DEF_ORDER": "FLOAT",
    "UDF_DEF_CATEGORY": "STR",
    "UDF_DEF_ENABLED": "BOOL",
    "UDF_DEF_KEY": "BOOL",
    },
    "query_cols": ["UDF_DEF_NAME","UDF_DEF_TYPE","UDF_DEF_ORDER","UDF_DEF_CATEGORY","UDF_DEF_ENABLED","UDF_DEF_KEY"],
    "search_cols": ["UDF_DEF_NAME", "UDF_DEF_TYPE"],
    "order_cols": ["UDF_DEF_ORDER","UDF_DEF_NAME"]
}

apis["UDF_DATA"] = {
    "lists": [],
    "cols": {
        "UDF_DATA_ROWID": "INT",
        "UDF_DATA_VALUE": "STR",
    },
    "query_cols": ["UDF_DATA_VALUE"],
    "search_cols": ["UDF_DATA_VALUE"],
    "order_cols": ["UDF_DATA_VALUE"],
}