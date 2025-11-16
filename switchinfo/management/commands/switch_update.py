from django.conf import settings

import switchinfo.load_info.switch_info as switch_info
from snmp_compat import snmp_exceptions
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.management.commands import SwitchBaseCommand


class Command(SwitchBaseCommand):
    help = 'Update info about a switch'

    def handle(self, *args, **options):
        try:
            from config_backup.git import Git
            git = Git(settings.BACKUP_PATH)
        except ImportError:
            git = None

        for switch in self.handle_arguments(options):
            print(switch)
            try:
                device = get_switch(switch)
                switch_new = switch_info.switch_info(device=device)
                print(switch_new)
                if switch_new.name != switch.name and git:
                    git.move(switch.name, switch_new.name)

            except snmp_exceptions.SNMPError as e:
                print(switch, e)
                continue
