import json

import requests
from django.core.management.base import BaseCommand  # , CommandError

from switchinfo.models import Arp


class Command(BaseCommand):
    help = 'Import ARP from pfSense'

    def add_arguments(self, parser):
        parser.add_argument('ip', nargs='+', type=str)

    def handle(self, *args, **options):
        r = requests.get('http://%s/arp_json.php' % options['ip'][0])
        arp = json.loads(r.text)
        for host in arp:
            arp_db = Arp(mac=host['mac'].replace(':', ''), ip=host['ip'])
            arp_db.save()
