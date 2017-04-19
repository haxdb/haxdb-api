## Dev install for a mac

This will get a single instance up and going and is meant for testing/development purposes and not production.

After forking your own repo:
```
pip install virtualenv
git clone https://github.com/<your username>/haxdb-api.git haxdb
cd haxdb
virtualenv -p /usr/bin/python2.7 env
source env/bin/activate
pip install Flask Flask-CORS msgpack-python mysqul-connector-python-rf pillow
cp haxdb.cfg-example haxdb.cfg
cd mods/core_auth_email/mod.cfg-example mod.cfg
'''

Now edit haxdb.cfg and mods/core_auth_email/mod.cfg with the settings you want.


Then to run the app:

'''
./app.py
'''
