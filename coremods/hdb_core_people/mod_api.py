from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/PEOPLE/list", methods=haxdb.METHOD)
    def PEOPLE_list():
        return haxdb.api.list_call(mod_def["PEOPLE"])

    @haxdb.route("/PEOPLE/view", methods=haxdb.METHOD)
    def PEOPLE_view():
        return haxdb.api.view_call(mod_def["PEOPLE"])

    @haxdb.route("/PEOPLE/new", methods=haxdb.METHOD)
    def PEOPLE_new():
        return haxdb.api.new_call(mod_def["PEOPLE"])

    @haxdb.route("/PEOPLE/delete", methods=haxdb.METHOD)
    def PEOPLE_delete():
        return haxdb.api.delete_call(mod_def["PEOPLE"])

    @haxdb.route("/PEOPLE/save", methods=haxdb.METHOD)
    def PEOPLE_save():
        return haxdb.api.save_call(mod_def["PEOPLE"])
