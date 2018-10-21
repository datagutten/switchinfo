# from datetime import datetime
from pprint import pprint
import requests
import json
from pprint import pprint
from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone

from switchinfo.models import Arp

from .cisco import Cisco
cisco = Cisco()


class Command(BaseCommand):
    help = 'Import ARP from pfSense'

    def add_arguments(self, parser):
        parser.add_argument('ip', nargs='+', type=str)

    def handle(self, *args, **options):
        r = requests.get('http://%s/arp_json.php' % options['ip'][0])
        arp = json.loads(r.text)
        for host in arp:
            obj, new = Arp.objects.get_or_create(ip=host['ip'], mac=host['mac'].replace(':',''))