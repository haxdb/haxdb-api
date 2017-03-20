#!/usr/bin/python

import logging
from config import config
import db
import haxdb
import mods
import api

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config, db.db(config["DB"], logger), logger)
api.init(haxdb)

mods.init(haxdb, api)
mods.run()

app = haxdb.app


if __name__ == "__main__":
    haxdb.run()
