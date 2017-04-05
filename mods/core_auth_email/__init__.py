import mod_db
import mod_api
import mod_tools

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

    mod_tools.init(config, db, haxdb)
    mod_db.init(db, config)
    mod_api.init(haxdb, mod_config, mod_tools)


def run():
    mod_db.run()
    mod_api.run()
