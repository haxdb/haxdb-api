apis = {}

apis["FIELDSET"] = {
    "cols": {
        "FIELDSET_NAME": "STR",
        "FIELDSET_QUERY": "STR",
    },
    "udf_context": None,
    "udf_context_id": None,
    "udf_rowid": None,
    "query_cols": ["FIELDSET_NAME", "FIELDSET_ORDER"],
    "search_cols": ["FIELDSET_NAME", "FIELDSET_ORDER"],
    "order_cols": ["FIELDSET_ORDER", "FIELDSET_NAME"]
}

apis["QUERY"] = {
    "cols": {
        "QUERY_NAME": "STR",
        "QUERY_QUERY": "STR",
        "QUERY_ORDER": "INT",
    },
    "udf_context": None,
    "udf_context_id": None,
    "udf_rowid": None,
    "query_cols": ["QUERY_NAME", "QUERY_QUERY", "QUERY_ORDER"],
    "search_cols": ["QUERY_NAME", "QUERY_QUERY", "QUERY_ORDER"],
    "order_cols": ["QUERY_ORDER", "QUERY_NAME"]
}
