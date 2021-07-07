from datetime import datetime

from django.db.utils import DataError
from easysnmp.exceptions import EasySNMPTimeoutError

from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.models import Interface, Switch, Vlan


def load_interfaces(switch, now=None):
    if not now:
        now = datetime.now()
    device = get_switch(switch)
    interfaces = device.interfaces_rfc()
    try:
        interface_vlan, tagged_vlans, untagged_vlan = device.vlan_ports()
    except ValueError as exception:
        print(exception)
        print('Using pvid')
        interface_vlan = device.vlan_ports_pvid()
        tagged_vlans = None
        untagged_vlan = None

    uptime = device.uptime()
    if not interfaces:
        raise ValueError('No interfaces found on switch')

    ports_rev = dict()
    if switch.type == 'Cisco':
        vlans = Vlan.objects.filter(on_switch=switch, vlan__gt=0)
        if not vlans:
            raise ValueError('No vlans on switch, run load_vlans')

        ports = device.bridgePort_to_ifIndex()

        for vlan in vlans:
            try:
                ports_temp = device.bridgePort_to_ifIndex(vlan=vlan.vlan)
                if not ports_temp:
                    print('No ports found in vlan %d' % vlan.vlan)
                    continue
                for bridge_port, if_index in ports_temp.items():
                    ports[bridge_port] = if_index
                    ports_rev[if_index] = bridge_port
            except EasySNMPTimeoutError:
                pass
    else:
        ports = device.bridgePort_to_ifIndex()
        for bridge_port, if_index in ports.items():
            ports_rev[if_index] = bridge_port

    if not ports:
        raise ValueError('bridgePort to ifIndex conversion table not found')

    cdp_multi = device.cdp_multi()

    poe_status = device.interface_poe_status()
    if poe_status and not switch.has_poe:
        switch.has_poe = True
        switch.save()

    if switch.type == 'Aruba':
        try:
            stack = device.stack_ports()
        except ValueError:
            stack = []
    else:
        stack = []

    # for bridge_port, if_index in ports.items():
    for if_index in interfaces['type'].keys():
        if if_index not in ports_rev:
            bridge_port = (str(int(if_index[-2:])))
        else:
            bridge_port = ports_rev[if_index]

        if if_index in interfaces['name']:
            name = interfaces['name'][if_index]
        elif if_index in interfaces['descr']:
            name = switch.shorten_interface_name(interfaces['descr'][if_index])
        else:
            name = ''

        # Interface naming for Westermo DSL modems
        if switch.type == 'Westermo':
            if interfaces['type'][if_index] == '6':
                name = '10/100TX Eth %s' % name
            elif interfaces['type'][if_index] == '169':
                name = 'SHDSL DSL %s' % name

        """
        117 is gigabitEthernet on HP
        169 is DSL
        """
        allowed_types = ['6', '117', '169', 'ethernetCsmacd', 'shdsl']

        if not interfaces['type'][if_index] in allowed_types:
            # print('Interface type %s' % interfaces['type'][if_index])
            continue
        if name == 'Fa0':
            continue

        interface, new = Interface.objects.get_or_create(
            switch=switch,
            index=if_index,
            defaults={'interface': name, 'type': interfaces['type'][if_index]}
        )

        if not new:
            if not interface.status == int(interfaces['status'][if_index]):
                interface.link_status_changed = datetime.now()
        if if_index in interfaces['alias']:
            interface.description = interfaces['alias'][if_index]

        if if_index in interfaces['high_speed']:
            interface.speed = interfaces['high_speed'][if_index]
        else:
            interface.speed = None
        # print(if_index)
        # print(interfaces['status'][if_index])
        interface.status = int(interfaces['status'][if_index])
        interface.admin_status = int(interfaces['admin_status'][if_index])
        interface.interface = name
        interface.type = interfaces['type'][if_index]

        if poe_status and bridge_port in poe_status:
            interface.poe_status = poe_status[bridge_port]
        else:
            interface.poe_status = None

        if switch.type == 'Westermo':
            neighbor = get_neighbors(int(ports_rev[if_index]), cdp_multi, switch)
        elif switch.type == 'HP':
            neighbor = get_neighbors(int(bridge_port), cdp_multi, switch)
        else:
            neighbor = get_neighbors(interface.index, cdp_multi, switch)

        if not neighbor and interface.neighbor:
                if interface.neighbor_set_by == switch:
                    print('Clearing neigbor %s from %s, set by %s'
                          % (interface.neighbor,
                             interface,
                             interface.neighbor_set_by))
                    interface.neighbor = None
                else:
                    print('Keeping neigbor %s on %s set by %s' %
                          (interface.neighbor,
                           interface,
                           interface.neighbor_set_by))

        elif isinstance(neighbor, Switch):
            interface.neighbor = neighbor
            interface.neighbor_set_by = switch
            # Interfaces with CDP or LDDP is a link,
            # skip loading of MAC addresses
            interface.skip_mac = True
        else:
            interface.neighbor_string = neighbor
            # Mitel IP Phones have lldp, but we want to load their MAC
            if neighbor in ['Mitel IP Phone']:
                interface.force_mac = True

        if not switch.type == 'Cisco' and not switch.type == 'CiscoSB' and not switch.type == 'Aruba':
            key = int(bridge_port)
        else:
            key = int(if_index)

        if key not in interface_vlan or not interface_vlan[key]:
            # print('%d not in interface_vlan' % key)
            interface.vlan = None
        else:
            vlan = interface_vlan[key]
            try:
                interface.vlan = Vlan.objects.get(vlan=vlan)
                interface.vlan.has_ports = True
                interface.vlan.save()
            except Vlan.DoesNotExist:
                print('Missing vlan %s, run load_vlans' % vlan)
        if tagged_vlans and key in tagged_vlans:

            for tagged_vlan in tagged_vlans[key]:
                try:
                    vlan = Vlan.objects.get(vlan=tagged_vlan)
                    interface.tagged_vlans.add(vlan)
                except Vlan.DoesNotExist:
                    print('Missing tagged vlan %s, run load_vlans' % tagged_vlan)
        if untagged_vlan and key in untagged_vlan:
            try:
                interface.vlan = Vlan.objects.get(vlan=untagged_vlan[key])
                interface.vlan.has_ports = True
                interface.vlan.save()
            except Vlan.DoesNotExist:
                print('Missing vlan %s, run load_vlans' % untagged_vlan[key])
        if interface.index in stack:
            print('Interface %s in stack' % interface)
            interface.neighbor_string = stack[interface.index]

        try:
            interface.save()
        except DataError as error:
            print(error)

        # if if_index in tagged_ports:
        #    for vlan in tagged_ports[if_index]:
        #        print('vlan %s is tagged on ifindex %s' % (vlan, if_index))
        #        # interface.tagged_vlans.add(vlan)

    del device.sessions[switch.ip]


def get_neighbors(index, cdp_multi, switch):
    if index in cdp_multi:
        for neighbor in cdp_multi[index].values():
            if 'ip' not in neighbor:
                neighbor['ip'] = None
            if 'device_id' not in neighbor:
                neighbor['device_id'] = None

            if neighbor['ip']:
                neighbor_switch = Switch.objects.filter(ip=neighbor['ip'])
            elif neighbor['device_id']:
                neighbor_switch = Switch.objects.filter(name=neighbor['device_id'].split('.')[0])
            else:
                return
            if neighbor_switch and len(neighbor_switch) > 0:
                neighbor_switch = neighbor_switch.first()
                print('%s is a valid neighbor' % neighbor_switch)

                remote_interface = neighbor['remote_port']
                # if neighbor_switch.type == 'Cisco':
                #    remote_interface = re.sub(r'([A-Z][a-z]).+?([0-9\/]+)', r'\1\2', remote_interface)
                # elif neighbor_switch.type == 'Extreme':
                #    remote_interface = re.sub(r'Slot:\s+([0-9]+), Port:\s([0-9]+)', r'\1:\2', remote_interface)
                remote_interface = neighbor_switch.shorten_interface_name(remote_interface)
                # Set neighbor on the remote interface in case the current switch does not broadcast
                # remote = Interface.objects.filter(switch=neighbor_switch, interface=remote_interface)
                try:
                    remote = Interface.objects.get(switch=neighbor_switch,
                                                   interface=remote_interface)
                    remote.neighbor = switch
                    remote.neighbor_set_by = switch
                    # Interfaces with CDP or LDDP is a link, skip loading of MAC addresses
                    # Set skip MAC on remote interface
                    remote.skip_mac = True
                    remote.save()
                except Interface.DoesNotExist:
                    print('No interface named %s on %s' % (remote_interface, neighbor_switch))
                return neighbor_switch  # Valid neighbor found
                # break  # Valid neighbor found, break loop
            else:
                print('Unknown neighbor: ' + (neighbor['ip'] or neighbor['device_id']))

        if neighbor['ip'] is None and neighbor['device_id'] == neighbor['platform']:
            return neighbor['device_id']
        return '%s\n%s\n%s' % (
            neighbor['device_id'],
            neighbor['ip'],
            neighbor['platform'])
    return None
