import base64
import os

haxdb = None


def apikey_create():
    size = int(haxdb.config["NODES"]["APIKEY_SIZE"])
    return base64.urlsafe_b64encode(os.urandom(500))[5:5+size]

def node_create(name, ip=None, expire=None, dba=0, enabled=1,
                people_id=None, assets_id=None):
    api_key = apikey_create()

    if dba != 1:
        dba = 0

    if enabled != 1:
        enabled = 0

    cols = ["NODES_API_KEY", "NODES_NAME", "NODES_DBA", "NODES_ENABLED"]
    params = (api_key, name, dba, enabled)

    if ip:
        cols.append("NODES_IP")
        params += (ip,)

    if expire:
        cols.append("NODES_EXPIRE")
        params += (expire, )

    if  people_id:
        cols.append("NODES_PEOPLE_ID")
        params += (people_id, )

    if assets_id:
        cols.append("ASSETS_ID")
        params += (assets_id)

    sql = """
        INSERT INTO NODES ({})
        VALUES ({})
    """.format(",".join(cols), ",".join(["%s"]*len(params)))

    haxdb.db.query(sql, params)
    if haxdb.db.error:
        return haxdb.error(haxdb.db.error)
    haxdb.db.commit()
    return api_key


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("APIKEY:CREATE", apikey_create)
    haxdb.func("NODES:CREATE", node_create)

def run():
    pass
