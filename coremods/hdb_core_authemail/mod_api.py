import re

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    @haxdb.route("/AUTH/email", methods=haxdb.METHOD)
    def mod_auth_email():
        tokenurl = haxdb.get("tokenurl")
        email = haxdb.get("email")
        if not email:
            msg = "EMAIL IS REQUIRED"
            return haxdb.response(success=0, message=msg)
        email = email.upper()

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "INVALID EMAIL"
            return haxdb.response(success=0, message=msg)

        # EMAIL EXISTS OR DBA IN CONFIG
        config_dbas = haxdb.config["AUTHEMAIL"]["DBA"].split(',')
        config_dbas = [x.strip().upper() for x in config_dbas]

        sql = "SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL = %s"
        people = haxdb.db.qaf(sql, (email,))
        if not people:
            if email in config_dbas:
                people = haxdb.func("PEOPLE:CREATE")(email=email, dba=1)
            if not people:
                msg = "UNKNOWN EMAIL"
                return haxdb.response(success=0, message=msg)
        pid = people["PEOPLE_ID"]

        # CREATE TOKEN
        token = haxdb.func("AUTHTOKEN:CREATE")(people_id=pid)

        # SEND EMAIL
        to = email
        subject = haxdb.config["AUTHEMAIL"]["EMAIL_SUBJECT"]
        if tokenurl:
            message = haxdb.config["AUTHEMAIL"]["EMAIL_BODY"]
            message = message.replace("[tokenurl]", tokenurl)
        else:
            message = haxdb.config["AUTHEMAIL"]["EMAIL_BODY_NOURL"]
        message = message.replace("[token]", token)
        result = haxdb.func("EMAIL:SEND")(to, subject, message)
        if not result:
            return haxdb.response(success=0, message=result)
        return haxdb.response(success=1, message="EMAIL SENT")
