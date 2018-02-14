haxdb = None


def people_create(email, first_name=None, last_name=None, dba=0):
    if not first_name:
        first_name = "UNKNOWN"
    if not last_name:
        last_name = "UNKNOWN"
    if dba != 1:
        dba = 0
    sql = """
        INSERT INTO
        PEOPLE(PEOPLE_EMAIL, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST, PEOPLE_DBA)
        VALUES (%s, %s, %s, %s)
    """
    haxdb.db.query(sql, (email, first_name, last_name, dba))
    if haxdb.db.rowcount > 0:
        haxdb.db.commit()
        person = {
            "PEOPLE_ID": haxdb.db.lastrowid,
            "PEOPLE_NAME_FIRST": first_name,
            "PEOPLE_NAME_LAST": last_name,
            "DBA": dba,
        }
        return person
    if haxdb.db.error:
        return haxdb.error(haxdb.db.error)
    return False


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("PEOPLE:CREATE", people_create)


def run():
    pass
