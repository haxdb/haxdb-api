haxdb = None


def build_people_perms():
    ids = []
    sql = "SELECT * FROM PEOPLE"
    r = haxdb.db.query(sql, squelch=True)
    if not r:
        return False
    for row in r:
        ids.append(row["PEOPLE_ID"])

    sql = """
        INSERT INTO PEOPLEPERMS (PEOPLEPERMS_PEOPLE_ID, PEOPLEPERMS_TABLE,
        PEOPLEPERMS_READ, PEOPLEPERMS_WRITE, PEOPLEPERMS_INSERT,
        PEOPLEPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
    """
    for md in haxdb.mod_def:
        for rid in ids:
            haxdb.db.query(sql, (rid, haxdb.mod_def[md]["NAME"]), squelch=True)
    haxdb.db.commit()


def build_people_perm(data):
    sql = """
        INSERT INTO PEOPLEPERMS (PEOPLEPERMS_PEOPLE_ID, PEOPLEPERMS_TABLE,
        PEOPLEPERMS_READ, PEOPLEPERMS_WRITE, PEOPLEPERMS_INSERT,
        PEOPLEPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
    """
    for md in haxdb.mod_def:
        mdname = haxdb.mod_def[md]["NAME"]
        haxdb.db.query(sql, (data["rowid"], mdname), squelch=True)
    haxdb.db.commit()


def build_node_perms():
    nids = []
    sql = "SELECT * FROM NODES"
    r = haxdb.db.query(sql, squelch=True)
    if not r:
        return False
    for row in r:
        nids.append(row["NODES_ID"])

    sql = """
        INSERT INTO NODEPERMS (NODEPERMS_NODES_ID, NODEPERMS_TABLE,
        NODEPERMS_READ, NODEPERMS_WRITE, NODEPERMS_INSERT,
        NODEPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
    """
    for md in haxdb.mod_def:
        for nid in nids:
            haxdb.db.query(sql, (nid, haxdb.mod_def[md]["NAME"]), squelch=True)
    haxdb.db.commit()


def build_node_perm(data):
    nodes_id = data["rowid"]
    sql = """
        INSERT INTO NODEPERMS (NODEPERMS_NODES_ID, NODEPERMS_TABLE,
        NODEPERMS_READ, NODEPERMS_WRITE, NODEPERMS_INSERT,
        NODEPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
    """
    for md in haxdb.mod_def:
        mdname = haxdb.mod_def[md]["NAME"]
        haxdb.db.query(sql, (nodes_id, mdname), squelch=True)
    haxdb.db.commit()


def person2node_perm(people_id, nodes_id):
    print "PERSON2NODE {} {}".format(people_id, nodes_id)
    perms = []
    sql = """
        SELECT * FROM PEOPLEPERMS
        WHERE PEOPLEPERMS_PEOPLE_ID=%s
    """
    r = haxdb.db.query(sql, (people_id,), squelch=True)
    for row in r:
        perms.append(row)

    sql = """
        UPDATE NODEPERMS SET
        NODEPERMS_READ=%s, NODEPERMS_WRITE=%s,
        NODEPERMS_INSERT=%s, NODEPERMS_DELETE=%s
        WHERE
        NODEPERMS_NODES_ID=%s AND NODEPERMS_TABLE=%s
    """
    for p in perms:
        params = (p["PEOPLEPERMS_READ"],)
        params += (p["PEOPLEPERMS_WRITE"],)
        params += (p["PEOPLEPERMS_INSERT"],)
        params += (p["PEOPLEPERMS_DELETE"],)
        params += (nodes_id,)
        params += (p["PEOPLEPERMS_TABLE"],)
        haxdb.db.query(sql, params, squelch=True)
    haxdb.db.commit()


def has_perm(table, perm_type, perm_val):
    if haxdb.session.get("dba") == 1:
        return True

    if perm_val <= 0:
        return True

    nodes_id = haxdb.session.get("nodes_id")
    sql = """
    SELECT * FROM NODEPERMS WHERE
    NODEPERMS_NODES_ID=%s
    AND NODEPERMS_TABLE=%s
    """
    row = haxdb.db.qaf(sql, (nodes_id, table))
    typecol = "NODEPERMS_{}".format(perm_type)

    try:
        if int(perm_val) <= int(row[typecol]):
            return True
    except Exception:
        return False
    return False


def get_perm(table, perm_type):
    if haxdb.session.get("dba") == 1:
        return 99999999

    nodes_id = haxdb.session.get("nodes_id")
    sql = """
        SELECT * FROM NODEPERMS WHERE
        NODEPERMS_NODES_ID=%s
        AND NODEPERMS_TABLE=%s
    """
    row = haxdb.db.qaf(sql, (nodes_id, table))
    typecol = "NODEPERMS_{}".format(perm_type, squelch=True)
    try:
        return int(row[typecol])
    except Exception:
        return 0


def get_perm_all():
    nodes_id = haxdb.session.get("nodes_id")
    sql = """
        SELECT * FROM NODEPERMS WHERE
        NODEPERMS_NODES_ID=%s
    """
    r = haxdb.db.query(sql, (nodes_id,))
    perms = {}
    if r:
        for row in r:
            perms[row["NODEPERMS_TABLE"]] = {
                "read": row["NODEPERMS_READ"],
                "write": row["NODEPERMS_WRITE"],
                "insert": row["NODEPERMS_INSERT"],
                "delete": row["NODEPERMS_DELETE"],
            }
    return perms


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb


def run():
    haxdb.func("PERM:HAS", has_perm)
    haxdb.func("PERM:GET", get_perm)
    haxdb.func("PERM:GET:ALL", get_perm_all)
    haxdb.func("PERM:PERSON2NODE", person2node_perm)

    build_people_perms()
    haxdb.on("NEW.PEOPLE", build_people_perm)

    build_node_perms()
    haxdb.on("NEW.NODES", build_node_perm)
