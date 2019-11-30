from django.core.management.base import BaseCommand  # , CommandError
from easysnmp.exceptions import EasySNMPTimeoutError

from switchinfo.load_info.load_interfaces import load_interfaces
from switchinfo.models import Switch


class Command(BaseCommand):
    help = 'Import ports from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()

        for switch in switches:
            print(switch.name)
            try:
                load_interfaces(switch)
            except ValueError as error:
                print(error)
                continue
            except EasySNMPTimeoutError:
                print('Timeout connecting to %s' % switch)
                continue
