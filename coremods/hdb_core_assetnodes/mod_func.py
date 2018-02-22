haxdb = None


def assetnode_create(name, ip=None, enabled=1, assets_id=None):
    api_key = haxdb.func("APIKEY:CREATE")()

    if enabled != 1:
        enabled = 0

    data = {
        "ASSETNODES_API_KEY": api_key,
        "ASSETNODES_NAME": name,
        "ASSETNODES_ENABLED": enabled
    }

    if ip:
        data["ASSETNODES_IP"] = ip

    if assets_id:
        data["ASSETNODES_ASSETS_ID"] = assets_id

    cols = []
    params = ()
    for key in data:
        cols.append(key)
        params += (data[key],)

    sql = """
        INSERT INTO ASSETNODES ({})
        VALUES ({})
    """.format(",".join(cols), ",".join(["%s"] * len(params)))

    haxdb.db.query(sql, params)
    if haxdb.db.error:
        return None, None
    haxdb.db.commit()
    rowid = haxdb.db.lastrowid

    event_data = {
        "mod": "ASSETNODES",
        "call": "new",
        "data": data,
        "rowid": rowid,
    }
    haxdb.trigger("NEW.ASSETNODES", event_data)

    return api_key, rowid


def assetnode_get(api_key):
    sql = """
        SELECT * FROM ASSETNODES
        LEFT OUTER JOIN ASSETS ON ASSETNODES_ASSETS_ID=assets_id
        WHERE ASSETNODES_API_KEY=%s
        """
    r = haxdb.db.qaf(sql, (api_key,))
    return r


def assetnode_sense(node, sensors):
    sql = """
        UPDATE ASSETSENSORS
        SET ASSETSENSORS_VAL=%s
        WHERE ASSETSENSORS_REFERENCE=%s
        AND ASSETSENSORS_ASSETNODES_ID=%s
        """
    for sname in sensors:
        val = sensors[sname]
        haxdb.db.query(sql, (val, sname, node["ASSETNODES_ID"]))
    haxdb.db.commit()


def assetnode_operator(node_id, people_id):
    if people_id:
        sql = """
            UPDATE ASSETNODES
            SET ASSETNODES_PEOPLE_ID=%s
            WHERE ASSETNODES_ID=%s
            """
        haxdb.db.query(sql, (people_id, node_id))
    else:
        sql = """
            UPDATE ASSETNODES
            SET ASSETNODES_PEOPLE_ID=NULL
            WHERE ASSETNODES_ID=%s
            """
        haxdb.db.query(sql, (node_id,))
    haxdb.db.commit()


def assetnode_auth(raw, rfid):
    # get rfid data
    r = haxdb.func("RFID:GET")(rfid, False)
    if r:
        identity = "{} {}".format(r["PEOPLE_NAME_FIRST"],
                                  r["PEOPLE_NAME_LAST"])
        raw["rfid"]["person"]["id"] = r["PEOPLE_ID"]
        raw["rfid"]["person"]["name"] = identity
    else:
        raw["message"] = "INVALID RFID"
        return haxdb.response(raw=raw)

    if r["PEOPLE_DBA"] == 1 or r["MEMBERSHIPS_RFID"] == 1:
            raw["rfid"]["valid"] = 1
    else:
        raw["message"] = "INACTIVE RFID"
        return haxdb.response(raw=raw)

    # any valid rfid will work
    if raw["node"]["approval"] != 1:
        assetnode_operator(raw["node"]["id"], r["PEOPLE_ID"])
        raw["engage"] = 1
        raw["message"] = "ACCESS GRANTED"
        return haxdb.response(raw=raw)

    # only valid rfid on approval list
    sql = """
        SELECT * FROM PEOPLE
        JOIN ASSETS
        JOIN PEOPLERFID ON PEOPLERFID_PEOPLE_ID=PEOPLE_ID
        JOIN ASSETNODES ON ASSETNODES_ASSETS_ID=ASSETS_ID
        LEFT OUTER JOIN MEMBERSHIPS ON PEOPLE_MEMBERSHIPS_ID=MEMBERSHIPS_ID
        LEFT OUTER JOIN ASSETAUTHS ON ASSETAUTHS_PEOPLE_ID=PEOPLE_ID
                        AND ASSETAUTHS_ASSETS_ID=ASSETS_ID
        WHERE
        ASSETNODES_ID=%s
        AND PEOPLERFID_RFID = %s
        AND PEOPLERFID_ENABLED=1
        AND (
         PEOPLE_DBA = 1
         OR
         ( MEMBERSHIPS_RFID=1 AND ASSETAUTHS_ENABLED=1 )
        )
        """
    r = haxdb.db.qaf(sql, (raw["node"]["id"], rfid,))
    if not r:
        raw["engage"] = 0
        raw["message"] = "APPROVAL REQUIRED"
        return haxdb.response(raw=raw)
    else:
        assetnode_operator(raw["node"]["id"], r["PEOPLE_ID"])
        raw["engage"] = 1
        raw["message"] = "ACCESS GRANTED"
        return haxdb.response(raw=raw)


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("ASSETNODE:CREATE", assetnode_create)
    haxdb.func("ASSETNODE:GET", assetnode_get)
    haxdb.func("ASSETNODE:OPERATOR", assetnode_operator)
    haxdb.func("ASSETNODE:SENSE", assetnode_sense)
    haxdb.func("ASSETNODE:AUTH", assetnode_auth)


def run():
    pass
