import mod_data
from flask import request
import time

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


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
        if db.error:
            return haxdb.data.output(success=0, meta=meta, message=db.error)

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
            if db.error:
                return haxdb.data.output(success=0, meta=meta, message=db.error)
            if person:
                print dict(person)
                # RFID MATCHES A DBA.
                # ATTEMPT TO REGISTER NODE IN QUEUE
                ip = str(request.access_route[-1])

                sql = "SELECT * FROM NODES WHERE NODES_IP=%s"
                row = db.qaf(sql, (ip,))
                if db.error:
                    return haxdb.data.output(success=0, meta=meta, message=db.error)
                if row:
                    return haxdb.data.output(success=0, meta=meta, message="NODE ALREADY REGISTERED ON THIS IP.")

                sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_NAME, NODES_READONLY, NODES_DBA, NODES_IP, NODES_ENABLED, NODES_QUEUED)
                    VALUES (%s,%s,%s,'1','0',%s,'0','1')
                    """
                api_key = base64.urlsafe_b64encode(os.urandom(500))[5:260]
                node_name = "%s %s REGISTERED (RFID)" % (person["PEOPLE_NAME_FIRST"], person["PEOPLE_NAME_LAST"])
                db.query(sql, (api_key, person["PEOPLE_ID"], node_name, ip,))
                if db.error:
                    return haxdb.data.output(success=0, meta=meta, message=db.error)
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

        if node["ASSETS_RFID_REQUIRE_RFID"] != None and int(node["ASSETS_RFID_REQUIRE_RFID"]) != 1:
            # NODE DOES NOT REQUIRE RFID
            # TODO: LOG ASSET_USAGE
            message = "%s\n%s" % (node["ASSETS_NAME"], node["ASSETS_RFID_STATUS"])
            return haxdb.data.output(success=1, meta=meta, message=message)

        if not rfid:
            # TODO: LOG ASSET_USAGE
            message = "%s\n%s" % (node["ASSETS_NAME"], node["ASSETS_RFID_STATUS"])
            return haxdb.data.output(success=0, meta=meta, message=message)

        if not node["PEOPLE_ID"]:
            # TODO: DEAUTH ASSET
            return haxdb.data.output(success=0, meta=meta, message="RFID NOT RECOGNIZED.")

        if node["ASSETS_RFID_REQUIRE_AUTH"] != None and int(node["ASSETS_RFID_REQUIRE_AUTH"]) != 1:
            message = "%s\n%s %s\nNO AUTHORIZE REQUIRED" % (
                node["ASSETS_NAME"], node["PEOPLE_NAME_FIRST"], node["PEOPLE_NAME_LAST"])
            return haxdb.data.output(success=0, meta=meta, message=message)

        if not node["ASSET_AUTHS_ID"]:
            # TODO: DEAUTH ASSET
            message = "%s\n%s %s\nNOT AUTHORIZED" % (
                node["ASSETS_NAME"], node["PEOPLE_NAME_FIRST"], node["PEOPLE_NAME_LAST"])
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

    @haxdb.app.route("/ASSETS_RFID/view", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_ASSETS_RFID_view(rowid=None):
        def calc_row(row):
            row["ASSETS_RFID_IN_USE"] = 0
            if row["ASSETS_RFID_AUTH_LAST"] and row["ASSETS_RFID_AUTH_TIMEOUT"] and (time.time() - int(row["ASSETS_RFID_AUTH_LAST"])) < row["ASSETS_RFID_AUTH_TIMEOUT"]:
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

    @haxdb.app.route("/ASSETS_RFID/save", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/save/<int:rowid>/<col>/<path:val>", methods=["POST", "GET"])
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
        db.query(sql, (rowid,), squelch=True)
        db.commit()

        sql = """
        UPDATE ASSETS_RFID SET {}=%s WHERE ASSETS_RFID_ASSETS_ID = %s
        """
        params = (val, rowid,)

        return apis["ASSETS_RFID"].save_call(sql, params, meta, col, val)

    @haxdb.app.route("/PEOPLE_RFID/list", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/list/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_PEOPLE_RFID_list(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id") or haxdb.data.var.get("people_id")
        apis["PEOPLE_RFID"].context_id(context_id)

        sql = """
        SELECT * FROM PEOPLE WHERE PEOPLE_ID=%s
        """
        row = db.qaf(sql, (context_id,))
        meta = {}
        meta["context_name"] = "{} {}".format(row["PEOPLE_NAME_FIRST"],row["PEOPLE_NAME_LAST"])

        sql = """
        SELECT PR.*, UDF_NAME, UDF_DATA_VALUE
        FROM
        (
        SELECT PEOPLE_RFID.*, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM PEOPLE_RFID
        JOIN PEOPLE ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID
        ) PR
        """
        return apis["PEOPLE_RFID"].list_call(sql=sql, meta=meta)

    @haxdb.app.route("/PEOPLE_RFID/new", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/new/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_new(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id") or haxdb.data.var.get("people_id")
        apis["PEOPLE_RFID"].context_id(context_id)
        return apis["PEOPLE_RFID"].new_call()

    @haxdb.app.route("/PEOPLE_RFID/save", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE_RFID/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_save(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["PEOPLE_RFID"].save_call(rowid=rowid)

    @haxdb.app.route("/PEOPLE_RFID/delete", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE_RFID/delete/<int:rowid>", methods=["GET", "POST"])
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
