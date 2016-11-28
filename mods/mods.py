import os
import sys
from flask import Blueprint

mods = {}
config = None
haxdb = None
db = None

def init(app_config, app_haxdb, app_db):
    global config, haxdb, db
    config = app_config
    haxdb = app_haxdb
    db = app_db
        
        
def run():
    global mods, config, haxdb, db
    sys.path.insert(0,config["MOD"]["PATH"])
    mod_names = [name for name in os.listdir(config["MOD"]["PATH"]) if os.path.isdir(os.path.join(config["MOD"]["PATH"], name))]

    print "MOD.init(): ",
    for mod_name in mod_names:
        print mod_name,
        mod = __import__(mod_name)
        mod.init(config, db, haxdb)
        mods[mod_name] = mod
    print ""
    
    print "MOD.run(): ",        
    for mod in mods:
        print mod,
        mods[mod].run()
    print ""
