from flask import request
import time
import base64
import os

methods = ["GET", "POST"]

haxdb = None
db = None
config = None
apis = {}


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
    pass
