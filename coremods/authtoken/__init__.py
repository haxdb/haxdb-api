import mod_db
import mod_api
import mod_tools


def init(haxdb):
    mod_db.init(haxdb)
    mod_api.init(haxdb)
    return {}


def run():
    mod_db.run()
    mod_api.run()
