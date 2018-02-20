
haxdb = None


def send_email(receiver, subject, msg):
    import smtplib
    try:
        ename = haxdb.config["EMAIL"]["NAME"]
        efrom = haxdb.config["EMAIL"]["FROM"]
        ehost = haxdb.config["EMAIL"]["HOST"]
        eport = haxdb.config["EMAIL"]["PORT"]
        euser = haxdb.config["EMAIL"]["USER"]
        epass = haxdb.config["EMAIL"]["PASS"]
        etls = int(haxdb.config["EMAIL"]["TLS"])

        sender = "{} <{}>".format(ename, efrom)
        header = "From: {}\n".format(sender)
        header += "To: {}\n".format(receiver)
        header += "Subject: {}\n".format(subject)
        header += "\r\n\r\n"
        msg = header + msg

        server = smtplib.SMTP(ehost, eport, None, 10)
        if etls == 1:
            server.starttls()
        if euser and epass:
            server.login(euser, epass)
        server.sendmail(sender, receiver, msg)
        server.quit()
    except smtplib.SMTPServerDisconnected:
        return haxdb.error("EMAIL SERVER DISCONNECTED")
    except smtplib.SMTPDataError:
        return haxdb.error("EMAIL DATA ERROR")
    except smtplib.SMTPConnectError:
        return haxdb.error("EMAIL CONNECT ERROR")
    except smtplib.SMTPRecipientsRefused:
        return haxdb.error("INVALID EMAIL ADDRESS")
    except smtplib.SMTPAuthenticationError:
        return haxdb.error("MISCONFIGURED EMAIL")
    except smtplib.SMTPHeloError:
        return haxdb.error("HELO ERROR")
    except smtplib.SMTPSenderRefused:
        return haxdb.error("SENDER REFUSED")
    except smtplib.SMTPResponseException, e:
        print e.smtp_code, e.smtp_error
        return haxdb.error(e.smtp_error)
    except smtplib.SMTPException:
        return haxdb.error("FAILED TO SEND EMAIL")
    return True


def init(hdb):
    global haxdb
    haxdb = hdb
    haxdb.func("EMAIL:SEND", send_email)
    return {}


def run():
    pass
