from flask import session as sess, jsonify, json, request
import msgpack
import time

def output(success=0, message=None, value=None, data=None, meta=None, authenticated=True):
    output_format = var.get("format")
    include_meta = var.get("meta")
    
    out = {}
    if include_meta: out["meta"] = meta
    out["success"] = success
    out["value"] = value
    out["message"] = message

    if output_format and output_format in ("min"):
        return json.dumps(out)

    if output_format and output_format == "msgpack":
        return msgpack.packb(out)

    out["timestamp"] = time.time()
    out["authenticated"] = 1 if authenticated else 0
    out["data"] = None if not data else data

    return json.dumps(out)


class get_class:
    def get(self, key):
        return request.args.get(key) or None

    def getlist(self, key):
        return request.args.getlist(key) or request.args.getlist(key+"[]") or None

    def __getitem__(self, key):
        return self.get(key)
    
class post_class:
    def get(self, key):
        return request.form.get(key) or None

    def getlist(self, key):
        return request.form.getlist(key) or request.form.getlist(key+"[]") or None
    
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
    

class var_class:
    def get(self, key, use_session=False):
        val = None
        val = post.get(key)
        if not val:
            val = get.get(key)
        if not val and use_session:
            val = session.get(key)
        return val

    def getlist(self, key):
        val = None
        val = post.getlist(key)
        if not val:
            val = get.getlist(key)
        return val
    
    def __getitem__(self, key):
        return self.get(key)
    
    
get = get_class()
post = post_class()
session = session_class()
var = var_class()