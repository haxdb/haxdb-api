from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/QUERY/list", methods=haxdb.METHOD)
    def QUERY_list():
        return haxdb.api.list_call(mod_def["QUERY"])

    @haxdb.route("/QUERY/view", methods=haxdb.METHOD)
    def QUERY_view():
        return haxdb.api.view_call(mod_def["QUERY"])

    @haxdb.route("/QUERY/new", methods=haxdb.METHOD)
    def QUERY_new():
        return haxdb.api.new_call(mod_def["QUERY"])

    @haxdb.route("/QUERY/delete", methods=haxdb.METHOD)
    def QUERY_delete():
        return haxdb.api.delete_call(mod_def["QUERY"])

    @haxdb.route("/QUERY/save", methods=haxdb.METHOD)
    def QUERY_save():
        return haxdb.api.save_call(mod_def["QUERY"])
