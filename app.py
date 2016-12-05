#!/usr/bin/python

from config import config
import db, haxdb, mods
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config["API"], db.db(config["DB"], logger), logger)
mods.init(config, haxdb, haxdb.db)
mods.run()

app = haxdb.app


if __name__ == "__main__":
    haxdb.run()



