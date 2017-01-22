# Quick and Dirty Install

This is a very quick install on a Fedora 25 system.  This will get a single
instance up and going and is meant for testing/development purposes and not
production.

---

```
sudo dnf install python-pip python-devel git python2-virtualen
git clone https://github.com/jondale/haxdb.git haxdb
cd haxdb
virtualenv env
source env/bin/activate
pip install Flask Flask-CORS msgpack-python mysql-connector-python-rf
cp haxdb.cfg-example haxdb.cfg
```
Now edit haxdb.cfg and mods/mod_auth_email/mod.cfg with the settings you want.  

---

To then run the app:
```
./app.py
```
