#!/usr/bin/python

from config import config
import db, api, mods

haxdb = db.db(config["DB"])
api.db = haxdb
api.config = config["API"]
    
mods.init(config, api, haxdb)
mods.run()

app = api.app

if __name__ == "__main__":
    api.run()



