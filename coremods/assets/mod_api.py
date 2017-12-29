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
    @haxdb.route("/ASSETS/list", methods=methods)
    def mod_assets_list():
        return haxdb.api.list_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/view", methods=methods)
    def mod_assets_view():
        return haxdb.api.view_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/new", methods=methods)
    def mod_assets_new():
        return haxdb.api.new_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/delete", methods=methods)
    def mod_assets_delete():
        return haxdb.api.delete_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/save", methods=methods)
    def mod_assets_save():
        return haxdb.api.save_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/upload", methods=methods)
    def mod_ASSETS_upload():
        return haxdb.api.upload_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/download", methods=methods)
    def mod_assets_download(rowid=None):
        return haxdb.api.download_call(mod_def["ASSETS"])

    @haxdb.route("/ASSETS/thumbnail", methods=methods)
    def mod_assets_thumbnail():
        return haxdb.api.thumbnail_call(mod_def["ASSETS"])

    #################################################
    # /ASSETURLS
    #################################################

    @haxdb.route("/ASSETURLS/list", methods=methods)
    def mod_asset_links_list():
        return haxdb.api.list_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/new", methods=methods)
    def mod_asset_links_new():
        return haxdb.api.new_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/save", methods=methods)
    def mod_asset_links_save():
        return haxdb.api.save_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/delete", methods=methods)
    def mod_asset_links_delete():
        return haxdb.api.delete_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/upload", methods=methods)
    def mod_ASSETURLS_upload():
        return haxdb.api.upload_call(mod_def["ASSETURLS"])

    @haxdb.route("/ASSETURLS/download", methods=methods)
    def mod_ASSETURLS_download():
        return haxdb.api.download_call(mod_def["ASSETURLS"])

    #################################################
    # /ASSETAUTHS
    #################################################

    @haxdb.route("/ASSETAUTHS/list", methods=methods)
    def mod_ASSETAUTHS_list():
        return haxdb.api.list_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/new", methods=methods)
    def mod_ASSETAUTHS_new():
        return haxdb.api.new_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/delete", methods=methods)
    def mod_ASSETAUTHS_delete():
        return haxdb.api.delete_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/save", methods=methods)
    def mod_asset_auths_save():
        return haxdb.api.save_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/upload", methods=methods)
    def mod_ASSETAUTHS_upload():
        return haxdb.api.upload_call(mod_def["ASSETAUTHS"])

    @haxdb.route("/ASSETAUTHS/download", methods=methods)
    def mod_ASSETAUTHS_download():
        return haxdb.api.download_call(mod_def["ASSETAUTHS"])
