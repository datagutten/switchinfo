import re

from django.core.management.base import BaseCommand

from switchinfo.models import Switch, SwitchGroup


class Command(BaseCommand):
    help = 'Build groups from switch names'

    def handle(self, *args, **options):
        devices = Switch.objects.all()
        for switch in devices:
            group = re.match(r'(\S+?)\-[A-Z0-9\-]+$', switch.name)
            if group:
                group = group.group(1)
                SwitchGroup.objects.get_or_create(grouping_key=group, defaults={'name': group})
