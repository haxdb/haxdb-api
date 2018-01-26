from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/FILES/list", methods=haxdb.METHOD)
    def FILES_list():
        return haxdb.api.list_call(mod_def["FILES"])

    @haxdb.route("/FILES/view", methods=haxdb.METHOD)
    def FILES_view():
        return haxdb.api.view_call(mod_def["FILES"])

    @haxdb.route("/FILES/new", methods=haxdb.METHOD)
    def FILES_new():
        return haxdb.api.new_call(mod_def["FILES"])

    @haxdb.route("/FILES/delete", methods=haxdb.METHOD)
    def FILES_delete():
        return haxdb.api.delete_call(mod_def["FILES"])

    @haxdb.route("/FILES/save", methods=haxdb.METHOD)
    def FILES_save():
        return haxdb.api.save_call(mod_def["FILES"])
