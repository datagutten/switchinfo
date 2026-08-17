import django.db.utils
import requests
from django.core.management.base import BaseCommand

from switchinfo.models import Oui


class Command(BaseCommand):
    help = 'Import OUI'

    def handle(self, *args, **options):
        import re
        response = requests.get('https://standards-oui.ieee.org/', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'})
        response.raise_for_status()

        pattern = r'([A-F0-9]{6})\s+\(.+\)\s+(.+)'
        matches = re.findall(pattern, response.text)

        for vendor in matches:
            try:
                Oui.objects.get_or_create(
                    prefix=vendor[0],
                    defaults={'vendor': vendor[1].strip()},
                )
            except django.db.utils.OperationalError:
                continue
