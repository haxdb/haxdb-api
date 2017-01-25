db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table('PEOPLE_RFID')
    t.add("PEOPLE_RFID_NAME", "CHAR", col_size=50)
    t.add("PEOPLE_RFID_PEOPLE_ID", "INT", col_required=True, fk_table="PEOPLE", fk_col="PEOPLE_ID")
    t.add("PEOPLE_RFID_RFID", "ASCII", col_size=255)
    t.add("PEOPLE_RFID_ENABLED", "INT", col_size=1)
    tables.append(t)

    indexes = []
    idx = db.tables.index("ASSETS_RFID",
                          ["ASSETS_RFID_ASSETS_ID"],
                          unique=True)
    indexes.append(idx)

    idx = db.tables.index("ASSETS_RFID",
                          ["ASSETS_RFID_AUTH_PEOPLE_ID"])
    indexes.append(idx)

    idx = db.tables.index("PEOPLE_RFID",
                          ["PEOPLE_RFID_PEOPLE_ID", "PEOPLE_RFID_RFID"],
                          unique=True)
    indexes.append(idx)

    db.create(tables=tables, indexes=indexes)


def get_list(name):
    sql = "SELECT * FROM LISTS WHERE LISTS_NAME = ?"
    db.query(sql, (name,))
    row = db.next()
    if row:
        return row["LISTS_ID"]
    return None


def add_list(name):
    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (%s,1)"
    db.query(sql, (name,), squelch=True)
    db.commit()
    return get_list(name)


def add_list_item(lid, item):
    sql = """
    INSERT INTO LIST_ITEMS
    (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION,
    LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER, LIST_ITEMS_INTERNAL)
    VALUES (%s, %s, %s, 1, 99, 1)
    """
    db.query(sql, (lid, item, item,), squelch=True)
    db.commit()


def add_udf(ucontext, uname, utype, uapi=None, ulid=None):
    params = (ucontext, uname, utype)
    sql = """
    INSERT INTO UDF
    (
    UDF_CONTEXT, UDF_CONTEXT_ID, UDF_CATEGORY, UDF_NAME,
    UDF_TYPE,UDF_ORDER, UDF_ENABLED, UDF_INTERNAL
    """
    if uapi:
        sql += ", UDF_TYPE_API"
        params += (uapi,)
    if ulid:
        sql += ", UDF_LISTS_ID"
        params += (ulid,)
    sql += """
    )
    VALUES
    (
    %s, 0, 'RFID', %s, %s, 999, 1, 1
    """
    if uapi:
        sql += ", %s"
    if ulid:
        sql += ", %s"
    sql += """
    )
    """
    db.query(sql, params, squelch=True)
    db.commit()


def run():
    lid = add_list("ASSET_STATUSES")

    if lid:
        for item in ["OPERATIONAL", "BORKEN"]:
            add_list_item(lid, item)

    add_udf("ASSETS", "AUTO_LOG", "BOOL")
    add_udf("ASSETS", "REQUIRE_RFID", "BOOL")
    add_udf("ASSETS", "REQUIRE_AUTH", "BOOL")
    add_udf("ASSETS", "AUTH_TIMEOUT", "INT")
    add_udf("ASSETS", "AUTH_PEOPLE_ID", "ID", uapi="PEOPLE")
    add_udf("ASSETS", "AUTH_START", "INT")
    add_udf("ASSETS", "AUTH_LAST", "INT")
    add_udf("ASSETS", "STATUS", "LIST", ulid=lid)
    add_udf("ASSETS", "STATUS_DESC", "TEXT")
