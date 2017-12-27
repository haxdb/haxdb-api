#! /usr/bin/env python

import logging
from config import config
import db
import haxdb
import coremods
import usermods
import api

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config, db.db(config["DB"], logger), logger)
api.init(haxdb)

coremods.init(haxdb, api)
coremods.run()

usermods.init(haxdb)
usermods.run()

app = haxdb.app

if __name__ == "__main__":
    haxdb.run()
