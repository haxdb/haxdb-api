haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    @haxdb.route("/AUTH/email", methods=["GET", "POST"])
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
        config_dbas = haxdb.config["CORE_AUTHEMAIL"]["DBA"].split(',')
        config_dbas = [x.strip().upper() for x in config_dbas]
        if email not in config_dbas:
            sql = "SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL = %s"
            people = db.qaf(sql, (email,))
            if not people:
                msg = "UNKNOWN EMAIL"
                return haxdb.response(success=0, message=msg)

        # CREATE TOKEN
        token = haxdb.func("AUTHTOKEN_CREATE")()

        # SEND EMAIL
        to = email
        subject = haxdb.config["CORE_AUTHEMAIL"]["AUTH_SUBJECT"]
        if tokenurl:
            message = haxdb.config["CORE_AUTHEMAIL"]["AUTH_BODY"]
            message = message.replace("[tokenurl]", tokenurl)
        else:
            message = haxdb.config["CORE_AUTHEMAIL"]["AUTH_BODY_NOURL"]
        message = message.replace("[token]", token)
        result = haxdb.func("EMAIL_SEND")(to, subject, message)
        if not result:
            return haxdb.response(success=0, message=result)
        return haxdb.response(success=1, message="EMAIL SENT")
