from switchinfo.SwitchSNMP.exceptions import SNMPError
from switchinfo.load_info.load_vlan import load_vlan

from switchinfo.management.commands import SwitchBaseCommand


class Command(SwitchBaseCommand):
    help = 'Import vlans from switches'

    def handle(self, *args, **options):
        for switch in self.handle_arguments(options):
            print(switch)
            try:
                load_vlan(switch, silent=False)
            except SNMPError as e:
                print(switch, e)
                continue
