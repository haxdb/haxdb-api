import mod_db
import mod_api
import mod_tools


def init(haxdb):
    haxdb.mod2db(mod_def)
    mod_api.init(haxdb)
    return {}


def run():
    mod_api.run()
