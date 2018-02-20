mod_def = {}

mod_def["PEOPLERFID"] = {
    "HEADER": "RFIDS",
    "NAME": "PEOPLERFID",
    "ROWNAME": ["PEOPLERFID_NAME"],
    "NEW": 1,
    "UDF": 0,
    "ORDER": ["PEOPLERFID_PEOPLE_ID", "PEOPLERFID_NAME"],
    "INDEX": [],
    "UNIQUE": [["PEOPLERFID_RFID"],
               ["PEOPLERFID_PEOPLE_ID", "PEOPLERFID_NAME"]],
    "CLIENT": {
        "NAME": "RFID",
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": ["PEOPLE"],
        "ICON": "id-card-o"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "RFID",
            "NAME": "PEOPLERFID_NAME",
            "HEADER": "NAME",
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
            "CATEGORY": "RFID",
            "NAME": "PEOPLERFID_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "ID_API": "PEOPLE",
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
            "CATEGORY": "RFID",
            "NAME": "PEOPLERFID_RFID",
            "HEADER": "RFID",
            "TYPE": "CHAR",
            "SIZE": 50,
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
            "CATEGORY": "RFID",
            "NAME": "PEOPLERFID_ENABLED",
            "HEADER": "ENABLED",
            "TYPE": "BOOL",
            "NEW": 1,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save", "new", "delete"]
}
