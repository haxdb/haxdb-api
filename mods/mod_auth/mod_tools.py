import time, base64, re, os, urllib2, json

class tool_error:

    message = ""
    
    def __init__(self, msg):
        self.message = msg
    
    def __bool__(self):
        return False
    __nonzero__ = __bool__
    
    def __repr__(self):
        return self.message
    __str__ = __repr__
    

api = None
db = None
config = None

def init(app_config, app_db, app_api):
    global api, db, config
    api = app_api
    db = app_db
    config = app_config

def valid_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True
    
def create_token(email):
    token = base64.urlsafe_b64encode(os.urandom(500))[5:260]
    expire = time.time() + int(config["AUTH"]["TOKEN_EXPIRE"])

    db.query("INSERT INTO AUTH_TOKEN (AUTH_TOKEN_TOKEN, AUTH_TOKEN_EMAIL, AUTH_TOKEN_EXPIRE) VALUES (?,?,?)", (token,email,expire))
    db.commit()

    if db.rowcount != 1:
        return tool_error(db.error)
    return token

def verify_token(token):
    db.query("SELECT * FROM AUTH_TOKEN WHERE AUTH_TOKEN_TOKEN=? AND AUTH_TOKEN_EXPIRE>?", (token,time.time()))
    row = db.next()
    if row and row["AUTH_TOKEN_EMAIL"] and row["AUTH_TOKEN_TOKEN"] == token:
        return row["AUTH_TOKEN_EMAIL"]
    else:
        return False

def delete_token(token):
    db.query("DELETE FROM AUTH_TOKEN WHERE AUTH_TOKEN_TOKEN=?", (token,))
    db.commit()
    if db.rowcount != 1:
        return False
    return True

def get_people(email=None, people_id=None):

    people = None
    if people_id:
        db.query("SELECT * FROM PEOPLE WHERE PEOPLE_ID=?", (people_id,))
        people = db.next()
        if not people:
            return None
        email = people["PEOPLE_EMAIL"]
    elif email:
        email = email.upper()
        db.query("SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL=?", (email,))
        people = db.next()
        if not people:
            return None
        return people

    dbas = [x.strip().upper() for x in config["AUTH"]["DBA"].split(',')]
    if email in dbas and people["PEOPLE_DBA"] != 1:
        db.query("UPDATE PEOPLE SET PEOPLE_DBA=1 WHERE PEOPLE_ID=?", people["PEOPLE_ID"])
        db.commit()
        people["PEOPLE_DBA"] = 1

    return people

def create_people(email):
    dba = 0
    dbas = [x.strip().upper() for x in config["AUTH"]["DBA"].split(',')]
    if email.upper() in dbas: dba = 1
    sql = "INSERT INTO PEOPLE (PEOPLE_EMAIL,PEOPLE_DBA) VALUES (?,?)"
    db.query(sql, (email,dba))
    db.commit()
    if db.rowcount != 1:
        return tool_error(db.error)
    people = {}
    people["PEOPLE_ID"] = db.lastrowid
    people["PEOPLE_EMAIL"] = email
    people["PEOPLE_DBA"] = dba
    return people

def send_email(receiver, subject, msg):
    
    sender = "%s <%s>" % (config["EMAIL"]["NAME"], config["EMAIL"]["FROM"])
    header = "From: %s\n" % sender
    header += "To: %s\n" % receiver
    header += "Subject: %s\n" % subject
    header += "\r\n\r\n"
    msg = header + msg
    
    import smtplib
    try:
        server = smtplib.SMTP(config["EMAIL"]["HOST"])
        server.starttls()
        server.login(config["EMAIL"]["USER"], config["EMAIL"]["PASS"])
        server.sendmail(sender, receiver, msg)
        server.quit()
    except smtplib.SMTPRecipientsRefused:
        return tool_error("INVALID EMAIL ADDRESS")
    except smtplib.SMTPException:
        return tool_error("FAILED TO SEND EMAIL")
    
    return True

def get_api_key(api_key_id):
    db.query("SELECT * FROM API_KEYS WHERE API_KEYS_ID=?", (api_key_id,))
    row = db.next()
    if row and row["API_KEYS_KEY"]:
        return row
    else:
        return tool_error(db.error)
    
def create_api_key(dba, readonly, people_id, people_default=False):

    api_key = base64.urlsafe_b64encode(os.urandom(500))[5:260]

    sql = "INSERT INTO API_KEYS (API_KEYS_KEY, API_KEYS_PEOPLE_ID, API_KEYS_READONLY, API_KEYS_DBA) VALUES (?,?,?,?)"
    db.query(sql,(api_key, people_id, readonly, dba))
    db.commit()
    if db.rowcount > 0:
        api_key_id = db.lastrowid
        key = get_api_key(api_key_id)
        if people_default:
            sql = "UPDATE PEOPLE SET PEOPLE_API_KEY_ID=? WHERE PEOPLE_ID=?"
            db.query(sql,(api_key_id,people_id))
            db.commit()
        return key
    else:
        return tool_error(db.error)
    
def get_people_api_key(people_id):
    people = get_people(people_id=people_id)
    if people:
        key = None
        
        if people["PEOPLE_API_KEY_ID"]:
            key = get_api_key(people["PEOPLE_API_KEY_ID"])
        
        if not key:
            key = create_api_key(people["PEOPLE_DBA"], 0, people["PEOPLE_ID"], True)

        if not key:
            return key
        
        if key["API_KEYS_DBA"] != people["PEOPLE_DBA"]:
            db.query("UPDATE API_KEYS SET API_KEYS_DBA=? WHERE API_KEYS_ID=?", (people["PEOPLE_DBA"], key["API_KEYS_ID"]))
            db.commit()
                
        return key["API_KEYS_KEY"]

    return tool_error("UNKNOWN USER")
        
def api_get(call):
    url = config["API"]["URL"] + call
    response = urllib2.urlopen(url)
    if response:
        data = json.load(response)
        if data:
            return data
    return None
