# from datetime import datetime
from pprint import pprint

from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone
import switchinfo.load_info.switch_info as switch_info


class Command(BaseCommand):
    help = 'Get info/add a switch'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        ip = options['switch'][0]
        community = options['switch'][1]
        print(switch_info.switch_info(ip, community, silent=False))
