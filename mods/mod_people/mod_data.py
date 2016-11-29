apis = {}

apis["PEOPLE"] = {
    "lists": [],
    "cols": {
    "PEOPLE_NAME_FIRST": "STR",
    "PEOPLE_NAME_LAST": "STR",
    "PEOPLE_EMAIL": "STR",
    "PEOPLE_DBA": "STR",
    },
    "udf_context": "PEOPLE",
    "udf_context_id": None,
    "udf_rowid": "PEOPLE_ID",
    "query_cols": ["PEOPLE_NAME_FIRST", "PEOPLE_NAME_LAST", "PEOPLE_EMAIL", "PEOPLE_DBA"],
    "search_cols": ["PEOPLE_NAME_FIRST", "PEOPLE_NAME_LAST", "PEOPLE_EMAIL"],
    "order_cols": ["PEOPLE_NAME_LAST", "PEOPLE_NAME_FIRST"]
}

