import switchinfo.load_info.switch_info as switch_info
from snmp_compat import snmp_exceptions
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.management.commands import SwitchBaseCommand


class Command(SwitchBaseCommand):
    help = 'Update info about a switch'

    def handle(self, *args, **options):

        for switch in self.handle_arguments(options):
            print(switch)
            try:
                device = get_switch(switch)
                print(switch_info.switch_info(device=device))
            except snmp_exceptions.SNMPError as e:
                print(switch, e)
                continue
