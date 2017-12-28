import mod_api


def init(app_haxdb, app_api, mod_config):
    haxdb = app_haxdb
    mod_api.init(haxdb)
    return {}


def run():
    mod_db.run()
    mod_api.run()
