from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/FIELDSET/list", methods=haxdb.METHOD)
    def FIELDSET_list():
        return haxdb.api.list_call(mod_def["FIELDSET"])

    @haxdb.route("/FIELDSET/view", methods=haxdb.METHOD)
    def FIELDSET_view():
        return haxdb.api.view_call(mod_def["FIELDSET"])

    @haxdb.route("/FIELDSET/new", methods=haxdb.METHOD)
    def FIELDSET_new():
        return haxdb.api.new_call(mod_def["FIELDSET"])

    @haxdb.route("/FIELDSET/delete", methods=haxdb.METHOD)
    def FIELDSET_delete():
        return haxdb.api.delete_call(mod_def["FIELDSET"])

    @haxdb.route("/FIELDSET/save", methods=haxdb.METHOD)
    def FIELDSET_save():
        return haxdb.api.save_call(mod_def["FIELDSET"])
