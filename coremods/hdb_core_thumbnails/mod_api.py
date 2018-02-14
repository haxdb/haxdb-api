haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    @haxdb.route("/THUMBNAIL/<table>", methods=haxdb.METHOD)
    def THUMBNAIL_download_all(table):
        pass

    @haxdb.route("/THUMBNAIL/<table>/<rowid>", methods=haxdb.METHOD)
    def THUMBNAIL_download(table, rowid):
        pass
