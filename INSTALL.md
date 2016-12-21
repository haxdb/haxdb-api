# Quick and Dirty Install
This is an example of installing the haxdb api on an ubuntu 16.04 system but other distro's can be deduced from this info.
---

Install dependencies
```
sudo apt-get install python-pip python-dev virtualenv git
```

Create haxdb user and change to that user.
```
sudo adduser haxdb
su - haxdb
```

Clone repo and then set up environment
```
mkdir www
cd www
git clone https://github.com/jondale/haxdb.git haxdb-api
cd haxdb-api
virtualenv haxdb-env
source haxdb-env/bin/activate
pip install Flask Flask-CORS msgpack-python gunicorn mysql-connector-python-rf
```

Copy the example config file and then edit it to your settings
```
cp haxdb.cfg-example haxdb.cfg

```

At this point you should be able to type ./app.py and have it start on whatever port you chose in the config.

---

## Set up as a service

Create ***/etc/systemd/system/haxdb.service***
```
[Unit]
Description=haxdb api service
After=network.target

[Service]
User=haxdb
Group=www-data
WorkingDirectory=/home/haxdb/www/haxdb-api
Environment="PATH=/home/haxdb/www/haxdb-api/haxdb-env/bin"
ExecStart=/home/haxdb/www/haxdb-api/haxdb-env/bin/gunicorn --workers 5 --bind unix:haxdb.sock -m 007 --error-logfile /home/haxdb/www/haxdb-api/error.log app:app

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl start haxdb

sudo systemctl status haxdb
```
This should show your gunicorn workers started.  If an error occured you can check /home/haxdb/www/haxdb-api/error.log for more information.

---

# Setting up nginx

Now that you have your gunicorn workers you can set up nginx as a proxy to serve it up.

Install nginx
```
sudo apt install nginx git
```


Create **/etc/nginx/sites-available/haxdb-api**
```
server {
    listen 80;
    server_name haxdb-api.mydomain.tld;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/haxdb/www/haxdb-api/haxdb.sock;
        add_header Access-Control-Allow-Origin *;
    }
}
```

Enable the site (and remove default if desired)
```
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/haxdb-api /etc/nginx/sites-enabled/haxdb-api
service nginx restart
```

Use letsencrypt to add ssl.
```
git clone https://github.com/certbot/certbot.git
cd certbot
./certbot-auto --nginx
```

---

# Set up MariaDB
By default haxdb uses sqlite but maybe you have thousands of users or just prefer something a bit more.  Future plans also include support for postgresql.

Install MariaDB
```
sudo apt install mariadb-server
```

Create haxdb database and user
```
sudo mysql
create user haxdb;
grant all privileges on haxdb.* to 'haxdb'@'localhost' identified by 'supersecretpassword';
flush privileges;
```

Don't forget to edit your haxdb.cfg file and change the [DB] settings
```
[DB]
DEBUG = 1
ENABLED = 1
TYPE = MARIADB
HOST = localhost
PORT = 3306
USER = haxdb
PASS = supersecretpassword
DB = haxdb
```
