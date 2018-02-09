mod_def = {}

mod_def["THUMBNAILS"] = {
    "HEADER": "THUMBNAIL",
    "NAME": "THUMBNAILS",
    "ROWNAME": ["THUMBNAILS_TABLE", "THUMBNAILS_ROWID"],
    "UDF": 0,
    "ORDER": ["THUMBNAILS_TABLE", "THUMBNAILS_ROWID"],
    "INDEX": [],
    "UNIQUE": [["THUMBNAILS_TABLE", "THUMBNAILS_ROWID"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": [],
        "ICON": "picture-o"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "THUMBNAIL",
            "NAME": "THUMBNAIL_TABLE",
            "HEADER": "TABLE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "THUMBNAIL",
            "NAME": "THUMBNAIL_ROWID",
            "HEADER": "ROWID",
            "TYPE": "INT",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "THUMBNAIL",
            "NAME": "THUMBNAIL_SMALL",
            "HEADER": "SMALL",
            "TYPE": "BLOB",
            "NEW": 0,
            "EDIT": 0,
            "QUERY": 0,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "THUMBNAIL",
            "NAME": "THUMBNAIL_BIG",
            "HEADER": "BIG",
            "TYPE": "BLOB",
            "NEW": 0,
            "EDIT": 0,
            "QUERY": 0,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": None,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["upload", "download"]
}
