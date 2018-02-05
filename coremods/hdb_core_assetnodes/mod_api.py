from mod_def import mod_def

haxdb = None
apis = {}


def init(hdb):
    global haxdb
    haxdb = hdb

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
