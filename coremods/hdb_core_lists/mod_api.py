from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    ####################################
    # LISTS
    ####################################

    @haxdb.route("/LISTS/list", methods=haxdb.METHOD)
    def LISTS_list():
        return haxdb.api.list_call(mod_def["LISTS"])

    @haxdb.route("/LISTS/view", methods=haxdb.METHOD)
    def LISTS_view():
        return haxdb.api.view_call(mod_def["LISTS"])

    @haxdb.route("/LISTS/new", methods=haxdb.METHOD)
    def LISTS_new():
        return haxdb.api.new_call(mod_def["LISTS"])

    @haxdb.route("/LISTS/delete", methods=haxdb.METHOD)
    def LISTS_delete():
        return haxdb.api.delete_call(mod_def["LISTS"])

    @haxdb.route("/LISTS/save", methods=haxdb.METHOD)
    def LISTS_save():
        return haxdb.api.save_call(mod_def["LISTS"])

    ####################################
    # LIST_ITEMS
    ####################################

    @haxdb.route("/LIST_ITEMS/list", methods=haxdb.METHOD)
    def LIST_ITEMS_list():
        return haxdb.api.list_call(mod_def["LIST_ITEMS"])

    @haxdb.route("/LIST_ITEMS/view", methods=haxdb.METHOD)
    def LIST_ITEMS_view():
        return haxdb.api.view_call(mod_def["LIST_ITEMS"])

    @haxdb.route("/LIST_ITEMS/new", methods=haxdb.METHOD)
    def LIST_ITEMS_new():
        return haxdb.api.new_call(mod_def["LIST_ITEMS"])

    @haxdb.route("/LIST_ITEMS/delete", methods=haxdb.METHOD)
    def LIST_ITEMS_delete():
        return haxdb.api.delete_call(mod_def["LIST_ITEMS"])

    @haxdb.route("/LIST_ITEMS/save", methods=haxdb.METHOD)
    def LIST_ITEMS_save():
        return haxdb.api.save_call(mod_def["LIST_ITEMS"])
