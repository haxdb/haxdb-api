from mod_def import mod_def

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
        rfid = haxdb.get("rfid")

        raw = {
            "api_key": None,
        }
        msg = ""
        return haxdb.response(success=1, message=msg, raw=raw)

    @haxdb.route("/ASSETNODES/pulse")
    def ASSETNODES_pulse():
        # PULSE from ASSETNODE
        # if rfid exists update and log usage
        # if sensor[] sent update and log values
        # return open and auth status

        rfid = haxdb.get("rfid")
        sensors = haxdb.get("sensor")

        raw = {
            "open": 0,
            "auth": 1,
        }
        msg = ""
        return haxdb.response(success=1, message=msg, raw=raw)

    @haxdb.route("/ASSETNODES/sense")
    def ASSETNODES_sense():
        # SENSE call from ASSETNODE
        # update and log sensor[] values
        return haxdb.response(success=1)

    @haxdb.route("/ASSETNODES/auth")
    def ASSETNODES_auth():
        # AUTH call from ASSETNODE
        # return success=1 if successful AUTH

        rfid = haxdb.get("rfid")
        msg = ""
        return haxdb.response(success=1, message=msg)

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
