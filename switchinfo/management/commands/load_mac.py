from django.core.management.base import BaseCommand

from switchinfo.SwitchSNMP.exceptions import SNMPError
from switchinfo.load_info.load_mac import load_mac
from switchinfo.models import Switch, Vlan


class Command(BaseCommand):
    help = 'Import MAC-addresses from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['switch'][0] == 'vlan':
            vlan = Vlan.objects.get(vlan=options['switch'][1])
            switches = vlan.on_switch.all()
        elif not options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()

        for switch in switches:
            try:
                load_mac(switch)
            except SNMPError as e:
                print(switch, e)
                continue
