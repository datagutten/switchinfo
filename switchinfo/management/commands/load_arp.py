from snmp_compat import snmp_exceptions

from switchinfo.load_info import load_arp
from switchinfo.management.commands import SwitchBaseCommand


class Command(SwitchBaseCommand):
    help = 'Import ARP from switches'

    def handle(self, *args, **options):
        for switch in self.handle_arguments(options):
            print(switch)
            try:
                load_arp(switch)
            except snmp_exceptions.SNMPError as e:
                print(e)
                continue
