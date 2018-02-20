haxdb = None


def FIELDSET_create(table, name, fields, people_id=None,
                    order=9999, internal=1):
    cols = [
        "FIELDSET_TABLE",
        "FIELDSET_NAME",
        "FIELDSET_ORDER",
        "FIELDSET_INTERNAL"]
    params = (table, name, order, internal)
    if people_id:
        cols.append("FIELDSET_PEOPLE_ID")
        params += (people_id,)

    sql = """
        INSERT INTO FIELDSET
        ({})
        VALUES ({})
    """.format(",".join(cols), ",".join(["%s"] * len(cols)))

    r = haxdb.db.query(sql, params)
    haxdb.db.commit()
    return r


def FIELDSET_get(table, people_id=None):
    sql = """
        SELECT * FROM FIELDSET
        JOIN FIELDSETFIELDS ON FIELDSETFIELDS_FIELDSET_ID=FIELDSET_ID
        WHERE FIELDSET_TABLE=%s
    """
    params = (table,)
    if people_id:
        sql += " AND FIELDSET_PEOPLE_ID=%s"
        params += (people_id, )
    sql += " ORDER BY FIELDSET_TABLE, FIELDSET_ORDER, FIELDSETFIELDS_ORDER"
    r = haxdb.db.query(sql, params)

    fieldsets = {}
    fields = []
    lastfid = None
    for row in r:
        fid = row["FIELDSET_ID"]
        name = row["FIELDSET_NAME"]
        field = row["FIELDSETFIELDS_FIELD"]

        if fid != lastfid:
            if lastfid is not None:
                fieldset = {
                    "rowid": fid,
                    "table": table,
                    "name": name,
                    "fields": fields
                }
                fieldsets.append(fieldset)
                fields = []
            lastfid = fid

        fields.append(field)
    return fieldsets


def FIELDSET_getall(people_id=None):
    sql = """
        SELECT * FROM FIELDSET
        JOIN FIELDSETFIELDS ON FIELDSETFIELDS_FIELDSET_ID=FIELDSET_ID
        WHERE 1=1
    """
    params = ()
    if people_id:
        sql += " AND FIELDSET_PEOPLE_ID=%s"
        params += (people_id, )
    sql += " ORDER BY FIELDSET_TABLE, FIELDSET_ORDER, FIELDSETFIELDS_ORDER"
    r = haxdb.db.query(sql, params)

    fieldsets = {}
    if not r:
        return fieldsets
    fields = []
    lastfid = None
    for row in r:
        table = row["FIELDSET_TABLE"]
        fid = row["FIELDSET_ID"]
        name = row["FIELDSET_NAME"]
        field = row["FIELDSETFIELDS_FIELD"]

        if table not in fieldsets:
            fieldsets[table] = []

        if fid != lastfid:
            if lastfid is not None:
                fieldset = {
                    "rowid": fid,
                    "table": table,
                    "name": name,
                    "fields": fields
                }
                fieldsets[table].append(fieldset)
                fields = []
            lastfid = fid

        fields.append(field)

    return fieldsets


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("FIELDSET:CREATE", FIELDSET_create)
    haxdb.func("FIELDSET:GET", FIELDSET_get)
    haxdb.func("FIELDSET:GET:ALL", FIELDSET_getall)


def run():
    pass
