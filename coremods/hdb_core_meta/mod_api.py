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
            md = dict(haxdb.mod_def[mdname])
            md_perm = md["AUTH"]["READ"]
            u_perm = 0
            if mdname in perms:
                u_perm = perms[mdname]["read"]
            if (dba==1) or (md_perm <=0) or (u_perm >= md_perm):
                mod_def[mdname] = md

            sql = """
                SELECT * FROM UDF
                LEFT OUTER JOIN LISTS ON LISTS_ID = UDF_LISTS_ID
                WHERE UDF_TABLE=%s AND UDF_ENABLED=1
                """
            r = haxdb.db.query(sql, (mdname,))
            for udf in r:
                print udf
                fieldname = "{}_UDF{}".format(mdname, udf["UDF_NUM"])
                colrperm = 0
                if udf["UDF_AUTH_READ"]:
                    colrperm = int(udf["UDF_AUTH_READ"])
                if (dba==1) or (rperm is not None and rperm >= colrperm):
                    col = {
                        "CATEGORY": udf["UDF_CATEGORY"],
                        "NAME": fieldname,
                        "HEADER": udf["UDF_NAME"],
                        "TYPE": udf["UDF_TYPE"],
                        "LIST_NAME": udf["LISTS_NAME"],
                        "ID_API": udf["UDF_API"],
                        "EDIT": 1,
                        "QUERY": 1,
                        "SEARCH": 0,
                        "REQUIRED": 0,
                        "DEFAULT": None,
                        "NEW": 0,
                        "AUTH": {
                            "READ": udf["UDF_AUTH_READ"],
                            "WRITE": udf["UDF_AUTH_WRITE"],
                            }
                    }
                    mod_def[mdname]["COLS"].append(col)

        raw = {
          "mods": mod_def,
          "lists": haxdb.func("LISTS:GET")(),
          "queries": haxdb.func("QUERY:GET:ALL")(people_id=pid),
          "fieldsets": haxdb.func("FIELDSET:GET:ALL")(people_id=pid),
        }
        return haxdb.response(success=1, raw=raw)
