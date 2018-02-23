# Quick and Dirty Install

This is a very quick install on a Ubuntu 16.04.  This will get a single
instance up and going and is meant for testing/development purposes and not
production.

---
```
sudo apt install python-pip python-dev git virtualenv
```


```
git clone https://github.com/haxdb/haxdb-api.git haxdb
cd haxdb
virtualenv env
source env/bin/activate
pip install Flask Flask-CORS msgpack-python Pillow
cp haxdb.cfg-example haxdb.cfg
```
Now edit haxdb.cfg with the settings you want.  

---

Then run the app:
```
./app.py
```
---

If you want to test using MariaDB then install the connector and edit haxdb.cfg file use TYPE = MARIADB
```
pip install mysql-connector-python-rf
```
