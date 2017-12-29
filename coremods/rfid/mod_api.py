from flask import request
import time
import base64
import os

methods = ["GET", "POST"]

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


def init(app_haxdb, api, mod_config, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    for api_name in mod_def.keys():
        apis[api_name] = api.api_call(mod_def[api_name])


def get_person(rfid=None):
    if not rfid:
        return None

    sql = """
        SELECT PEOPLE_ID, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST, PEOPLE_DBA
        FROM PEOPLE
        JOIN PEOPLE_RFID ON PEOPLE_RFID_PEOPLE_ID = PEOPLE_ID
        WHERE
        PEOPLE_RFID_RFID = %s
        AND PEOPLE_RFID_RFID IS NOT NULL
        AND PEOPLE_RFID_RFID != ''
        AND PEOPLE_RFID_ENABLED = 1
        LIMIT 1
    """
    return db.qaf(sql, (rfid,))


def build_udf_join(udf_name=None, rowid=None):
    sql = """
        LEFT OUTER JOIN (
        SELECT UDF_DATA_ROWID, UDF_DATA_VALUE AS "{}"
        FROM UDF
        JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
        WHERE
        UDF_NAME='{}'
        ) UDF_{} ON UDF_{}.UDF_DATA_ROWID={}
    """.format(udf_name, udf_name, udf_name, udf_name, rowid)
    return sql


def get_asset(asset=None):
    if not asset:
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
    return db.qaf(sql, (asset,))


def is_person_authed(asset=None, person=None):
    if not asset or not person:
        return False

    sql = """
        SELECT *
        FROM ASSET_AUTHS
        WHERE
        ASSET_AUTHS_ASSETS_ID = %s
        AND ASSET_AUTHS_PEOPLE_ID = %s
        AND ASSET_AUTHS_ENABLED=1
    """
    row = db.qaf(sql, (asset, person))
    if row:
        return True
    return False


def get_node(api_key=None):
    if not api_key:
        return None

    sql = """
        SELECT * FROM NODES
        WHERE NODES_API_KEY = %s
    """
    return db.qaf(sql, (api_key,))


def register_node(ip=None, node_name=None):
    ip = ip or ""
    node_name = node_name or "NEWLY REGISTERED NODE"
    api_key = base64.urlsafe_b64encode(os.urandom(500))[5:39]

    sql = """
        INSERT INTO NODES (NODES_API_KEY, NODES_NAME, NODES_IP, NODES_ENABLED)
        VALUES (%s, %s, %s, 0)
    """
    db.query(sql, (api_key, node_name, ip))
    if db.rowcount > 0:
        db.commit()
        return api_key
    return False


def boolval(val):
    try:
        val = int(val)
    except (ValueError, TypeError) as e:
        return False
    if val == 1:
        return True
    return False


def run():
    @haxdb.route("/ASSETS_RFID/pulse", methods=methods)
    @haxdb.route("/ASSETS_RFID/pulse/<rfid>", methods=methods)
    @haxdb.route("/ASSETS_RFID/pulse/<rfid>/<status>", methods=methods)
    def mod_rfid_asset_pulse(rfid=None, status=None):
        api_key = haxdb.get("api_key")
        rfid = rfid or haxdb.get("rfid")
        status = status or haxdb.get("status")
        ip = str(request.access_route[-1])

        node = get_node(api_key)
        person = get_person(rfid)

        if not node:
            # API KEY DOES NOT MATCH A NODE.
            # REGISTER IF RFID MATCHES DBA.

            if not rfid:
                # NO API KEY OR RFID SENT
                msg = "UNREGISTERED"
                return haxdb.output(success=0, message=msg)

            if not person:
                # UNKNOWN OR DISABLED RFID
                msg = "INVALID RFID"
                return haxdb.output(success=0, message=msg)

            if not boolval(person["PEOPLE_DBA"]):
                # RFID MATCHES BUT NOT A DBA
                msg = "MUST BE DBA TO REGISTER"
                return haxdb.output(success=0, message=msg)

            # RFID MATCHES WITH DBA
            new_api_key = register_node(ip=ip)
            edata = {
                "ip": ip,
                "person": dict(person),
            }
            haxdb.trigger("API.RFID.NODE_REGISTRATION", edata)
            msg = "NODE REGISTERED\n"
            msg += "ACTIVATION REQUIRED."
            return haxdb.output(success=0, value=new_api_key, message=msg)

        else:
            # API KEY MATCHES NODE

            if not boolval(node["NODES_ENABLED"]):
                msg = "NODE REGISTERED\nNOT ACTIVE"
                return haxdb.output(success=0, message=msg)

            asset = get_asset(node["NODES_ASSETS_ID"])

            if not asset:
                # NO ASSET ASSIGNED TO NODE
                msg = "NO ASSET ASSIGNED"
                return haxdb.output(success=0, message=msg)

            if not boolval(asset["REQUIRE_RFID"]):
                # NO RFID REQUIRED TO ACTIVATE
                msg = "{}\nACTIVATED".format(asset["ASSETS_NAME"])
                return haxdb.output(success=1, message=msg)

            # VALID RFID REQUIRED
            if not person:
                # NO VALID RFID
                if not rfid:
                    msg = "{}".format(asset["ASSETS_NAME"])
                else:
                    msg = "{}\nINVALID RFID".format(asset["ASSETS_NAME"])
                return haxdb.output(success=0, message=msg)

            if not boolval(asset["REQUIRE_AUTH"]):
                # ONLY VALID RFID REQUIRED
                edata = {
                    "person": dict(person),
                    "asset": dict(asset),
                }
                haxdb.trigger("API.RFID.AUTH", edata)

                msg = "{}\n{} {}".format(asset["ASSETS_NAME"],
                                         person["PEOPLE_NAME_FIRST"],
                                         person["PEOPLE_NAME_LAST"])
                return haxdb.output(success=1, message=msg)

            # VALID RFID AND ASSET AUTH REQUIRED
            if not is_person_authed(asset["ASSETS_ID"], person["PEOPLE_ID"]):
                edata = {
                    "person": dict(person),
                    "asset": dict(asset),
                }
                haxdb.trigger("API.RFID.NO_AUTH", edata)

                msg = "{}\nREQUIRES PRIOR AUTH".format(asset["ASSETS_NAME"])
                return haxdb.output(success=0, message=msg)

            edata = {
                "person": dict(person),
                "asset": dict(asset),
            }
            haxdb.trigger("API.RFID.AUTH", edata)

            msg = "{}\n{} {}".format(asset["ASSETS_NAME"],
                                     person["PEOPLE_NAME_FIRST"],
                                     person["PEOPLE_NAME_LAST"])
            return haxdb.output(success=1, message=msg)


##############################################################################

    @haxdb.route("/PEOPLE_RFID/list", methods=methods)
    @haxdb.route("/PEOPLE_RFID/list/<int:PEOPLE_ID>", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_PEOPLE_RFID_list(PEOPLE_ID=None):
        PEOPLE_ID = PEOPLE_ID or haxdb.get("PEOPLE_ID")

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

    @haxdb.route("/PEOPLE_RFID/new", methods=methods)
    @haxdb.route("/PEOPLE_RFID/new/<int:PEOPLE_ID>", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_new(PEOPLE_ID=None):
        PEOPLE_ID = PEOPLE_ID or haxdb.get("PEOPLE_ID")

        m = {
            "name": get_people_name(PEOPLE_ID),
        }

        defaults = {
            "PEOPLE_RFID_PEOPLE_ID": PEOPLE_ID,
        }
        return apis["PEOPLE_RFID"].new_call(defaults=defaults, meta=m)

    @haxdb.route("/PEOPLE_RFID/save", methods=methods)
    @haxdb.route("/PEOPLE_RFID/save/<int:rowid>", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_save(rowid=None):
        return apis["PEOPLE_RFID"].save_call(rowid=rowid)

    @haxdb.route("/PEOPLE_RFID/delete", methods=methods)
    @haxdb.route("/PEOPLE_RFID/delete/<int:rowid>", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_delete(rowid=None):
        return apis["PEOPLE_RFID"].delete_call(rowid=rowid)

    @haxdb.route("/PEOPLE_RFID/upload", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_upload():
        return apis["PEOPLE_RFID"].upload_call()

    @haxdb.route("/PEOPLE_RFID/download", methods=methods)
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_download(rowid=None):
        return apis["PEOPLE_RFID"].download_call()
