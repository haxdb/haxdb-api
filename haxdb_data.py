from flask import session as sess, request


class get_class:

    def get(self, key):
        return request.args.get(key)

    def getlist(self, key):
        return request.args.getlist(key) or request.args.getlist(key + "[]")

    def __getitem__(self, key):
        return self.get(key)


class post_class:

    def get(self, key):
        return request.form.get(key)

    def getlist(self, key):
        return request.form.getlist(key) or request.form.getlist(key + "[]")

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
        val = post.get(key)
        if val is None:
            val = get.get(key)
        if val is None and use_session:
            val = session.get(key)
        return val

    def getlist(self, key):
        val = post.getlist(key)
        if val is None:
            val = get.getlist(key)
        return val

    def __getitem__(self, key):
        return self.get(key)


get = get_class()
post = post_class()
session = session_class()
var = var_class()
