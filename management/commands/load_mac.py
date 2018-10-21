# from datetime import datetime
from pprint import pprint

from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone
from switchinfo.SwitchSNMP.utils import mac_string
from switchinfo.models import Interface, Switch, Vlan, Mac
from switchinfo.SwitchSNMP.select import get_switch
from datetime import datetime


class Command(BaseCommand):
    help = 'Import MAC-addresses from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()
        now = datetime.now()
        for switch in switches:
            print(switch)
            device = get_switch(switch)

            if not switch.type == 'Cisco':
                vlans = Vlan.objects.filter(vlan=0)
            else:
                vlans = Vlan.objects.filter(on_switch=switch, has_ports=True)
                if not vlans:
                    print('No vlans on switch ' + switch.name)
                    return False

            for vlan in vlans:
                for interface, macs in device.mac_on_port(vlan=vlan.vlan).items():
                    try:
                        interface_obj = Interface.objects.get(switch=switch, interface=interface)
                    except Interface.DoesNotExist as exception:
                        # print('Interface not found: ' + interface)
                        # print(exception)
                        continue
                    if not interface_obj.vlan:  # Do not find mac for trunk ports
                        continue
                    for mac in macs:
                        # print('mac: %s interface: %s' % (device.mac_string(mac), interface))
                        try:
                            mac, new = Mac.objects.get_or_create(mac=mac_string(mac),
                                                                 defaults={'interface': interface_obj,
                                                                           'last_seen': now})
                            if not new:
                                if not mac.interface == interface_obj:
                                    print('MAC %s moved from %s to %s' % (mac, mac.interface.switch_string(),
                                                                          interface_obj.switch_string()))
                                mac.interface = interface_obj
                                mac.last_seen = now
                                mac.save()
                        except Mac.MultipleObjectsReturned:
                            print('Multiple MAC')
                            print(Mac.objects.filter(mac=mac_string(mac)))

            bad_macs = Mac.objects.filter(interface__switch=switch).exclude(last_seen=now)
            bad_macs.delete()
            device.sessions[switch.ip] = None
            # pprint(bad_macs)
