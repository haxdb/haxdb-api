apis = {}

apis["LISTS"] = {
    "lists": [],
    "cols": {
    "LISTS_NAME": "STR",
    },
    "required": ["LISTS_NAME"],
    "query_cols": ["LISTS_NAME"],
    "search_cols": ["LISTS_NAME"],
    "order_cols": ["LISTS_INTERNAL", "LISTS_NAME"]
}

apis["LIST_ITEMS"] = {
    "lists": [],
    "cols": {
        "LIST_ITEMS_VALUE": "STR",
        "LIST_ITEMS_DESCRIPTION": "STR",
        "LIST_ITEMS_ENABLED": "BOOL",
        "LIST_ITEMS_ORDER": "FLOAT",
    },
    "required": [],
    "query_cols": ["LIST_ITEMS_VALUE","LIST_ITEMS_DESCRIPTION","LIST_ITEMS_ENABLED","LIST_ITEMS_ORDER"],
    "search_cols": ["LIST_ITEMS_VALUE","LIST_ITEMS_DESCRIPTION"],
    "order_cols": ["LIST_ITEMS_ORDER","LIST_ITEMS_VALUE"],
}