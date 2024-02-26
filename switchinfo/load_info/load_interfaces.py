from datetime import datetime

from django.db.models import Q
from django.db.utils import DataError
from switchinfo import SwitchSNMP

from switchinfo.SwitchSNMP.exceptions import SNMPError, SNMPNoData
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.models import Interface, Switch, Vlan, trunk_force_mac


def set_interface_vlan(interface, vlan_number: int, tagged=False):
    vlan_obj, created = Vlan.objects.get_or_create(vlan=vlan_number, defaults={'has_ports': not tagged})
    if created or interface.switch not in vlan_obj.on_switch.all():
        vlan_obj.on_switch.add(interface.switch)
    if created:
        print('Created missing vlan %d, run load_vlans to get name' % vlan_number)

    if not tagged:
        interface.vlan = vlan_obj
        if not vlan_obj.has_ports:
            vlan_obj.has_ports = True
            vlan_obj.save()
    else:
        interface.tagged_vlans.add(vlan_obj)


def load_aggregations(aggregations: dict, switch: Switch):
    for aggregation_index, members in aggregations.items():
        try:
            if type(aggregation_index) == int:
                parent_interface = Interface.objects.get(switch=switch, index=aggregation_index)
            else:
                parent_interface = Interface.objects.get(switch=switch, interface=aggregation_index)
        except Interface.DoesNotExist:
            print('Unable to find aggregation parent interface with index %d' % aggregation_index)
            return

        for member_id in members:
            try:
                if type(member_id) == int:
                    interface = Interface.objects.get(switch=switch, index=member_id)
                else:
                    interface = Interface.objects.get(switch=switch, interface=member_id)
                interface.aggregation = parent_interface
                interface.save()
            except Interface.DoesNotExist:
                print('Unable to find interface with index %d in aggregation %s' % member_id,
                      parent_interface)


def load_interfaces(switch: Switch, now=None):
    if not now:
        now = datetime.now()
    device = get_switch(switch)
    interfaces = device.interfaces_rfc()
    using_pvid = False
    try:
        if 'untagged' in interfaces:
            interface_vlan = None
            untagged_vlan = interfaces['untagged']
            tagged_vlans = interfaces['tagged']
        elif switch.type in ['Fortinet']:
            interface_vlan, tagged_vlans, untagged_vlan = device.vlan_ports(static=True,
                                                                            vlan_index=True)
        elif switch.type in ['Aruba CX']:
            interface_vlan, tagged_vlans, untagged_vlan = device.vlan_ports(static=False)
        else:
            interface_vlan, tagged_vlans, untagged_vlan = device.vlan_ports(static=True)

    except SNMPNoData as e:  # HP 1910
        if switch.type in ['Cisco', 'Aruba CX', 'Extreme']:
            raise e
        using_pvid = True
        print('Using Q-BRIDGE-MIB::dot1qPvid')
        try:
            interface_vlan = device.vlan_ports_pvid()
        except SNMPNoData:
            interface_vlan = None

        tagged_vlans = None
        untagged_vlan = None

    uptime = device.uptime()
    switch_vlans = list(switch.vlan.all().values_list(flat=True))

    """
    Key: Interface index
    Value: Bridge port
    """
    ports_rev = {}

    try:
        aggregations = device.aggregations()
    except SNMPError:
        aggregations = {}

    if switch.type == 'Cisco':
        try:
            ports = device.bridgePort_to_ifIndex()
        except SNMPError:
            ports = {}

        vlan_check = []
        for vlan in untagged_vlan.values():
            if vlan in vlan_check:
                continue
            vlan_check.append(vlan)
            try:
                try:
                    ports_temp = device.bridgePort_to_ifIndex(vlan=vlan)
                except SNMPNoData:
                    print('No ports found in vlan %d' % vlan)
                    continue
                for bridge_port, if_index in ports_temp.items():
                    ports[bridge_port] = if_index
                    ports_rev[if_index] = bridge_port
                device.close_sessions()
            except SNMPError:
                pass
    elif switch.type != 'Aruba CX REST API':
        try:
            ports = device.bridgePort_to_ifIndex()
            for bridge_port, if_index in ports.items():
                ports_rev[if_index] = bridge_port
        except SNMPNoData:
            ports = {}
            ports_rev = {}

    cdp_multi = device.cdp_multi()
    lldp = device.lldp()

    poe_interfaces = device.interface_poe()
    if poe_interfaces and not switch.has_poe:
        switch.has_poe = True
        switch.save()

    if switch.type == 'Aruba':
        try:
            stack = device.stack_ports()  # TODO: Correct type ArubaVSF
        except SNMPNoData:
            stack = []
    else:
        stack = []

    # for bridge_port, if_index in ports.items():
    for if_index in interfaces['type'].keys():
        if_index_int = int(if_index)
        if if_index in ports_rev.keys():
            bridge_port = ports_rev[if_index]
        elif len(str(if_index)) > 2:
            bridge_port = str(if_index)[-2:]
        else:
            bridge_port = None

        if bridge_port and switch.type not in ['Cisco', 'Cisco IOS XE', 'CiscoSB', 'Aruba', 'Aruba CX REST API']:
            key = int(bridge_port)
        else:
            key = int(if_index)

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
        if switch.type == 'Fortinet':
            allowed_types.append('54')

        if not interfaces['type'][if_index] in allowed_types and \
                int(if_index) not in aggregations.keys():
            # print('Interface %s type %s' % (if_index, interfaces['type'][if_index]))
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

        interface.poe_status = None

        if device.poe_absolute_index and bridge_port in poe_interfaces:
            interface.poe_status = poe_interfaces[bridge_port]['pethPsePortDetectionStatus']
        elif if_index_int in poe_interfaces:
            interface.poe_status = poe_interfaces[if_index_int]['pethPsePortDetectionStatus']
        elif not device.poe_absolute_index:
            normalized_port = SwitchSNMP.utils.normalize_interface(name)
            if normalized_port and normalized_port in poe_interfaces:
                interface.poe_status = poe_interfaces[normalized_port]['pethPsePortDetectionStatus']

        neighbor = None
        if lldp:  # LLDP on Cisco is indexed by bridge port
            if hasattr(device, 'lldp_key'):
                if device.lldp_key == 'interface_name':
                    neighbor = get_neighbors(interface.interface, lldp, switch)
            else:
                if switch.type in ['Cisco', 'Cisco IOS XE', 'Extreme', 'Westermo']:  # TODO: Handle bridge_port is none
                    neighbor = get_neighbors(int(bridge_port or 0), lldp, switch)
                elif switch.type == 'Aruba CX REST API' or type(device).__name__ == 'FortinetAPI':
                    neighbor = get_neighbors(interface.interface, lldp, switch)
                else:
                    neighbor = get_neighbors(interface.index, lldp, switch)
        else:
            neighbor = None

        if not neighbor and cdp_multi:  # Retry with CDP
            if switch.type == 'Westermo':
                neighbor = get_neighbors(int(ports_rev[if_index]), cdp_multi, switch)
            elif switch.type == 'HP' or switch.type == 'Comware':
                neighbor = get_neighbors(int(bridge_port), cdp_multi, switch)
            elif switch.type == 'Aruba CX REST API':
                neighbor = get_neighbors(interface.interface, cdp_multi, switch)
            else:  # CDP on Cisco is indexed by interface index
                neighbor = get_neighbors(interface.index, cdp_multi, switch)

        if not neighbor and interface.neighbor:
            if interface.neighbor_set_by == switch:
                print('Clearing neighbor %s from %s, set by %s'
                      % (interface.neighbor,
                         interface,
                         interface.neighbor_set_by))
                interface.neighbor = None
            else:
                print('Keeping neighbor %s on %s set by %s' %
                      (interface.neighbor,
                       interface,
                       interface.neighbor_set_by))

        if interface.neighbor_string and not neighbor:
            print('Clear neighbor string from %s' % interface)
            interface.neighbor_string = None

        elif isinstance(neighbor, Switch):
            interface.neighbor = neighbor
            interface.neighbor_set_by = switch
            # Interfaces with CDP or LLDP is a link,
            # skip loading of MAC addresses
            interface.skip_mac = True
        elif neighbor is not None:
            interface.neighbor_string = neighbor
            # Mitel IP Phones have lldp, but we want to load their MAC
            for line in neighbor.split('\n'):
                if line in trunk_force_mac:
                    interface.force_mac = True

        if interface_vlan:
            if key not in interface_vlan or not interface_vlan[key]:
                if key not in interface_vlan:
                    print('%d not in interface_vlan' % key)
                interface.vlan = None
            else:
                set_interface_vlan(interface, interface_vlan[key])

        if tagged_vlans and key in tagged_vlans:
            for tagged_vlan in tagged_vlans[key]:
                if tagged_vlan == 'all':
                    for vlan in switch.vlan.filter(vlan__gt=1):
                        interface.tagged_vlans.add(vlan)
                elif tagged_vlan in switch_vlans or not device.ignore_unknown_vlans:
                    set_interface_vlan(interface, tagged_vlan, True)

            # Remove tagged vlans from database when removed from switch
            vlan_obj: Vlan
            for vlan_obj in interface.tagged_vlans.all():
                if tagged_vlans[key] == ['all']:
                    if vlan_obj not in switch.vlan.all():  # vlan removed from switch
                        interface.tagged_vlans.remove(vlan_obj)
                else:
                    # vlan no longer tagged on port or not on switch
                    if vlan_obj.vlan not in tagged_vlans[key] or (
                            device.ignore_unknown_vlans and vlan_obj.vlan not in switch_vlans):
                        print('Remove tagged vlan %s from %s' % (vlan_obj, interface))
                        interface.tagged_vlans.remove(vlan_obj)
        else:
            interface.tagged_vlans.clear()

        if untagged_vlan and key in untagged_vlan:
            set_interface_vlan(interface, untagged_vlan[key])
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
    load_aggregations(aggregations, switch)
    try:
        del device.sessions[switch.ip]
    except KeyError:
        pass


def get_neighbors(index: int, cdp_multi: dict, switch: Switch):
    if index in cdp_multi and cdp_multi[index]:
        neighbor = None
        if type(cdp_multi[index]) == dict:
            cdp_multi[index] = list(cdp_multi[index].values())

        for neighbor in cdp_multi[index]:
            if neighbor == {}:
                print('Skip unknown neighbor on index %d' % index)
                neighbor = None
                continue

            for key in ['ip', 'device_id', 'platform']:
                if key not in neighbor:
                    neighbor[key] = None

            try:
                if 'device_id' in neighbor and neighbor['device_id']:
                    neighbor_switch = Switch.objects.get(
                        Q(ip=neighbor['ip']) |
                        Q(name=neighbor['device_id']) |
                        Q(name=neighbor['device_id'].split('.')[0])
                    )
                else:
                    neighbor_switch = Switch.objects.get(ip=neighbor['ip'])

            except Switch.DoesNotExist:
                for key in ['ip', 'device_id', 'platform']:
                    if key in neighbor:
                        print('Unknown neighbor: %s' % neighbor[key])
                        break
                continue
            except Switch.MultipleObjectsReturned:
                print('Multiple switches found with info ', neighbor['ip'], neighbor['device_id'])
                try:
                    neighbor_switch = Switch.objects.get(ip=neighbor['ip'])
                except Switch.DoesNotExist:
                    print('Unable to de-duplicate %s using IP %s' % (neighbor['device_id'], neighbor['ip']))
                    continue

            print('%s is a valid neighbor' % neighbor_switch)

            remote_interface_long = neighbor['remote_port']
            remote_interface_short = neighbor_switch.shorten_interface_name(remote_interface_long)
            # Set neighbor on the remote interface in case the current switch does not broadcast
            try:
                remote = Interface.objects.get(
                    Q(interface=remote_interface_short) |
                    Q(interface=remote_interface_long) |
                    Q(description=remote_interface_short),
                    switch=neighbor_switch
                )
                remote.neighbor = switch
                remote.neighbor_set_by = switch
                # Interfaces with CDP or LLDP is a link, skip loading of MAC addresses
                # Set skip MAC on remote interface
                remote.skip_mac = True
                remote.save()
            except Interface.DoesNotExist:
                print('No interface named %s on %s' % (remote_interface_short, neighbor_switch))
            except Interface.MultipleObjectsReturned:
                print('Multiple interfaces named %s on %s' % (remote_interface_short, neighbor_switch))
            return neighbor_switch  # Valid neighbor found

        # No valid neighbor found
        if neighbor and (neighbor['ip'] is None and neighbor['device_id'] == neighbor['platform']):
            return neighbor['device_id']
        elif neighbor:
            neighbor_string = ''
            for field in [neighbor['device_id'], neighbor['ip'], neighbor['platform']]:
                if field:
                    neighbor_string += field + '\n'
            return neighbor_string.strip()
    return None
