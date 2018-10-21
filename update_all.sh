#!/usr/bin/env bash
python3 manage.py load_vlans all
python3 manage.py load_interfaces_rfc all
python3 manage.py load_mac all
