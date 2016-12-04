#!/usr/bin/python

from config import config
import db, haxdb, mods

haxdb.init(config["API"], db.db(config["DB"]))
haxdb.db.open()
mods.init(config, haxdb, haxdb.db)
mods.run()
haxdb.db.close()

app = haxdb.app

if __name__ == "__main__":
    haxdb.run()



