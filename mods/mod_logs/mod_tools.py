import time, base64, re, os

haxdb = None
db = None
config = None

def init(app_config, app_db, app_haxdb):
    global haxdb, db, config
    haxdb = app_haxdb
    db = app_db
    config = app_config

