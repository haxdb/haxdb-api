from mod_def import mod_def
from flask import request

haxdb = None
apis = {}


def init(hdb):
    global haxdb
    haxdb = hdb

    @haxdb.route("/ASSETNODES/register")
    def ASSETNODES_register():
        # REGISTER ASSET NODE
        # - DBA rfid required
        # - NODE and ASSETNODE crated
        # - api_key returned
        name = haxdb.get("name") or "NEW ASSETNODE NODE"
        rfid = haxdb.get("rfid")
        dba = haxdb.func("RFID:DBA")(rfid)

        if not dba:
            msg = "AWAITING ADMIN RFID"
            return haxdb.response(success=0, message=msg)

        ip = str(request.access_route[-1])
        api_key, rowid = haxdb.func("ASSETNODE:CREATE")(name, ip=ip)

        sensors = haxdb.get("sensors")
        haxdb.func("ASSETSENSORS:CREATE")(rowid, sensors)

        raw = {
            "api_key": api_key,
        }
        msg = "WELCOME TO THE HIVE!"
        return haxdb.response(success=1, message=msg, raw=raw)

    @haxdb.route("/ASSETNODES/pulse")
    def ASSETNODES_pulse():
        # PULSE from ASSETNODE
        # if rfid exists update and log usage
        # if sensor[] sent update and log values
        # return open and auth status
        api_key = haxdb.get("api_key")
        rfid = haxdb.get("rfid")
        sensors = haxdb.get("sensors")

        raw = {
            "code": 0,
        }

        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw["code"] = -1
            raw["message"] = "REGISTER ASSETNODE"
            return haxdb.response(success=0, raw=raw)

        if node["ASSETNODES_ENABLED"] != 1:
            raw["code"] = -2
            raw["message"] = "ASSETNODE DISABLED"
            return haxdb.response(success=0, raw=raw)

        if not node["ASSETS_ID"]:
            raw["code"] = -3
            raw["message"] = "ASSETNODE UNASSIGNED"
            return haxdb.response(success=0, raw=raw)

        raw["assetName"] = node["ASSETS_NAME"]
        raw["assetId"] = node["ASSETS_ID"]

        if sensors:
            haxdb.func("ASSETNODE:SENSE")(node, sensors)

        if node["ASSETNODES_RESTRICTED"] != 1:
            raw["code"] = 1
            return haxdb.response(success=1, raw=raw)

        if rfid:
            return haxdb.func("ASSETNODE:AUTH")(node, rfid)

        return haxdb.response(success=1, raw=raw)

    @haxdb.route("/ASSETNODES/sense")
    def ASSETNODES_sense():
        # SENSE call from ASSETNODE
        # update and log sensor[] values
        api_key = haxdb.get("api_key")
        sensors = haxdb.get("sensors")
        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw = {
                "registered": 0,
                "code": -1,
                "message": "UNREGISTERED NODE",
            }
            return haxdb.response(success=0, raw=raw)

        haxdb.func("ASSETNODE:SENSE")(node, sensors)
        return haxdb.response(success=1)

    @haxdb.route("/ASSETNODES/list", methods=haxdb.METHOD)
    def ASSETNODES_list():
        return haxdb.api.list_call(mod_def["ASSETNODES"])

    @haxdb.route("/ASSETNODES/view", methods=haxdb.METHOD)
    def ASSETNODES_view():
        return haxdb.api.view_call(mod_def["ASSETNODES"])

    @haxdb.route("/ASSETNODES/new", methods=haxdb.METHOD)
    def ASSETNODES_new():
        return haxdb.api.new_call(mod_def["ASSETNODES"])

    @haxdb.route("/ASSETNODES/delete", methods=haxdb.METHOD)
    def ASSETNODES_delete():
        return haxdb.api.delete_call(mod_def["ASSETNODES"])

    @haxdb.route("/ASSETNODES/save", methods=haxdb.METHOD)
    def ASSETNODES_save():
        return haxdb.api.save_call(mod_def["ASSETNODES"])


def run():
    pass
