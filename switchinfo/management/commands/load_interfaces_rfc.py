from switchinfo.SwitchSNMP.exceptions import SNMPError

from switchinfo.load_info.load_interfaces import load_interfaces
from switchinfo.management.commands import SwitchBaseCommand


class Command(SwitchBaseCommand):
    help = 'Load interfaces from switches'

    def handle(self, *args, **options):
        for switch in self.handle_arguments(options):
            print(switch)
            try:
                load_interfaces(switch)
            except SNMPError as e:
                print(e)
                continue
