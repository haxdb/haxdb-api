haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/META/list", methods=haxdb.METHOD)
    def META_list():
        raw = {
          "data": haxdb.mod_def,
        }
        return haxdb.response(success=1, raw=raw)
