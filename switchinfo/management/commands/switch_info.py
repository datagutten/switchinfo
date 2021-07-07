from django.core.management.base import BaseCommand

import switchinfo.load_info.switch_info as switch_info
from switchinfo.SwitchSNMP.exceptions import SNMPError


class Command(BaseCommand):
    help = 'Get info/add a switch'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        ip = options['switch'][0]
        community = options['switch'][1]
        try:
            print(switch_info.switch_info(ip, community, silent=False))
        except SNMPError as e:
            print(e)
