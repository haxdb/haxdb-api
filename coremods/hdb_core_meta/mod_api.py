haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/META", methods=haxdb.METHOD)
    def META_list():
        dba = haxdb.session("dba")
        pid = haxdb.session("people_id")
        perms = haxdb.func("PERM:GET:ALL")()

        mod_def = {}
        for mdname in haxdb.mod_def:
            md = haxdb.mod_def[mdname]
            md_perm = md["AUTH"]["READ"]
            u_perm = 0
            if mdname in perms:
                u_perm = perms[mdname]["read"]
            if (dba==1) or (md_perm <=0) or (u_perm >= md_perm):
                mod_def[mdname] = md

        raw = {
          "mods": mod_def,
          "lists": haxdb.func("LISTS:GET")(),
          "queries": haxdb.func("QUERY:GET:ALL")(people_id=pid),
          "fieldsets": haxdb.func("FIELDSET:GET:ALL")(people_id=pid),
        }
        return haxdb.response(success=1, raw=raw)