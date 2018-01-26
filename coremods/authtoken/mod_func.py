import time
import base64
import os

haxdb = None


def token_create(people_id):
    size = int(haxdb.config["AUTHTOKEN"]["TOKEN_SIZE"])
    expire = time.time() + int(haxdb.config["AUTHTOKEN"]["TOKEN_EXPIRE"])
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


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("AUTHTOKEN:CREATE", token_create)


def run():
    pass
