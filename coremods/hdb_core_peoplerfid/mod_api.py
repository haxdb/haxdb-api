from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/PEOPLERFID/list", methods=haxdb.METHOD)
    def PEOPLERFID_list():
        return haxdb.api.list_call(mod_def["PEOPLERFID"])

    @haxdb.route("/PEOPLERFID/view", methods=haxdb.METHOD)
    def PEOPLERFID_view():
        return haxdb.api.view_call(mod_def["PEOPLERFID"])

    @haxdb.route("/PEOPLERFID/new", methods=haxdb.METHOD)
    def PEOPLERFID_new():
        return haxdb.api.new_call(mod_def["PEOPLERFID"])

    @haxdb.route("/PEOPLERFID/delete", methods=haxdb.METHOD)
    def PEOPLERFID_delete():
        return haxdb.api.delete_call(mod_def["PEOPLERFID"])

    @haxdb.route("/PEOPLERFID/save", methods=haxdb.METHOD)
    def PEOPLERFID_save():
        return haxdb.api.save_call(mod_def["PEOPLERFID"])
