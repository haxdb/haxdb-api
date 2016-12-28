apis = {}

apis["UDF"] = {
    "lists": [""],
    "cols": {
        "UDF_NAME": "STR",
        "UDF_TYPE": "STR",
        "UDF_LISTS_ID": "INT",
        "UDF_ORDER": "FLOAT",
        "UDF_CATEGORY": "STR",
        "UDF_ENABLED": "BOOL",
    },
    "query_cols": ["UDF_NAME", "UDF_TYPE", "UDF_ORDER", "UDF_CATEGORY", "UDF_ENABLED", "UDF_KEY"],
    "search_cols": ["UDF_CATEGORY", "UDF_NAME", "UDF_TYPE"],
    "order_cols": ["UDF_ORDER", "UDF_NAME"]
}
