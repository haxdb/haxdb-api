haxdb = None


def assetsensors_create(assetnode_id, sensors):
    sql = """
        INSERT INTO ASSETSENSORS
        (ASSETSENSORS_NAME, ASSETSENSORS_REFERENCE, ASSETSENSORS_ASSETNODES_ID)
        VALUES
        (%s, %s, %s)
        """
    for sname in sensors:
        haxdb.db.query(sql, (sname, sname, assetnode_id))
    haxdb.db.commit()


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("ASSETSENSORS:CREATE", assetsensors_create)


def run():
    pass
