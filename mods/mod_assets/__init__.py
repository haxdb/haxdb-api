import mod_db
import mod_api
import mod_tools

db = None
config = None
haxdb = None


def init(app_config, app_db, app_haxdb):
    global config, db, haxdb
    config = app_config
    db = app_db
    haxdb = app_haxdb

    mod_db.init(db, config)
    mod_api.init(haxdb, mod_def)


def run():
    mod_db.run()
    mod_api.run()
