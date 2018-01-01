from mod_def import mod_def

haxdb = None
methods = ["POST", "GET"]


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    #################################################
    # /ASSETS
    #################################################
    @haxdb.route("/ASSETS/list", methods=haxdb.METHOD)
    def ASSETS_list():
        return haxdb.api.list_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/view", methods=haxdb.METHOD)
    def ASSETS_view():
        return haxdb.api.view_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/new", methods=haxdb.METHOD)
    def ASSETS_new():
        return haxdb.api.new_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/delete", methods=haxdb.METHOD)
    def ASSETS_delete():
        return haxdb.api.delete_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/save", methods=haxdb.METHOD)
    def ASSETS_save():
        return haxdb.api.save_call(mod_def["ASSETS"])

    #################################################
    # /ASSETURLS
    #################################################

    @haxdb.route("/ASSETURLS/list", methods=haxdb.METHOD)
    def ASSETURLS_list():
        return haxdb.api.list_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/view", methods=haxdb.METHOD)
    def ASSETURLS_view():
        return haxdb.api.view_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/new", methods=haxdb.METHOD)
    def ASSETURLS_new():
        return haxdb.api.new_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/delete", methods=haxdb.METHOD)
    def ASSETURLS_delete():
        return haxdb.api.delete_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/save", methods=haxdb.METHOD)
    def ASSETURLS_save():
        return haxdb.api.save_call(mod_def["ASSETURLS"])

    #################################################
    # /ASSETAUTHS
    #################################################

    @haxdb.route("/ASSETAUTHS/list", methods=haxdb.METHOD)
    def ASSETAUTHS_list():
        return haxdb.api.list_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/view", methods=haxdb.METHOD)
    def ASSETAUTHS_view():
        return haxdb.api.view_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/new", methods=haxdb.METHOD)
    def ASSETAUTHS_new():
        return haxdb.api.new_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/delete", methods=haxdb.METHOD)
    def ASSETAUTHS_delete():
        return haxdb.api.delete_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/save", methods=haxdb.METHOD)
    def ASSETAUTHS_save():
        return haxdb.api.save_call(mod_def["ASSETAUTHS"])
