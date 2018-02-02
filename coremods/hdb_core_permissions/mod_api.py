from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/PEOPLEPERMS/view", methods=haxdb.METHOD)
    def PEOPLEPERMS_view():
        return haxdb.api.view_call(mod_def["NODEPERMS"])

    @haxdb.route("/PEOPLEPERMS/list", methods=haxdb.METHOD)
    def PEOPLEPERMS_list():
        pid = haxdb.get("PEOPLEPERMS_PEOPLE_ID")
        if pid:
            isql = """
            INSERT INTO PEOPLEPERMS (PEOPLEPERMS_PEOPLE_ID, PEOPLEPERMS_TABLE,
            PEOPLEPERMS_READ, PEOPLEPERMS_WRITE, PEOPLEPERMS_INSERT,
            PEOPLEPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
            """
            for md in haxdb.mod_def:
                table = md["NAME"]
                haxdb.db.query(isql, (pid, table))
            haxdb.db.commit()

        return haxdb.api.list_call(mod_def["PEOPLEPERMS"])

    @haxdb.route("/PEOPLEPERMS/save", methods=haxdb.METHOD)
    def PEOPLEPERMS_save():
        return haxdb.api.save_call(mod_def["PEOPLEPERMS"])

    @haxdb.route("/NODEPERMS/view", methods=haxdb.METHOD)
    def NODEPERMS_view():
        return haxdb.api.view_call(mod_def["NODEPERMS"])

    @haxdb.route("/NODEPERMS/list", methods=haxdb.METHOD)
    def NODEPERMS_list():
        pid = haxdb.get("NODESPERMS_NODES_ID")
        if pid:
            isql = """
            INSERT INTO NODESPERMS (NODESPERMS_NODES_ID, NODESPERMS_TABLE,
            NODESPERMS_READ, NODESPERMS_WRITE, NODESPERMS_INSERT,
            NODESPERMS_DELETE) VALUES (%s, %s, 0, 0, 0, 0)
            """
            for mod_def in haxdb.mod_def:
                table = mod_def["NAME"]
                haxdb.db.query(isql, (pid, table))

        return haxdb.api.list_call(mod_def["NODESPERMS"])

    @haxdb.route("/NODEPERMS/save", methods=haxdb.METHOD)
    def NODEPERMS_save():
        return haxdb.api.save_call(mod_def["NODEPERMS"])
