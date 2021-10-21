from django.db.utils import DataError
from switchinfo.SwitchSNMP.exceptions import SNMPError

import switchinfo.SwitchSNMP.utils as utils
from switchinfo.management.commands import SwitchBaseCommand
from switchinfo.models import Arp, Switch
from switchinfo.SwitchSNMP.select import get_switch


class Command(SwitchBaseCommand):
    help = 'Import ARP from switches'

    def handle(self, *args, **options):
        switch: Switch
        for switch in self.handle_arguments(options):
            device = get_switch(switch)
            try:
                arp = device.arp()
            except SNMPError as e:
                print(e)
                continue

            for mac, ip in arp.items():
                if not len(mac) == 12:
                    mac = utils.mac_string(mac)
                try:
                    arp_db = Arp(mac=mac, ip=ip)
                    arp_db.save()
                except DataError as error:
                    print(error)
                    print(mac)
                    print(utils.mac_string(mac))
