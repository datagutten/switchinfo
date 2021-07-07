from switchinfo.SwitchSNMP.exceptions import SNMPError
from switchinfo.load_info.load_mac import load_mac
from switchinfo.management.commands import SwitchBaseCommand
from switchinfo.models import Vlan


class Command(SwitchBaseCommand):
    help = 'Import MAC-addresses from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['switch'][0] == 'vlan':
            vlan = Vlan.objects.get(vlan=options['switch'][1])
            switches = vlan.on_switch.all()
        else:
            switches = self.handle_arguments({'switch': options['switch'][0]})

        for switch in switches:
            try:
                load_mac(switch)
            except SNMPError as e:
                print(switch, e)
                continue
