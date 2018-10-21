# from datetime import datetime
from pprint import pprint

from django.core.management.base import BaseCommand  # , CommandError
# from django.utils import timezone
from django.db.utils import DataError

from switchinfo.models import Interface, Switch, Vlan
from switchinfo.SwitchSNMP.select import get_switch
from datetime import datetime

from pprint import pprint
import re


class Command(BaseCommand):
    help = 'Import ports from switches'

    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **options):
        if not options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=options['switch'][0])
        else:
            switches = Switch.objects.all()

        for switch in switches:
            print(switch.name)
            device = get_switch(switch)
            # print(device.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.15'))

            # return
            interfaces = device.interfaces_rfc()
            trunk_status = device.trunk_status()
            uptime = device.uptime()
            if not interfaces:
                print('No interfaces')
                continue
            if switch.type == 'Cisco':
                vlans = Vlan.objects.filter(on_switch=switch, vlan__gt=0)
                if not vlans:
                    print('No vlans found, run load_vlans')
                    continue

                ports = dict()
                for vlan in vlans:
                    ports_temp = device.bridgePort_to_ifIndex(vlan=vlan.vlan)
                    if not ports_temp:
                        print('No ports found in vlan %d' % vlan.vlan)
                        continue
                    for bridge_port, if_index in ports_temp.items():
                        ports[bridge_port] = if_index
            else:
                ports = device.bridgePort_to_ifIndex()

            if not ports:
                print('No ports')
                continue
            # cdp = device.cdp()
            # pprint(cdp)
            # print('Trunk status')
            # pprint(trunk_status)
            cdp_multi = device.cdp_multi()
            port_vlan = device.port_vlan()

            poe_status = device.interface_poe_status()
            if poe_status and not switch.has_poe:
                switch.has_poe = True
                switch.save()

            for bridge_port, if_index in ports.items():
                name = interfaces['name'][if_index]
                # 117 is gigabitEthernet on HP
                if not interfaces['type'][if_index] == '6' and not interfaces['type'][if_index] == '117':
                    print('Interface type %s' % interfaces['type'][if_index])
                    continue
                if name == 'Fa0':
                    continue

                interface, new = Interface.objects.get_or_create(
                    switch=switch,
                    index=if_index,
                    interface=interfaces['name'][if_index],
                    )
                if not new:
                    if not interface.status == int(interfaces['status'][if_index]):
                        interface.link_status_changed = datetime.now()
                interface.description = interfaces['alias'][if_index]
                # interface.last_change = int(uptime) - int(interfaces['last_change'][if_index])

                if if_index in interfaces['high_speed']:
                    interface.speed = interfaces['high_speed'][if_index]
                else:
                    interface.speed = None
                interface.status = int(interfaces['status'][if_index])
                #interface.status
                interface.admin_status = interfaces['admin_status'][if_index]
                # print('ifindex: %s' % ifindex)
                # print(bridge_port)
                if poe_status and bridge_port in poe_status:
                    interface.poe_status = poe_status[bridge_port]
                else:
                    interface.poe_status = None

                if if_index in cdp_multi:
                    for neighbor in cdp_multi[if_index].values():

                        interface.neighbor_string = "%s\n%s\n%s" % (
                            neighbor['device_id'],
                            neighbor['ip'],
                            neighbor['platform'])
                        if neighbor['ip']:
                            neighbor_switch = Switch.objects.filter(ip=neighbor['ip'])
                            if len(neighbor_switch) > 0:
                                neighbor_switch = neighbor_switch.first()
                                print('%s is a valid neighbor' % neighbor_switch)
                                interface.neighbor = neighbor_switch
                                remote_interface = neighbor['remote_port']
                                if interface.neighbor.type == 'Cisco':
                                    remote_interface = re.sub(r'([A-Z][a-z]).+?([0-9\/]+)', r'\1\2', remote_interface)
                                elif interface.neighbor.type == 'Extreme':
                                    remote_interface = re.sub(r'Slot:\s+([0-9]+), Port:\s([0-9]+)', r'\1:\2', remote_interface)
                                # Set neighbor on the remote interface in case the current switch does not broadcast
                                remote = Interface.objects.filter(switch=interface.neighbor, interface=remote_interface)
                                if len(remote) > 0:
                                    remote = remote.first()
                                    remote.neighbor = switch
                                    remote.save()
                                else:
                                    print('No interface named %s on %s' % (remote_interface, interface.neighbor))

                                break  # Valid neighbor found, break loop
                            else:
                                print('Unknown neighbor: %s' % neighbor['ip'])
                                interface.neighbor = None
                                continue

                try:
                    if not switch.type == 'Cisco':
                        vlan = port_vlan[bridge_port]
                    elif if_index in port_vlan:
                        vlan = port_vlan[if_index]
                    else:
                        # print('ifindex %s not in port_vlan' % ifindex)
                        vlan = None
                        # continue
                    if trunk_status and (int(if_index) in trunk_status or int(bridge_port) in trunk_status):
                        # print('ifindex %s is trunk' % ifindex)
                        vlan = None
                    if vlan:
                        interface.vlan = Vlan.objects.get(vlan=vlan)
                        interface.vlan.has_ports = True
                        interface.vlan.save()
                    else:
                        interface.vlan = None
                except Vlan.DoesNotExist:
                    print('Missing vlan ' + vlan)
                try:
                    interface.save()
                except DataError as error:
                    print(error)

                device.sessions[switch.ip] = None
