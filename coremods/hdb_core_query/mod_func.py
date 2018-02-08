haxdb = None


def QUERY_create(table, name, query, people_id=None, order=9999, internal=1):
    cols = [
        "QUERY_TABLE",
        "QUERY_NAME",
        "QUERY_QUERY",
        "QUERY_ORDER",
        "QUERY_INTERNAL"]
    params = (table, name, query, order, internal)
    if people_id:
        cols.append("QUERY_PEOPLE_ID")
        params += (people_id,)

    sql = """
        INSERT INTO QUERY
        ({})
        VALUES ({})
    """.format(",".join(cols), ",".join(["%s"]*len(cols)))

    r = haxdb.db.query(sql, params)
    haxdb.db.commit()
    return r


def QUERY_get(table, people_id=None):
    queries = []
    sql = "SELECT * FROM QUERY WHERE QUERY_TABLE=%s"
    params = (table,)
    if people_id:
        sql += " AND QUERY_PEOPLE_ID=%s"
        params += (people_id, )
    sql += "ORDER BY QUERY_ORDER"
    r = haxdb.db.query(sql, params)
    for row in r:
        queries.append(row)
    return queries


def QUERY_getall(people_id=None):
    sql = "SELECT * FROM QUERY"
    params = ()
    if people_id:
        sql += " WHERE QUERY_PEOPLE_ID=%s"
        params += (people_id, )
    sql += " ORDER BY QUERY_ORDER"
    r = haxdb.db.query(sql, params)

    queries = {}
    if not r:
        return queries
    for row in r:
        if row["QUERY_TABLE"] not in queries:
            queries[row["QUERY_TABLE"]] = []
        queries[row["QUERY_TABLE"]].append(row)
    return queries


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("QUERY:CREATE", QUERY_create)
    haxdb.func("QUERY:GET", QUERY_get)
    haxdb.func("QUERY:GET:ALL", QUERY_getall)


def run():
    pass
