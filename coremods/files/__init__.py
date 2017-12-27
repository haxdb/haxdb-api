import mod_db
import mod_func

db = None
config = None
haxdb = None
api = None


def init(app_haxdb, app_api, mod_config):
    global config, db, haxdb, api
    haxdb = app_haxdb
    config = mod_config
    db = haxdb.db
    api = app_api

    mod_db.init(db, config)
    mod_func.init(haxdb)


def run():
    mod_db.run()
    mod_func.run()
