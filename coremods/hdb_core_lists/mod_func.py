haxdb = None


def list_create(name, internal=1):
    sql = "INSERT INTO LISTS (LISTS_NAME, LISTS_INTERNAL) VALUES (%s, %s)"
    return haxdb.db.query(sql, (name, internal))


def list_add(listname, itemname, itemvalue, internal=1):
    sql = "SELECT * FROM LISTS WHERE LISTS_NAME=%s"
    r = haxdb.db.qaf(sql, (listname,))
    if r and "LISTS_NAME" in r and r["LISTS_NAME"]:
        lid = r["LISTS_ID"]
    sql = """
    INSERT INTO LIST_ITEMS (LIST_ITEMS_NAME, LIST_ITEMS_VALUE,
                            LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER,
                            LIST_ITEMS_INTERNAL)
                VALUES (%s, %s, 1, 9999, %s)
    """
    return haxdb.db.query(itemname, itemvalue, internal)


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("LIST:CREATE", list_create)
    haxdb.func("LIST:ADD", list_add)


def run():
    pass
