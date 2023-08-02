from datetime import datetime

from switchinfo.SwitchSNMP import exceptions
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.SwitchSNMP.utils import mac_string
from switchinfo.models import Interface, Mac, Switch, Vlan


def load_mac(switch: Switch, vlan=None):
    device = get_switch(switch)
    if switch.type not in ['Cisco', 'Aruba CX REST API']:
        vlans = [Vlan(vlan=0)]
    else:
        vlans = switch.vlan.filter(has_ports=True)
        if vlan:
            vlans.filter(vlan=vlan)
        if not vlans:
            print('No vlans on switch ' + switch.name)
            return
    now = datetime.now()
    mac_on_port = None
    for vlan in vlans:
        try:
            mac_on_port = device.mac_on_port(vlan=vlan.vlan or None,
                                             use_q_bridge_mib=switch.type == 'Comware')
            if not mac_on_port:
                print('No ports in vlan %s' % vlan)
                continue

            if switch.type == 'Cisco':  # Cisco needs one query for each vlan
                bridge_port_to_ifindex = device.bridgePort_to_ifIndex(vlan=vlan.vlan)
            elif switch.type == 'Westermo' or switch.type == 'Comware':
                bridge_port_to_ifindex = device.bridgePort_to_ifIndex()
            else:
                bridge_port_to_ifindex = None

        except exceptions.SNMPTimeout:
            print('Timeout connecting to %s vlan %s' % (switch, vlan))
            continue
        if not mac_on_port:
            print('No ports in vlan %s' % vlan)
            continue

        for mac, bridge_port in mac_on_port.items():

            if not bridge_port_to_ifindex:
                if_index = bridge_port
                if switch.type == 'Extreme':
                    if_index = str(int(if_index) + 1000)
            elif bridge_port not in bridge_port_to_ifindex:
                continue
            else:
                if_index = bridge_port_to_ifindex[bridge_port]

            try:
                if if_index.isnumeric():
                    interface_obj = Interface.objects.get(switch=switch, index=if_index)
                else:  # Interface name
                    interface_obj = Interface.objects.get(switch=switch, interface=if_index)
            except Interface.DoesNotExist:
                # print('Interface with index %s not found' % if_index)
                continue

            # Do not load mac for trunk ports
            if (interface_obj.is_trunk() and not interface_obj.force_mac) or interface_obj.skip_mac:
                # print('mac: %s trunk interface: %s %s' % (
                #     mac, interface_obj.switch, interface_obj))
                continue
            # print('mac: %s interface: %s' % (mac, interface))
            try:
                mac, new = Mac.objects.get_or_create(mac=mac,
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
            except exceptions.SNMPError as e:
                print(e)

    if mac_on_port:
        bad_macs = Mac.objects.filter(interface__switch=switch).exclude(last_seen=now)
        bad_macs.delete()
    device.sessions[switch.ip] = None
