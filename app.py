#!/usr/bin/python

import logging
from config import config
import db
import haxdb
import mods

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config, db.db(config["DB"], logger), logger)

mods.init(haxdb)
mods.run()

app = haxdb.app


if __name__ == "__main__":
    haxdb.run()
