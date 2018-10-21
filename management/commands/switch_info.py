# from datetime import datetime
from pprint import pprint

from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone

from switchinfo.models import Switch


from pprint import pprint
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Command(BaseCommand):
    help = 'Get info/add a switch'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        ip = options['switch'][0]
        community = options['switch'][1]
        device = SwitchSNMP(community=community)
        info = device.switch_info(ip)
        if not info:
            return
        switch, new = Switch.objects.get_or_create(ip=ip)

        pprint(info)
        switch.community = community
        if info['descr'].find('Cisco')==0:
            switch.type='Cisco'
        elif info['descr'].find('ExtremeXOS')==0:
            switch.type='Extreme'
        elif info['descr'].find('Aruba')==0:
            switch.type='Aruba'
        else:
            switch.type='Unknown'
        print(switch.type)
        switch.name = info['name'].split('.')[0]
        switch.save()
        
        pprint(switch)
