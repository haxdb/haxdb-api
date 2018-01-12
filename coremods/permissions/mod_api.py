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
        people_id = haxdb.get("PEOPLE_ID")
        perms = {}
        for mod_def in haxdb.mod_def:
            row = {
                "TABLE": mod_def["name"],
                "READ": 0,
                "WRITE": 0,
                "INSERT": 0,
                "DELETE": 0,
            }
            perms[row["TABLE"]] = row
        raw = {"data": data}
        return haxdb.response(success=1, raw=raw)

    @haxdb.route("/PEOPLEPERMS/save", methods=haxdb.METHOD)
    def PEOPLEPERMS_save():
        return haxdb.api.save_call(mod_def["PEOPLEPERMS"])

    @haxdb.route("/NODEPERMS/view", methods=haxdb.METHOD)
    def NODEPERMS_view():
        return haxdb.api.view_call(mod_def["NODEPERMS"])

    @haxdb.route("/NODEPERMS/list", methods=haxdb.METHOD)
    def NODEPERMS_list():
        return haxdb.api.list_call(mod_def["NODEPERMS"])

    @haxdb.route("/NODEPERMS/save", methods=haxdb.METHOD)
    def NODEPERMS_save():
        return haxdb.api.save_call(mod_def["NODEPERMS"])
