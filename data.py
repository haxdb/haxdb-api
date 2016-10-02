from flask import session as sess, jsonify, request
import time

def output(success=0, info=None, data=None, rows=None, authenticated=True):
    out = {}
    out["success"] = success
    out["info"] = info
    out["timestamp"] = time.time()
    out["authenticated"] = 1 if authenticated else 0
    if data: 
        data.update(out)
        out = data
    if rows:
        out["rows"] = rows
    return jsonify(out)


class get_class:
    def get(self, key):
        return request.args.get(key) or self.getlist(key)

    def getlist(self, key):
        return request.args.getlist(key) or request.args.getlist(key+"[]")

    def __getitem__(self, key):
        return self.get(key)
    
class post_class:
    def get(self, key):
        return request.form.get(key) or self.getlist(key)

    def getlist(self, key):
        return request.form.getlist(key) or request.form.getlist(key+"[]")
    
    def __getitem__(self, key):
        return self.get(key)

class session_class:
    def get(self, key):
        if key in sess:
            return sess[key]
        return None

    def set(self, key, val):
        sess[key] = val
        
    def __getitem__(self, key):
        return self.get(key)

    def clear(self):
        sess.clear()
    

class data_class:
    def get(self, key, use_session=False):
        val = None
        val = post.get(key)
        if not val:
            val = get.get(key)
        if not val and use_session:
            val = session.get(key)
        return val

    def __getitem__(self, key):
        return self.get(key)
    
    
get = get_class()
post = post_class()
session = session_class()
data = data_class()