mod_def = {}

mod_def["PEOPLE"] = {
    "NAME": "PEOPLE",
    "TABLE": "PEOPLE",
    "ROWID": "PEOPLE_ID",
    "COLS": [
        {
         "NAME": "PEOPLE_NAME_FIRST",
         "HEADER": "FIRST",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "PEOPLE_NAME_LAST",
         "HEADER": "LAST",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "PEOPLE_EMAIL",
         "HEADER": "EMAIL",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
        {
         "NAME": "PEOPLE_DBA",
         "HEADER": "DBA",
         "TYPE": "BOOL",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 0,
         "REQUIRED": 0,
        },
        {
         "NAME": "PEOPLE_MEMBERSHIP",
         "HEADER": "MEMBERSHIP",
         "TYPE": "STR",
         "EDIT": 1,
         "QUERY": 1,
         "SEARCH": 1,
         "REQUIRED": 0,
        },
    ],
    "ORDER": ["PEOPLE_NAME_LAST", "PEOPLE_NAME_FIRST"]
}
