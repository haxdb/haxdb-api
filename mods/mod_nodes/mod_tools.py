import time, base64, re, os, urllib2, json

class tool_error:

    message = ""
    
    def __init__(self, msg):
        self.message = msg
    
    def __bool__(self):
        return False
    __nonzero__ = __bool__
    
    def __repr__(self):
        return str(self.message)
    __str__ = __repr__
    

haxdb = None
db = None
config = None

def init(app_config, app_db, app_haxdb):
    global haxdb, db, config
    haxdb = app_haxdb
    db = app_db
    config = app_config

def get_people(email=None, people_id=None):

    people = None
    if people_id:
        db.query("SELECT * FROM PEOPLE WHERE PEOPLE_ID=%s", (people_id,))
        people = db.next()
        if not people:
            return None
        email = people["PEOPLE_EMAIL"]
    elif email:
        email = email.upper()
        db.query("SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL=%s", (email,))
        people = db.next()
        if not people:
            return None
        return people

    dbas = [x.strip().upper() for x in config["AUTH"]["DBA"].split(',')]
    if email in dbas and people["PEOPLE_DBA"] != 1:
        db.query("UPDATE PEOPLE SET PEOPLE_DBA=1 WHERE PEOPLE_ID=%s", people["PEOPLE_ID"])
        db.commit()
        people["PEOPLE_DBA"] = 1

    return people

    

def get_api_key(nodes_id):
    db.query("SELECT * FROM NODES WHERE NODES_ID=%s", (nodes_id,))
    row = db.next()
    if row and row["NODES_API_KEY"]:
        return row
    else:
        return tool_error(db.error)
    
def create_api_key():
    return base64.urlsafe_b64encode(os.urandom(500))[5:260]

