from functools import wraps
from flask import Flask
import os, time
from datetime import timedelta
from flask_cors import CORS
from data import *

app = Flask("hdbapi")
app.secret_key = os.urandom(24)

VERSION = "v1"
config = None
db = None

def run():
    debug = (int(config["DEBUG"]) == 1)
    CORS(app, origin=config["ORIGINS"])
    app.permanent_session_lifetime = timedelta(seconds=int(config["SESSION_TIMEOUT"]))
    app.run(config["HOST"],int(config["PORT"]), debug=debug)
    

def require_auth(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        key = session.get("api_key")
        authenticated = session.get("api_authenticated")

        if not (key and authenticated==1):
            return output(success=0, info="NOT AUTHENTICATED", authenticated=False)
        return view_function(*args, **kwargs)

    return decorated_function

def require_dba(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        dba = session.get("api_dba")
        if (not dba or (dba and int(dba) != 1)):
            return output(success=0, info="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


def no_readonly(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        readonly = session.get("api_readonly")

        if (readonly and readonly==1):
            return output(success=0, info="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function
