import time
import base64
import os

haxdb = None


def token_create(people_id):
    now = time.time()
    sql = "DELETE FROM AUTHTOKEN WHERE AUTHTOKEN_EXPIRE < %s"
    haxdb.db.query(sql, (now,))
    haxdb.db.commit()

    size = int(haxdb.config["AUTHTOKEN"]["TOKEN_SIZE"])
    expire = now + int(haxdb.config["AUTHTOKEN"]["TOKEN_EXPIRE"])
    token = base64.urlsafe_b64encode(os.urandom(500))[5:5+size]
    sql = """
        INSERT INTO AUTHTOKEN
            (AUTHTOKEN_TOKEN, AUTHTOKEN_PEOPLE_ID, AUTHTOKEN_EXPIRE)
        VALUES
            (%s, %s, %s)
    """
    params = (token, people_id, expire)
    haxdb.db.query(sql, params)
    haxdb.db.commit()
    return token

def token_validate(token):
    now = time.time()

    # DELETE OLD TOKEN
    sql = "DELETE FROM AUTHTOKEN WHERE AUTHTOKEN_EXPIRE<%s"
    haxdb.db.query(sql, (now,))
    haxdb.db.commit()

    # VALIDATE TOKEN
    sql = """
        SELECT * FROM AUTHTOKEN
        JOIN PEOPLE ON AUTHTOKEN_PEOPLE_ID = PEOPLE_ID
        WHERE
        AUTHTOKEN_TOKEN = %s
        AND AUTHTOKEN_EXPIRE > %s
    """
    haxdb.db.query(sql, (token, now,))
    row = haxdb.db.next()
    if not row:
        msg = "TOKEN IS INVALID OR EXPIRED."
        return haxdb.error(msg)

    # REMOVE TOKEN
    sql = "DELETE FROM AUTHTOKEN WHERE AUTHTOKEN_TOKEN=%s"
    haxdb.db.query(sql, (token,))
    if haxdb.db.error:
        return haxdb.response(success=0, message=haxdb.db.error)
    haxdb.db.commit()

    return row


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("AUTHTOKEN:CREATE", token_create)
    haxdb.func("AUTHTOKEN:VALIDATE", token_validate)

def run():
    pass
