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

        if not api_key:
            if haxdb.db.error:
                msg = haxdb.db.error
            else:
                msg = "UNKNOWN ERROR"
            return haxdb.response(success=0, message=msg)

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
            "node": {
                "id": None,
                "name": None,
                "registered": 0,
                "enabled": 0,
                "restricted": 1,
                "approval": 1,
                "asset": {
                    "id": None,
                    "name": None,
                },
            },
            "rfid": {
                "valid": 0,
                "approved": 0,
                "person": {
                    "id": None,
                    "name": None,
                },
            },
            "engage": 0,
            "message": "",
        }

        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw["message"] = "REGISTER ASSETNODE"
            return haxdb.response(raw=raw)

        raw["node"]["registered"] = 1
        raw["node"]["id"] = node.get("ASSETNODES_ID", None)
        raw["node"]["name"] = node.get("ASSETNODES_NAME", None)
        raw["node"]["enabled"] = node.get("ASSETNODES_ENABLED", 0)
        raw["node"]["restricted"] = node.get("ASSETNODES_RESTRICTED", 1)
        raw["node"]["approval"] = node.get("ASSETNODES_APPROVAL", 1)

        if node["ASSETNODES_ENABLED"] != 1:
            raw["message"] = "NOT ENABLED"
            return haxdb.response(raw=raw)

        if not node["ASSETS_ID"]:
            raw["message"] = "NO ASSET ASSIGNED"
            return haxdb.response(raw=raw)

        raw["node"]["asset"]["id"] = node.get("ASSETS_ID")
        raw["node"]["asset"]["name"] = node.get("ASSETS_NAME")

        if sensors:
            haxdb.func("ASSETNODE:SENSE")(node, sensors)

        if node["ASSETNODES_RESTRICTED"] != 1:
            raw["engage"] = 1
            return haxdb.response(raw=raw)

        if rfid:
            return haxdb.func("ASSETNODE:AUTH")(raw, rfid)

        haxdb.func("ASSETNODE:OPERATOR")(raw["node"]["id"], None)
        return haxdb.response(raw=raw)

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
