from django.core.management.base import BaseCommand  # , CommandError

from switchinfo.SwitchSNMP import exceptions
from switchinfo.load_info.load_vlan import load_vlan
from switchinfo.models import Switch


class Command(BaseCommand):
    help = 'Import vlans from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()
        for switch in switches:
            print(switch)
            try:
                load_vlan(switch, silent=False)
            except exceptions.SNMPError:
                print('Timeout connecting to %s' % switch)
                continue
