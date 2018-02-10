import base64
import os

haxdb = None


def apikey_create():
    size = int(haxdb.config["NODES"]["APIKEY_SIZE"])
    return base64.urlsafe_b64encode(os.urandom(500))[5:5+size]

def node_create(name, ip=None, expire=None, dba=0, enabled=1, people_id=None):
    api_key = apikey_create()

    if dba != 1:
        dba = 0

    if enabled != 1:
        enabled = 0

    cols = ["NODES_API_KEY", "NODES_NAME", "NODES_DBA", "NODES_ENABLED"]
    params = (api_key, name, dba, enabled)

    data = {
        "NODES_API_KEY": api_key,
        "NODES_NAME": name,
        "NODES_DBA": dba,
        "NODES_ENABLED": enabled
    }

    if ip:
        cols.append("NODES_IP")
        params += (ip,)
        data["NODES_IP"] = ip

    if expire:
        cols.append("NODES_EXPIRE")
        params += (expire, )
        data["NODES_EXPIRE"] = expire

    if people_id:
        cols.append("NODES_PEOPLE_ID")
        params += (people_id, )
        data["NODES_PEOPLE_ID"] = people_id

    sql = """
        INSERT INTO NODES ({})
        VALUES ({})
    """.format(",".join(cols), ",".join(["%s"]*len(params)))

    haxdb.db.query(sql, params)
    if haxdb.db.error:
        return haxdb.error(haxdb.db.error)
    haxdb.db.commit()
    nodes_id = haxdb.db.lastrowid

    event_data = {
        "mod": "NODES",
        "call": "new",
        "data": data,
        "rowid": nodes_id,
    }
    haxdb.trigger("NEW.NODES", event_data)

    if people_id:
        haxdb.func("PERM:PERSON2NODE")(people_id, nodes_id)

    return api_key, nodes_id


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("APIKEY:CREATE", apikey_create)
    haxdb.func("NODES:CREATE", node_create)

def run():
    pass
