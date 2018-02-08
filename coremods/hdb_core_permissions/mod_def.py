mod_def = {}

mod_def["PEOPLEPERMS"] = {
    "HEADER": "PERMISSIONS",
    "NAME": "PEOPLEPERMS",
    "ROWNAME": ["PEOPLEPERMS_TABLE"],
    "NEW": 0,
    "UDF": 0,
    "ORDER": ["PEOPLEPERMS_TABLE"],
    "INDEX": [],
    "UNIQUE": [["PEOPLEPERMS_PEOPLE_ID", "PEOPLEPERMS_TABLE"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": "PEOPLE",
        "ICON": "key"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_PEOPLE_ID",
            "HEADER": "PERSON",
            "TYPE": "ID",
            "ID_API": "PEOPLE",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_TABLE",
            "HEADER": "TABLE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_READ",
            "HEADER": "READ",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_WRITE",
            "HEADER": "WRITE",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_INSERT",
            "HEADER": "INSERT",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "PEOPLEPERMS_DELETE",
            "HEADER": "DELETE",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save"]
}

mod_def["NODEPERMS"] = {
    "HEADER": "PERMISSIONS",
    "NAME": "NODEPERMS",
    "ROWNAME": ["NODEPERMS_TABLE"],
    "NEW": 0,
    "UDF": 0,
    "ORDER": ["NODEPERMS_TABLE"],
    "INDEX": [],
    "UNIQUE": [["NODEPERMS_NODES_ID", "NODEPERMS_TABLE"]],
    "CLIENT": {
        "MAJOR": 0,
        "MINOR": 0,
        "PARENT": "NODES",
        "ICON": "key"
    },
    "AUTH": {
        "READ": 100,
        "WRITE": 100,
        "INSERT": 100,
        "DELETE": 100,
    },
    "COLS": [
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_NODES_ID",
            "HEADER": "NODE",
            "TYPE": "ID",
            "ID_API": "NODES",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_TABLE",
            "HEADER": "TABLE",
            "TYPE": "CHAR",
            "SIZE": 25,
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 1,
            "REQUIRED": 1,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_READ",
            "HEADER": "READ",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_WRITE",
            "HEADER": "WRITE",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_INSERT",
            "HEADER": "INSERT",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
        {
            "CATEGORY": "PERMISSIONS",
            "NAME": "NODEPERMS_DELETE",
            "HEADER": "DELETE",
            "TYPE": "INT",
            "SIZE": 5,
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 1,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": 100,
                "WRITE": 100,
            }
        },
    ],
    "CALLS": ["list", "view", "save"]
}
