# switchinfo

A tool to show what is connected to switch ports

Add new switch:

`python3 manage.py switch_info [switch ip] [snmp community]`

The following brands are tested:

* Cisco
* HPE Aruba
* HP ProCurve (not able to get all information on all models)
* Extreme Networks
* Korenix
* Westermo SDSL modems

Requirements:
https://github.com/xstaticxgpx/netsnmp-py3/

# Setup

## Install dependencies

### Old debian:

`apt-get install libsnmp30 libsnmp-dev libczmq4 libczmq-dev`

### Debian bullseye or newer:

`apt-get install libsnmp40 libsnmp-dev libczmq4 libczmq-dev python3-pip`

`pip3 install pyzmq netsnmp-py django`

## Install the package(s)

### Switchinfo main project

`pip3 install switchinfo`

### Config backup

`pip3 install django-switch-config-backup`

## Create user

`adduser switch_info`

## Create a django project

`django-admin startproject switch_info /home/switch_info`

## Configure the project

`nano /home/switch_info/switch_info/settings.py`

### Set allowed host names

`ALLOWED_HOSTS = ['switchinfo']`

### Add the app(s) to the project

Add to the end of INSTALLED_APPS:

````python
'switchinfo.apps.SwitchinfoConfig',
'config_backup.apps.ConfigBackupConfig',
````

### Set time zone

`USE_TZ = False`
Set TIME_ZONE to your local time zone:
`TIME_ZONE = 'Europe/Oslo`

### Set static root

````python
import os

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
````

### Set root URL configuration

Change `/home/switch_info/switch_info/urls.py` to contain this:

````python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('switchinfo.urls')),
]
````

## Compile netsnmp

apt-get install libperl-dev

## Configure MariDB database (optional)

`apt-get install python3-mysqldb`

Change DATABASES key in settings.py to look something like this:

````python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'switch_info',
        'USER': 'switch_info',
        'PASSWORD': 'asdf',
        'HOST': 'localhost'
    }
}
````

Create database and user:

````sql
CREATE
DATABASE switch_info;
CREATE
USER 'switch_info'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON switch_info.* TO
'switch_info'@'localhost';
FLUSH
PRIVILEGES;
````

### Allow remote root access to MariaDB (optional):

````sql
CREATE
USER 'root'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO
'root'@'%' WITH GRANT OPTION;
FLUSH
PRIVILEGES;
````

`nano /etc/mysql/mariadb.conf.d/50-server.cnf`

Change bind-address to 0.0.0.0

Restart MariaDB server:
`/etc/init.d/mariadb restart`

## Apache vhost:
Copy config to /etc/apache2/sites-available/switchinfo.conf and edit ServerName:

`cp switchinfo.conf /etc/apache2/sites-available/switchinfo.conf`

```
<VirtualHost *:80>
    ErrorLog /var/log/apache2/switch_info_error.log
    CustomLog /var/log/apache2/switch_info_access.log combined
    ServerName switchinfo.yourdomain.local

        Alias /media /home/switch_info/media
        Alias /static /home/switch_info/static
        Alias /gitlist /var/www/html/gitlist
        Alias /loganalyzer /var/www/html/loganalyzer
        <Directory "/var/www/html/gitlist">
                Require all granted
                AllowOverride all
        </Directory>

        <Directory "/home/switch_info/static">
        Require all granted
        </Directory>

        <Directory "/home/switch_info/media">
        Require all granted
        </Directory>

        WSGIDaemonProcess switch_info user=switch_info group=switch_info threads=50 maximum-requests=10000 python-path=/home/switch_info
        WSGIProcessGroup switch_info
        WSGIScriptAlias / /home/switch_info/switch_info/wsgi.py

        <Directory /home/switch_info>
        <Files wsgi.py>
        Require all granted
        </Files>
        </Directory>
</VirtualHost>
```

Install mod-wsgi:
`apt-get install libapache2-mod-wsgi-py3`

Create user:
`adduser switch_info`

Remove default site:
`rm 000-default.conf`

Enable site:
`a2ensite switchinfo`

Initialize database and collect static files:

```
python3 manage.py collectstatic
python3 manage.py migrate
python3 manage.py createsuperuser
```

## Load OUI

`python3 manage.py load_oui`