from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone
import switchinfo.load_info.switch_info as switch_info
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.models import Switch
from easysnmp.exceptions import EasySNMPTimeoutError


class Command(BaseCommand):
    help = 'Update info about a switch'

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
                device = get_switch(switch)
                print(switch_info.switch_info(device=device))
            except EasySNMPTimeoutError:
                print('Timeout connecting to %s' % switch)
                continue
