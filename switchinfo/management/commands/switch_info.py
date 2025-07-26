from django.core.management.base import BaseCommand

import switchinfo.load_info.switch_info as switch_info
from snmp_compat import snmp_exceptions


class Command(BaseCommand):
    help = 'Get info/add a switch'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        ip = options['switch'][0]
        community = options['switch'][1]
        try:
            print(switch_info.switch_info(ip, community, silent=False))
        except snmp_exceptions.SNMPError as e:
            print(e)
