from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/MEMBERSHIPS/list", methods=haxdb.METHOD)
    def MEMBERSHIPS_list():
        return haxdb.api.list_call(mod_def["MEMBERSHIPS"])

    @haxdb.route("/MEMBERSHIPS/view", methods=haxdb.METHOD)
    def MEMBERSHIPS_view():
        return haxdb.api.view_call(mod_def["MEMBERSHIPS"])

    @haxdb.route("/MEMBERSHIPS/new", methods=haxdb.METHOD)
    def MEMBERSHIPS_new():
        return haxdb.api.new_call(mod_def["MEMBERSHIPS"])

    @haxdb.route("/MEMBERSHIPS/delete", methods=haxdb.METHOD)
    def MEMBERSHIPS_delete():
        return haxdb.api.delete_call(mod_def["MEMBERSHIPS"])

    @haxdb.route("/MEMBERSHIPS/save", methods=haxdb.METHOD)
    def MEMBERSHIPS_save():
        return haxdb.api.save_call(mod_def["MEMBERSHIPS"])
