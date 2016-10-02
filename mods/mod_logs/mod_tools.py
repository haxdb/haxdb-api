import time, base64, re, os

api = None
db = None
config = None

def init(app_config, app_db, app_api):
    global api, db, config
    api = app_api
    db = app_db
    config = app_config

