from abc import ABC

from django.core.management import BaseCommand

from switchinfo.models import Switch


class SwitchBaseCommand(BaseCommand, ABC):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='?', type=str)

    @staticmethod
    def handle_arguments(options):
        if not options['switch'] == 'all':
            return Switch.objects.filter(name__startswith=options['switch'])
        else:
            return Switch.objects.all()
