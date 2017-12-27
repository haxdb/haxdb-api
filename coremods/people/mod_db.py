db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table("PEOPLE")
    t.add("PEOPLE_IMAGE", "CHAR", col_size=50)
    t.add("PEOPLE_NAME_FIRST", "CHAR", col_size=50)
    t.add("PEOPLE_NAME_LAST", "CHAR", col_size=50)
    t.add("PEOPLE_EMAIL", "CHAR", col_size=100)
    t.add("PEOPLE_DBA", "INT", col_size=1, col_required=True)
    t.add("PEOPLE_MEMBERSHIP", "CHAR", col_size=50)
    t.add("PEOPLE_ACTIVE", "INT", col_size=1, col_required=True)
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("PEOPLE", ["PEOPLE_NAME_FIRST",
                                              "PEOPLE_NAME_LAST",
                                              "PEOPLE_EMAIL"], unique=True))

    db.create(tables=tables, indexes=indexes)


def run():

    insert_list = "INSERT INTO LISTS (LISTS_NAME, LISTS_INTERNAL) VALUES (%s, 1)"
    insert_list_item = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_INTERNAL, LIST_ITEMS_ORDER) VALUES (%s, %s, %s, 1, 1, 999)"
    find_list = "select LISTS_ID FROM LISTS WHERE LISTS_NAME=%s"
    insert_udf = "INSERT INTO UDF (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_CATEGORY, UDF_NAME, UDF_TYPE, UDF_LISTS_ID, UDF_ORDER, UDF_ENABLED, UDF_INTERNAL) VALUES ('PEOPLE',0,%s,%s,%s,%s,999,1,1)"

    db.query(insert_list, ("MEMBERSHIPS",), squelch=True)

    row = db.qaf(find_list, ("MEMBERSHIPS",), squelch=True)
    if row:
        db.query(insert_list_item, (row["LISTS_ID"], "TRIAL", "TRIAL",), squelch=True)
        db.query(insert_list_item, (row["LISTS_ID"], "MEMBER", "MEMBER",), squelch=True)
        db.commit()
