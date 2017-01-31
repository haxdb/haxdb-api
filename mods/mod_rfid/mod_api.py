from flask import request
import time

haxdb = None
db = None
config = None
apis = {}


def get_people_name(rowid):
        sql = """
        SELECT * FROM PEOPLE WHERE PEOPLE_ID=%s
        """
        row = db.qaf(sql, (rowid,))
        if not row:
            return None
        return "{} {}".format(row["PEOPLE_NAME_FIRST"],
                              row["PEOPLE_NAME_LAST"])


def init(app_haxdb, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def get_person(rfid=None):
    if not rfid:
        return None

    sql = """
        SELECT PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST, PEOPLE_DBA
        FROM PEOPLE
        JOIN PEOPLE_RFID ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_RFID_PEOPLE_ID
        WHERE
        PEOPLE_RFID_RFID = %s
        AND PEOPLE_RFID_RFID IS NOT NULL
        AND PEOPLE_RFID_RFID != ''
        AND PEOPLE_RFID_ENABLED = 1
    """
    return db.qaf(sql, (rfid,))


def build_udf_join(udf_name=None, rowid=None):
    sql = """
        LEFT OUTER JOIN (
        SELECT UDF_DATA_VALUE AS "{}"
        FROM UDF
        JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
        WHERE
        UDF_NAME='{}'
        AND UDF_DATA_ROWID={}
        ) UDF_{}
    """.format(udf_name, udf_name, rowid, udf_name)


def get_asset(rowid=None):
    if not rowid:
        return None

    sql = """
        SELECT ASSETS_ID, ASSETS_NAME, ASSETS_LOCATION,
        AUTO_LOG, REQUIRE_RFID, REQUIRE_AUTH, STATUS, STATUS_DESC
        FROM ASSETS
    """
    sql += build_udf_join("AUTO_LOG", "ASSETS_ID")
    sql += build_udf_join("REQUIRE_RFID", "ASSETS_ID")
    sql += build_udf_join("REQUIRE_AUTH", "ASSETS_ID")
    sql += build_udf_join("STATUS", "ASSETS_ID")
    sql += build_udf_join("STATUS_DESC", "ASSETS_ID")
    sql += """
        WHERE ASSETS_ID=%s
    """
    return db.qaf(sql, (rowid,))


def get_node(api_key=None):
    if not api_key:
        return None

    sql = """
        SELECT * FROM NODES
        WHERE NODES_API_KEY = %s
    """
    return db.qaf(sql, (api_key,))


def run():
    @haxdb.app.route("/ASSETS_RFID/pulse", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/pulse/<rfid>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/pulse/<rfid>/<status>", methods=["POST", "GET"])
    def mod_rfid_asset_pulse(rfid=None, status=None):
        api_key = haxdb.data.var.get("api_key")
        rfid = rfid or haxdb.data.var.get("rfid")
        status = status or haxdb.data.var.get("status")
        ip = str(request.access_route[-1])

        meta = {}
        meta["api"] = "ASSETS_RFID"
        meta["action"] = "pulse"
        meta["rfid"] = rfid
        meta["status"] = status

        node = get_node(api_key)
        if not node:
            # API KEY DOES NOT MATCH A NODE.
            # REGISTER IF RFID MATCHES DBA.

            if not rfid:
                # NO API KEY OR RFID SENT
                msg = "UNREGISTERED"
                return haxdb.data.output(success=0, message=msg)

            person = get_person(rfid)
            if not person:
                # RFID DOES NOT MATCH person
                msg = "INVALID RFID"
                return haxdb.data.output(success=0, message=msg)

    # TODO: FINISH pulse refactor

##############################################################################

    @haxdb.app.route("/PEOPLE_RFID/list", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/list/<int:PEOPLE_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_PEOPLE_RFID_list(PEOPLE_ID=None):
        PEOPLE_ID = PEOPLE_ID or haxdb.data.var.get("PEOPLE_ID")

        m = {
            "name": get_people_name(PEOPLE_ID),
        }

        t = """
        (
        SELECT PEOPLE_RFID.*, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM PEOPLE_RFID
        JOIN PEOPLE ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID
        WHERE
        PEOPLE_ID=%s
        )
        """
        p = (PEOPLE_ID,)
        return apis["PEOPLE_RFID"].list_call(table=t, params=p, meta=m)

    @haxdb.app.route("/PEOPLE_RFID/new", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/new/<int:PEOPLE_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_new(PEOPLE_ID=None):
        PEOPLE_ID = PEOPLE_ID or haxdb.data.var.get("PEOPLE_ID")

        m = {
            "name": get_people_name(PEOPLE_ID),
        }

        defaults = {
            "PEOPLE_RFID_PEOPLE_ID": PEOPLE_ID,
        }
        return apis["PEOPLE_RFID"].new_call(defaults=defaults, meta=m)

    @haxdb.app.route("/PEOPLE_RFID/save", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE_RFID/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_save(rowid=None):
        return apis["PEOPLE_RFID"].save_call(rowid=rowid)

    @haxdb.app.route("/PEOPLE_RFID/delete", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE_RFID/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_delete(rowid=None):
        return apis["PEOPLE_RFID"].delete_call(rowid=rowid)
