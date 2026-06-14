from django.db import DataError

from switchinfo import models
from switchinfo.SwitchSNMP.select import get_switch


def load_arp(switch: models.Switch):
    device = get_switch(switch)
    arp = device.arp()
    for mac, ip in arp.items():
        try:
            arp_db = models.Arp(mac=mac, ip=ip)
            arp_db.save()
        except DataError as error:
            print(error)
            print(mac)
