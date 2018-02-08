haxdb = None


def lists_create(name, internal=1):
    sql = "INSERT INTO LISTS (LISTS_NAME, LISTS_INTERNAL) VALUES (%s, %s)"
    r = haxdb.db.query(sql, (name, internal))
    haxdb.db.commit()
    return r


def lists_add(listname, itemname, itemvalue, internal=1):
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

    r = haxdb.db.query(itemname, itemvalue, internal)
    haxdb.db.commit()
    return r

def lists_get():
    lists = {}
    sql = "SELECT * FROM LISTS"
    r = haxdb.db.query(sql)
    if not r:
        return lists
    for row in r:
        lists[row["LISTS_NAME"]] = []

    sql = """
        SELECT * FROM LISTS
        JOIN LIST_ITEMS ON LISTS_ID = LIST_ITEMS_LISTS_ID
        WHERE LIST_ITEMS_ENABLED='1'
        ORDER BY LIST_ITEMS_ORDER
    """
    r = haxdb.db.query(sql)
    for row in r:
        list_item = {
            "name": row["LIST_ITEMS_NAME"],
            "value": row["LIST_ITEMS_VALUE"],
        }
        lists[row["LISTS_NAME"]].append(list_item)
    return lists


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("LISTS:CREATE", lists_create)
    haxdb.func("LISTS:ADD", lists_add)
    haxdb.func("LISTS:GET", lists_get)


def run():
    pass
