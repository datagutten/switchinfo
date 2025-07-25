#!/usr/bin/env bash

git config --global --add safe.directory /var/www/Config
git config --global user.email "config@backup.local"
git config --global user.name "Config backup"
chown -R www-data /var/www/Config

apache2-foreground