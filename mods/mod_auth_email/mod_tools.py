import time
import base64
import re
import os
import urllib2
import json


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


haxdb = None
db = None
config = None


def init(app_config, app_db, app_haxdb):
    global haxdb, db, config
    haxdb = app_haxdb
    db = app_db
    config = app_config


def send_email(receiver, subject, msg):

    sender = "%s <%s>" % (config["EMAIL"]["NAME"], config["EMAIL"]["FROM"])
    header = "From: %s\n" % sender
    header += "To: %s\n" % receiver
    header += "Subject: %s\n" % subject
    header += "\r\n\r\n"
    msg = header + msg

    import smtplib
    try:
        server = smtplib.SMTP(config["EMAIL"]["HOST"], config["EMAIL"]["PORT"], None, 10)
        server.starttls()
        server.login(config["EMAIL"]["USER"], config["EMAIL"]["PASS"])
        server.sendmail(sender, receiver, msg)
        server.quit()
    except smtplib.SMTPRecipientsRefused:
        return tool_error("INVALID EMAIL ADDRESS")
    except smtplib.SMTPException:
        return tool_error("FAILED TO SEND EMAIL")
    return True
