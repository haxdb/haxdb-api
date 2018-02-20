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


def assetnode_rfid(node, rfid):
    r = haxdb.func("RFID:GET")(rfid)
    params = ()
    if r:
        sql = """
            UPDATE ASSETNODES
            SET ASSETNODES_PEOPLE_ID=%s
            WHERE ASSETNODES_ID=%s
            """
        params = (r["PEOPLE_ID"], node["ASSETNODES_ID"])
    else:
        sql = """
            UPDATE ASSETNODES
            SET ASSETNODES_PEOPLE_ID=NULL
            WHERE ASSETNODES_ID=%s
        """
        params = (node["ASSETNODES_ID"],)
    haxdb.db.query(sql, params)
    haxdb.db.commit()


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
    sql = """
        UPDATE ASSETNODES
        SET ASSETNODES_PEOPLE_ID=%s
        WHERE ASSETNODES_ID=%s
        """
    haxdb.db.query(sql, (people_id, node_id))
    haxdb.db.commit()


def assetnode_auth(node, rfid):
    raw = {
        "assetName": node["ASSETS_NAME"],
        "assetId": node["ASSETS_ID"],
    }

    # If any valid rfid will work
    if node["ASSETNODES_APPROVAL"] != 1:
        r = haxdb.func("RFID:GET")(rfid)
        if not r:
            raw["code"] = -4
            raw["message"] = "ASSETNODE RESTRICTED"
            return haxdb.response(success=0, raw=raw)
        else:
            assetnode_operator(node["ASSETNODES_ID"], r["PEOPLE_ID"])
            identity = "{} {}".format(r["PEOPLE_NAME_FIRST"],
                                      r["PEOPLE_NAME_LAST"])
            raw["personName"] = identity
            raw["personId"] = r["PEOPLE_ID"]
            raw["code"] = 2
            raw["message"] = "ACCESS GRANTED"
            return haxdb.response(success=1, raw=raw)

    sql = """
        SELECT * FROM PEOPLE
        JOIN PEOPLERFID ON PEOPLERFID_PEOPLE_ID=PEOPLE_ID
        JOIN MEMBERSHIPS ON PEOPLE_MEMBERSHIPS_ID=MEMBERSHIPS_ID
        JOIN ASSETAUTHS ON ASSETAUTHS_PEOPLE_ID=PEOPLE_ID
        JOIN ASSETS ON ASSETS_ID=ASSETAUTHS_ASSETS_ID
        JOIN ASSETNODES ON ASSETNODES_ASSETS_ID=ASSETS_ID
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
    r = haxdb.db.qaf(sql, (node["ASSETNODES_ID"], rfid,))
    if not r:
        raw["code"] = -5
        raw["message"] = "ASSET REQUIRES APPROVAL"
        return haxdb.response(success=0, raw=raw)
    else:
        assetnode_operator(node["ASSETNODES_ID"], r["PEOPLE_ID"])
        identity = "{} {}".format(r["PEOPLE_NAME_FIRST"],
                                  r["PEOPLE_NAME_LAST"])
        raw["personName"] = identity
        raw["personId"] = r["PEOPLE_ID"]
        raw["code"] = 3
        raw["message"] = "ACCESS GRANTED"
        return haxdb.response(success=1, raw=raw)


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("ASSETNODE:CREATE", assetnode_create)
    haxdb.func("ASSETNODE:GET", assetnode_get)
    haxdb.func("ASSETNODE:RFID", assetnode_rfid)
    haxdb.func("ASSETNODE:SENSE", assetnode_sense)
    haxdb.func("ASSETNODE:AUTH", assetnode_auth)


def run():
    pass
