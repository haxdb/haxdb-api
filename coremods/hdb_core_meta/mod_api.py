haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/META", methods=haxdb.METHOD)
    def META_list():
        pid = haxdb.session("people_id")
        raw = {
          "mods": haxdb.mod_def,
          "lists": haxdb.func("LISTS:GET")(),
          "queries": haxdb.func("QUERY:GET:ALL")(people_id=pid),
          "fieldsets": haxdb.func("FIELDSET:GET:ALL")(people_id=pid),
        }
        return haxdb.response(success=1, raw=raw)
