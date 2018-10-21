from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone

from switchinfo.models import Oui


from pprint import pprint

class Command(BaseCommand):
    help = 'Import OUI'

    def handle(self, *args, **options):
        import re
        from pprint import pprint
        file = open ('/home/switch_info/switchinfo/oui.txt', 'r')
        oui = file.read()

        pattern = '([A-F0-9]{6})\s+\(.+\)\s+(.+)'
        matches = re.findall(pattern, oui)

        for vendor in matches:
            #pprint (vendor[0])
            Oui.objects.get_or_create(
                    prefix=vendor[0],
                    defaults = {'vendor': vendor[1]},
                    )
            #break