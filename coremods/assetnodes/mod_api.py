from flask import request
import time
import base64
import os

methods = ["GET", "POST"]

haxdb = None
apis = {}


def init(hdb, cfg):
    global haxdb, apis
    haxdb = hdb

    for api_name in mod_def.keys():
        apis[api_name] = api.api_call(mod_def[api_name])


def run():
    pass
