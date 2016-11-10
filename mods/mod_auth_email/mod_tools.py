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
    
    print "4.1"
    
    import smtplib
    try:
        print "4.2"
        server = smtplib.SMTP(config["EMAIL"]["HOST"], config["EMAIL"]["PORT"],None,10)
        print "4.3"
        server.starttls()
        print "4.4"
        server.login(config["EMAIL"]["USER"], config["EMAIL"]["PASS"])
        print "4.5"
        server.sendmail(sender, receiver, msg)
        print "4.6"
        server.quit()
        print "4.7"
    except smtplib.SMTPRecipientsRefused:
        return tool_error("INVALID EMAIL ADDRESS")
    except smtplib.SMTPException:
        return tool_error("FAILED TO SEND EMAIL")
    print "4.8"
    return True

def get_api_key(nodes_id):
    db.query("SELECT * FROM NODES WHERE NODES_ID=?", (nodes_id,))
    row = db.next()
    if row and row["NODES_API_KEY"]:
        return row
    else:
        return tool_error(db.error)
    
def create_api_key(nodes_name, dba, readonly, people_id, people_default=False):

    api_key = base64.urlsafe_b64encode(os.urandom(500))[5:260]

    sql = "INSERT INTO NODES (NODES_NAME, NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_STATUS) VALUES (?,?,?,?,?,'1','1')"
    db.query(sql,(nodes_name, api_key, people_id, readonly, dba))
    db.commit()
    if db.rowcount > 0:
        nodes_id = db.lastrowid
        key = get_api_key(nodes_id)
        if people_default:
            sql = "UPDATE PEOPLE SET PEOPLE_NODES_ID=? WHERE PEOPLE_ID=?"
            db.query(sql,(nodes_id,people_id))
            db.commit()
        return key
    else:
        return tool_error(db.error)
    
def get_people_api_key(people_id):
    people = get_people(people_id=people_id)
    if people:
        key = None
        
        if people["PEOPLE_NODES_ID"]:
            key = get_api_key(people["PEOPLE_NODES_ID"])
        
        if not key:
            key = create_api_key(people["PEOPLE_EMAIL"] + " EMAIL AUTH", people["PEOPLE_DBA"], 0, people["PEOPLE_ID"], True)

        if not key:
            return key
        
        if key["NODES_DBA"] != people["PEOPLE_DBA"]:
            db.query("UPDATE NODES SET NODES_DBA=? WHERE NODES_ID=?", (people["PEOPLE_DBA"], key["NODES_ID"]))
            db.commit()
                
        return key["NODES_API_KEY"]

    return tool_error("UNKNOWN USER")
        
def api_get(call):
    url = config["API"]["URL"] + call
    response = urllib2.urlopen(url)
    if response:
        data = json.load(response)
        if data:
            return data
    return None
