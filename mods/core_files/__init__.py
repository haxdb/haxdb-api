import mod_db

db = None
config = None
haxdb = None


def init(app_haxdb, mod_config):
    global config, db, haxdb
    haxdb = app_haxdb
    config = mod_config
    db = haxdb.db

    mod_db.init(db, config)


def run():
    mod_db.run()
