import requests
from django.core.management.base import BaseCommand

from switchinfo.models import Oui


class Command(BaseCommand):
    help = 'Import OUI'

    def handle(self, *args, **options):
        import re
        response = requests.get('http://standards-oui.ieee.org/oui.txt')

        pattern = r'([A-F0-9]{6})\s+\(.+\)\s+(.+)'
        matches = re.findall(pattern, response.text)

        for vendor in matches:
            Oui.objects.get_or_create(
                    prefix=vendor[0],
                    defaults={'vendor': vendor[1]},
                    )
