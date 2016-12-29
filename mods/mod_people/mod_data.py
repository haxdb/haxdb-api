mdata = {}

mdata["PEOPLE"] = {
    "COLS": [
        {"ORDER": 0.1,
         "NAME": "PEOPLE_NAME_FIRST",
         "HEADER": "FIRST",
         "TYPE": "STR"
         },
    ]
}


apis = {}

apis["PEOPLE"] = {
    "lists": ["MEMBERSHIPS", ],
    "cols": {
        "PEOPLE_NAME_FIRST": "STR",
        "PEOPLE_NAME_LAST": "STR",
        "PEOPLE_EMAIL": "STR",
        "PEOPLE_DBA": "STR",
        "PEOPLE_MEMBERSHIP": "STR",
        "PEOPLE_ACTIVE": "BOOL",
    },
    "udf_context": "PEOPLE",
    "udf_context_id": None,
    "udf_rowid": "PEOPLE_ID",
    "query_cols": ["PEOPLE_ID", "PEOPLE_NAME_FIRST", "PEOPLE_NAME_LAST", "PEOPLE_EMAIL", "PEOPLE_DBA", "PEOPLE_MEMBERSHIP", "PEOPLE_ACTIVE"],
    "search_cols": ["PEOPLE_NAME_FIRST", "PEOPLE_NAME_LAST", "PEOPLE_EMAIL", "PEOPLE_MEMBERSHIP"],
    "order_cols": ["PEOPLE_NAME_LAST", "PEOPLE_NAME_FIRST"]
}
