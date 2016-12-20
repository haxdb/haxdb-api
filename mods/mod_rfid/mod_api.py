import mod_data
from flask import request
import time

haxdb = None
db = None
config = None
tools = None
apis = {}


def init(app_haxdb, app_db, app_config, mod_tools):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = mod_tools

    for api_name in mod_data.apis:
        apis[api_name] = haxdb.api.api_call()
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]


def run():
    @haxdb.app.route("/ASSETS_RFID/pulse", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/pulse/<rfid>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/pulse/<rfid>/<status>", methods=["POST", "GET"])
    def mod_rfid_asset_pulse(rfid=None, status=None):
        api_key = haxdb.data.var.get("api_key")
        rfid = rfid or haxdb.data.var.get("rfid")
        status = status or haxdb.data.var.get("status")


        meta = {}
        meta["api"] = "ASSETS_RFID"
        meta["action"] = "pulse"
        meta["rfid"] = rfid
        meta["status"] = status

        sql = """
        SELECT *
        FROM NODES
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        LEFT OUTER JOIN ASSETS_RFID ON ASSETS_RFID_ASSETS_ID=ASSETS_ID
        """
        params = ()
        if rfid:
            sql += """
            LEFT OUTER JOIN PEOPLE_RFID ON PEOPLE_RFID_RFID=%s AND PEOPLE_RFID_ENABLED=1 AND PEOPLE_RFID_RFID IS NOT NULL AND PEOPLE_RFID_RFID != ''
            LEFT OUTER JOIN PEOPLE ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_ACTIVE=1
            LEFT OUTER JOIN ASSET_AUTHS ON ASSET_AUTHS_ASSETS_ID=ASSETS_ID AND ASSET_AUTHS_PEOPLE_ID=PEOPLE_ID
            """
            params += (rfid,)

        sql += """
        WHERE
        NODES_API_KEY=%s
        AND NODES_API_KEY IS NOT NULL
        AND NODES_API_KEY != ''
        """
        params += (api_key,)
        node = db.qaf(sql, params)
        if db.error: return haxdb.data.output(success=0, meta=meta, message=db.error)

        if not node:
            # API KEY DOES NOT MATCH A NODE.
            # REGISTER IF RFID MATCHES DBA.
            sql = """
            SELECT * FROM PEOPLE
            JOIN PEOPLE_RFID ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_RFID_ENABLED=1 AND PEOPLE_RFID_RFID IS NOT NULL AND PEOPLE_RFID_RFID != ''
            WHERE
            PEOPLE_DBA=1
            AND PEOPLE_RFID_RFID=%s
            """
            params = (rfid,)
            person = db.qaf(sql, params)
            if db.error: return haxdb.data.output(success=0, meta=meta, message=db.error)
            if person:
                print dict(person)
                # RFID MATCHES A DBA.
                # ATTEMPT TO REGISTER NODE IN QUEUE
                ip = str(request.access_route[-1])

                sql = "SELECT * FROM NODES WHERE NODES_IP=%s"
                row = db.qaf(sql,(ip,))
                if db.error: return haxdb.data.output(success=0, meta=meta, message=db.error)
                if row:
                    return haxdb.data.output(success=0, meta=meta, message="NODE ALREADY REGISTERED ON THIS IP.")

                sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_NAME, NODES_READONLY, NODES_DBA, NODES_IP, NODES_ENABLED, NODES_QUEUED)
                    VALUES (%s,%s,%s,'1','0',%s,'0','1')
                    """
                api_key = tools.create_api_key()
                node_name = "%s %s REGISTERED (RFID)" % (person["PEOPLE_NAME_FIRST"],person["PEOPLE_NAME_LAST"])
                db.query(sql, (api_key,person["PEOPLE_ID"],node_name,ip,))
                if db.error: return haxdb.data.output(success=0, meta=meta, message=db.error)
                if db.rowcount > 0:
                    db.commit()
                    return haxdb.data.output(success=0, meta=meta, value=api_key, message="NODE REGISTERED.\nACTIVATION NEEDED.")
                return haxdb.data.output(success=0, meta=meta, message="I DON'T KNOW WHAT HAPPENED")

            return haxdb.data.output(success=0, meta=meta, message="NODE MUST BE REGISTERED BY DBA.")

        if int(node["NODES_QUEUED"]) == 1:
            # NODE REGISTERED BUT NOT AUTHORIZED
            return haxdb.data.output(success=0, meta=meta, message="NODE REGISTERED BUT NOT ACTIVATED.")

        if int(node["NODES_ENABLED"]) != 1:
            # NODE NOT ENABLED
            return haxdb.data.output(success=0, meta=meta, message="NODE REGISTERED BUT NOT ENABLED.")

        if not node["NODES_ASSETS_ID"]:
            # NODE NOT ASSIGNED AN ASSET
            return haxdb.data.output(success=0, meta=meta, message="NODE REGISTERED BUT NOT ASSOCIATED WITH ASSET.")

        if node["ASSETS_RFID_REQUIRE_RFID"]!=None and int(node["ASSETS_RFID_REQUIRE_RFID"]) != 1:
            # NODE DOES NOT REQUIRE RFID
            # TODO: LOG ASSET_USAGE
            message ="%s\n%s" % (node["ASSETS_NAME"], node["ASSETS_RFID_STATUS"])
            return haxdb.data.output(success=1, meta=meta, message=message)

        if not rfid:
            # TODO: LOG ASSET_USAGE
            message ="%s\n%s" % (node["ASSETS_NAME"], node["ASSETS_RFID_STATUS"])
            return haxdb.data.output(success=0, meta=meta, message=message)

        if not node["PEOPLE_ID"]:
            # TODO: DEAUTH ASSET
            return haxdb.data.output(success=0, meta=meta, message="RFID NOT RECOGNIZED.")

        if node["ASSETS_RFID_REQUIRE_AUTH"]!=None and int(node["ASSETS_RFID_REQUIRE_AUTH"])!=1:
            message = "%s\n%s %s\nNO AUTHORIZE REQUIRED" % (node["ASSETS_NAME"], node["PEOPLE_NAME_FIRST"], node["PEOPLE_NAME_LAST"])
            return haxdb.data.output(success=0, meta=meta, message=message)

        if not node["ASSET_AUTHS_ID"]:
            # TODO: DEAUTH ASSET
            message = "%s\n%s %s\nNOT AUTHORIZED" % (node["ASSETS_NAME"], node["PEOPLE_NAME_FIRST"], node["PEOPLE_NAME_LAST"])
            return haxdb.data.output(success=0, meta=meta, message=message)

        # AUTH ASSET
        message = "%s\n%s %s\nAUTHORIZED" % (node["ASSETS_NAME"], node["PEOPLE_NAME_FIRST"], node["PEOPLE_NAME_LAST"])
        return haxdb.data.output(success=1, meta=meta, message=message)


    @haxdb.app.route("/RFID/asset/list", methods=["POST", "GET"])
    @haxdb.app.route("/RFID/asset/list/<path:query>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/list/<path:query>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_rfid_asset_list(query=None):

        meta = {}
        meta["api"] = "ASSETS_RFID"
        meta["action"] = "list"

        sql = """
        SELECT ASSETS.*, ASSETS_RFID.*
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM ASSETS_RFID
        JOIN ASSETS ON ASSETS_ID = ASSETS_RFID_ASSETS_ID
        LEFT OUTER JOIN PEOPLE ON ASSETS_RFID_AUTH_PEOPLE_ID=PEOPLE_ID
        """
        return apis["ASSETS_RFID"].list_call(sql, (), meta)

    @haxdb.app.route("/ASSETS_RFID/view", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS_RFID/view/<int:rowid>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_ASSETS_RFID_view(rowid=None):
        def calc_row(row):
            row["ASSETS_RFID_IN_USE"] = 0
            if row["ASSETS_RFID_AUTH_LAST"] and row["ASSETS_RFID_AUTH_TIMEOUT"]  and (time.time() - int(row["ASSETS_RFID_AUTH_LAST"])) < row["ASSETS_RFID_AUTH_TIMEOUT"]:
                row["ASSETS_RFID_IN_USE"] = 1
            return row

        rowid = rowid or haxdb.data.var.get("rowid")


        meta = {}
        meta["api"] = "ASSETS_RFID"
        meta["action"] = "view"
        meta["rowid"] = rowid

        sql = """SELECT ASSETS.*, ASSETS_RFID.*,
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM ASSETS
        LEFT OUTER JOIN ASSETS_RFID ON ASSETS_ID = ASSETS_RFID_ASSETS_ID
        LEFT OUTER JOIN PEOPLE ON ASSETS_RFID_AUTH_PEOPLE_ID=PEOPLE_ID
        WHERE
        ASSETS_ID=%s
        """
        params = (rowid,)
        return apis["ASSETS_RFID"].view_call(sql, params, meta, calc_row)


    @haxdb.app.route("/ASSETS_RFID/save", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS_RFID/save/<int:rowid>/<col>/<path:val>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_ASSETS_RFID_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")


        meta = {}
        meta["api"] = "ASSETS_RFID"
        meta["action"] = "save"
        meta["rowid"] = rowid

        sql = "INSERT INTO ASSETS_RFID(ASSETS_RFID_ASSETS_ID) VALUES (%s)"
        db.query(sql,(rowid,), squelch=True)
        db.commit()

        sql = """
        UPDATE ASSETS_RFID SET {}=%s WHERE ASSETS_RFID_ASSETS_ID = %s
        """
        params = (val, rowid,)

        return apis["ASSETS_RFID"].save_call(sql,params,meta,col,val)

    @haxdb.app.route("/PEOPLE_RFID/list", methods=["POST","GET"])
    @haxdb.app.route("/PEOPLE_RFID/list/<int:people_id>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_PEOPLE_RFID_list (people_id=None):
        people_id = people_id or haxdb.data.var.get("people_id")


        meta = {}
        meta["api"] = "PEOPLE_RFID"
        meta["action"] = "list"
        meta["people_id"] = people_id

        sql = "SELECT * FROM PEOPLE WHERE PEOPLE_ID=%s"
        row = db.qaf(sql,(people_id,))
        meta["people_name"] = "%s %s" % (row["PEOPLE_NAME_FIRST"],row["PEOPLE_NAME_LAST"],)

        sql = """
        SELECT *,
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM PEOPLE_RFID
        JOIN PEOPLE ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_ID=%s
        """
        params = (people_id,)
        return apis["PEOPLE_RFID"].list_call(sql, params, meta)

    @haxdb.app.route("/PEOPLE_RFID/new", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/new/<int:people_id>/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_new(people_id=None, name=None):
        people_id = people_id or haxdb.data.var.get("people_id")
        name = name or haxdb.data.var.get("name")


        meta = {}
        meta["api"] = "PEOPLE_RFID"
        meta["action"] = "new"
        meta["people_id"] = people_id
        meta["name"] = name

        sql = "INSERT INTO PEOPLE_RFID (PEOPLE_RFID_PEOPLE_ID, PEOPLE_RFID_NAME, PEOPLE_RFID_ENABLED) "
        sql += "VALUES (%s, %s, 0)"
        params = (people_id, name,)
        return apis["PEOPLE_RFID"].new_call(sql, params, meta)

    @haxdb.app.route("/PEOPLE_RFID/save", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE_RFID/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")


        meta = {}
        meta["api"] = "PEOPLE_RFID"
        meta["action"] = "save"
        meta["rowid"] = rowid
        meta["col"] = col
        meta["val"] = val
        meta["oid"] = "PEOPLE_RFID-%s-%s" % (rowid, col,)

        sql = "UPDATE PEOPLE_RFID SET {}=%s WHERE PEOPLE_RFID_ID=%s"
        params = (val,rowid,)
        return apis["PEOPLE_RFID"].save_call(sql, params, meta, col, val, rowid)

    @haxdb.app.route("/PEOPLE_RFID/delete", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE_RFID/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")


        meta = {}
        meta["api"] = "PEOPLE_RFID"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM PEOPLE_RFID WHERE PEOPLE_RFID_ID=%s"
        params = (rowid,)
        return apis["PEOPLE_RFID"].delete_call(sql, params, meta)
