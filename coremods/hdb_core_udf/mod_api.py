from mod_def import mod_def
import mod_func

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/UDF/list", methods=haxdb.METHOD)
    def UDF_list():
        return haxdb.api.list_call(mod_def["UDF"])

    @haxdb.route("/UDF/view", methods=haxdb.METHOD)
    def UDF_view():
        return haxdb.api.view_call(mod_def["UDF"])

    @haxdb.route("/UDF/save", methods=haxdb.METHOD)
    def UDF_save():
        response = haxdb.api.save_call(mod_def["UDF"])
        mod_func.extend_mod_def()
        return response
