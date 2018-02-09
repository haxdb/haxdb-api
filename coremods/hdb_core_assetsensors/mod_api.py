from mod_def import mod_def

haxdb = None
apis = {}


def init(hdb):
    global haxdb
    haxdb = hdb

    @haxdb.route("/ASSETSENSORS/list", methods=haxdb.METHOD)
    def ASSETSENSORS_list():
        return haxdb.api.list_call(mod_def["ASSETSENSORS"])

    @haxdb.route("/ASSETSENSORS/view", methods=haxdb.METHOD)
    def ASSETSENSORS_view():
        return haxdb.api.view_call(mod_def["ASSETSENSORS"])

    @haxdb.route("/ASSETSENSORS/new", methods=haxdb.METHOD)
    def ASSETSENSORS_new():
        return haxdb.api.new_call(mod_def["ASSETSENSORS"])

    @haxdb.route("/ASSETSENSORS/delete", methods=haxdb.METHOD)
    def ASSETSENSORS_delete():
        return haxdb.api.delete_call(mod_def["ASSETSENSORS"])

    @haxdb.route("/ASSETSENSORS/save", methods=haxdb.METHOD)
    def ASSETSENSORS_save():
        return haxdb.api.save_call(mod_def["ASSETSENSORS"])


def run():
    pass
