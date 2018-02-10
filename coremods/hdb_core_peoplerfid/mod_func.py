import base64

haxdb = None


def rfid_create():
    size = haxdb.config["RFID"]["SIZE"]
    return base64.urlsafe_b64encode(os.urandom(500))[5:5+size]


def rfid_get(rfid):
    sql = """
        SELECT * FROM PEOPLE
        JOIN PEOPLERFID ON PEOPLERFID_PEOPLE_ID=PEOPLE_ID
        JOIN MEMBERSHIPS ON PEOPLE_MEMBERSHIPS_ID=MEMBERSHIPS_ID
        WHERE
        PEOPLERFID_RFID = %s
        AND PEOPLERFID_ENABLED=1
        AND MEMBERSHIPS_RFID=1
        """
    r = haxdb.db.qaf(sql, (rfid,))
    return r


def rfid_dba(rfid):
    sql = """
        SELECT PEOPLE_DBA FROM PEOPLE
        JOIN PEOPLERFID ON PEOPLERFID_PEOPLE_ID=PEOPLE_ID
        WHERE PEOPLERFID_RFID = %s
        """
    r = haxdb.db.qaf(sql, (rfid,))
    if r and "PEOPLE_DBA" in r and r["PEOPLE_DBA"] == 1:
        return True
    return False

def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb


def run():
    haxdb.func("RFID:CREATE", rfid_create)
    haxdb.func("RFID:GET", rfid_get)
    haxdb.func("RFID:DBA", rfid_dba)
