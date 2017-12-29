from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/UDF/list", methods=["POST", "GET"])
    def mod_udf_def_list():
        return haxdb.api.list_call(mod_def["UDF"])


    @haxdb.route("/UDF/new", methods=["POST", "GET"])
    def mod_udf_def_new():
        return haxdb.api.new_call(mod_def["UDF"])

    @haxdb.route("/UDF/delete", methods=["GET", "POST"])
    def mod_udf_def_delete():
        return haxdb.api.delete_call(mod_def["UDF"])

    @haxdb.route("/UDF/save", methods=["GET", "POST"])
    def mod_udf_def_save():
        return haxdb.api.save_call(mod_def["UDF"])
