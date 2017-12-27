import time
import base64
import re
import os
import urllib2
import json

haxdb = None


def send_email(receiver, subject, msg):
    global haxdb

    sender = "%s <%s>" % (config["EMAIL"]["NAME"], config["EMAIL"]["FROM"])
    header = "From: %s\n" % sender
    header += "To: %s\n" % receiver
    header += "Subject: %s\n" % subject
    header += "\r\n\r\n"
    msg = header + msg

    import smtplib
    try:
        host = config["EMAIL"]["HOST"]
        port = config["EMAIL"]["PORT"]
        server = smtplib.SMTP(host, port, None, 10)
        server.starttls()
        server.login(config["EMAIL"]["USER"], config["EMAIL"]["PASS"])
        server.sendmail(sender, receiver, msg)
        server.quit()
    except smtplib.SMTPRecipientsRefused:
        return haxdb.error("INVALID EMAIL ADDRESS")
    except smtplib.SMTPException:
        return haxdb.error("FAILED TO SEND EMAIL")
    return True


def init(hdb):
    global haxdb
    haxdb = hdb
    haxdb.func("SEND_EMAIL")
    return {}


def run():
    pass
