from mod_def import mod_def

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    @haxdb.route("/THUMBNAIL/upload/<table>/<rowid>", methods=haxdb.METHOD)
    def THUMBNAIL_upload (table, rowid):
        pass

    @haxdb.route("/THUMBNAIL/download/<table>/<rowid>", methods=haxdb.METHOD)
    def THUMBNAIL_download (table, rowid):
        pass
