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
        data = request.get_json()
        name = data.get("name") or "NEW ASSETNODE NODE"
        rfid = data.get("rfid")
        dba = haxdb.func("RFID:DBA")(rfid)

        if not dba:
            msg = "AWAITING ADMIN RFID"
            return haxdb.response(success=0, message=msg)

        ip = str(request.access_route[-1])
        api_key, rowid = haxdb.func("ASSETNODE:CREATE")(name, ip=ip)

        sensors = data.get("sensors")
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
        data = request.get_json()
        api_key = data.get("api_key")
        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw = {
                "registered": 0,
            }
            msg = "UNREGISTERED NODE"
            return haxdb.response(success=0, message=msg, raw=raw)

        haxdb.func("ASSETNODE:RFID")(node, data.get("rfid"))
        haxdb.func("ASSETNODE:SENSE")(node, data.get("sensors"))

        raw = {
            "registered": 1,
            "name": node.get("ASSETNODES_NAME"),
            "restricted": node.get("ASSETNODES_RESTRICTED"),
            "asset": node.get("ASSETS_NAME")
        }
        return haxdb.response(success=1, raw=raw)


    @haxdb.route("/ASSETNODES/sense")
    def ASSETNODES_sense():
        # SENSE call from ASSETNODE
        # update and log sensor[] values
        data = request.get_json()
        api_key = data.get("api_key")
        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw = {
                "registered": 0,
            }
            msg = "UNREGISTERED NODE"
            return haxdb.response(success=0, message=msg, raw=raw)

        haxdb.func("ASSETNODE:SENSE")(node, data.get("sensors"))
        return haxdb.response(success=1)


    @haxdb.route("/ASSETNODES/auth")
    def ASSETNODES_auth():
        # AUTH call from ASSETNODE
        # return success=1 if successful AUTH
        data = request.get_json()
        api_key = data.get("api_key")
        node = haxdb.func("ASSETNODE:GET")(api_key)
        if not node:
            raw = {
                "registered": 0,
            }
            msg = "UNREGISTERED NODE"
            return haxdb.response(success=0, message=msg, raw=raw)

        if node["ASSETNODES_RESTRICTED"] != 1:
            msg = "NOT RESTRICTED"
            return haxdb.response(success=1, message=msg)

        rfid = data.get("rfid")
        r = haxdb.func("ASSETNODE:AUTH")(node, rfid)
        if not r:
            msg = "PERMISSION DENIED"
            return haxdb.response(success=0, message=msg)

        n = "{} {}".format(r["PEOPLE_NAME_FIRST"], r["PEOPLE_NAME_LAST"])
        raw = {
            "name": n,
        }
        msg = "PERMISSION GRANTED"
        return haxdb.response(success=1, message=msg, raw=raw)


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
