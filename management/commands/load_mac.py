# from datetime import datetime

from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone

from switchinfo.models import Interface, Switch, Vlan, Mac
from switchinfo.load_info.load_mac import load_mac
from easysnmp.exceptions import EasySNMPTimeoutError

# from pprint import pprint


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
            load_mac(switch)
