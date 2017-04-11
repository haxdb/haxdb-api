from flask import request
from werkzeug.utils import secure_filename
import os
from PIL import Image
import StringIO

haxdb = None
db = None
config = None
apis = {}

big_maxw = 500
big_maxh = 500
small_maxw = 250
small_maxh = 250


def init(app_haxdb, api, mod_config, mod_def):
    global haxdb, db, config, apis
    global big_maxh, big_maxw, small_maxh, small_maxw

    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    if config and "THUMBS" in config:
        if "BIGW" in config["THUMBS"]:
            big_maxw = config["THUMBS"]["BIGW"]
        if "BIGH" in config["THUMBS"]:
            big_maxw = config["THUMBS"]["BIGH"]
        if "SMALLW" in config["THUMBS"]:
            small_maxw = config["THUMBS"]["SMALLW"]
        if "SMALLH" in config["THUMBS"]:
            small_maxw = config["THUMBS"]["SMALLH"]


def run():

    def thumbs_gen(img=None, file=None):
        if img:
            thumb_big = img.copy()
            thumb_small = img.copy()
            w, h = img.size
        elif file:
            try:
                thumb_big = Image.open(file)
                thumb_small = thumb_big.copy()
                w, h = thumb_big.size
            except Exception:
                return False, False
        else:
            return False, False

        if w > h:
            bigw = big_maxw
            bigh = int(h * (float(bigw)/w))
            smallw = small_maxw
            smallh = int(h * (float(smallw)/w))
        else:
            bigh = big_maxh
            bigw = int(w * (float(bigh)/h))
            smallh = small_maxh
            smallw = int(w * (float(smallh)/h))

        thumb_big = thumb_big.resize((bigw, bigh), Image.ANTIALIAS)
        thumb_small = thumb_small.resize((smallw, smallh), Image.ANTIALIAS)

        big = StringIO.StringIO()
        small = StringIO.StringIO()
        thumb_big.save(big, "PNG")
        thumb_small.save(small, "PNG")
        return big.getvalue(), small.getvalue()

    haxdb.save_function("THUMBS_GEN", thumbs_gen)
