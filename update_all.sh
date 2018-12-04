#!/usr/bin/env bash
# https://kvz.io/blog/2013/11/21/bash-best-practices/
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 ${__dir}/manage.py load_vlans all
python3 ${__dir}/manage.py load_interfaces_rfc all
python3 ${__dir}/manage.py load_mac all
