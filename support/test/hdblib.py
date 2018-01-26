class hdb:
    debug = False
    host = "http://localhost:8080/"
    api_key = None

    def api(self, call, data):
        url = self.host
        if call[0] != "/":
            url += "/"
        url += call

        if "api_key" not in data:
            data["api_key"] = self.api_key

        r = json.loads(requests.get(url, data=data).text)

        if self.debug:
            print "############################"
            print "CALL: {}".format(call)
            print "DATA: {}".format(data)
            print "----------------------------"
            print r
            print "############################"

        return r

    def auth_email(self, email):
        return self.api("AUTH/EMAIL", {"email": email})

    def authtoken(self, token):
        r = self.api("AUTH/TOKEN", {"token": token})
        if r["success"] != 1:
            return False
        self.api_key = r["api_key"]
        return True
