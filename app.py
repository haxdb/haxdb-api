#!/usr/bin/python

from config import config
import db, haxdb, mods

haxdb.init(config["API"], db.db(config["DB"]))
mods.init(config, haxdb, haxdb.db)
mods.run()

app = haxdb.app

if __name__ == "__main__":
    haxdb.run()



