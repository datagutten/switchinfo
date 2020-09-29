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