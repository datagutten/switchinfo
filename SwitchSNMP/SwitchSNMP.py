import re

# from easysnmp import Session
import easysnmp

# from switchinfo.SwitchSNMP.utils import last_section
import switchinfo.SwitchSNMP.utils as utils
from switchinfo.SwitchSNMP.utils import mac_string, ip_string

Session = easysnmp.Session


class SwitchSNMP():

    sessions = dict()
    session = None
    device = None
    info_dicts = dict()
    community = None

    def __init__(self, community=None, device=None):
        self.community = community
        self.device = device

    def get_session(self, device=None, vlan=None):
        if not vlan:
            vlan = 0
            community = self.community
        else:
            vlan = int(vlan)
            community = self.community + '@' + str(vlan)
        if not device:
            device = self.device
        if device not in self.sessions:
            self.sessions[device] = dict()
        if vlan not in self.sessions[device]:
            # print('Creating session for %s vlan %s community %s' %
            #        (device, vlan, community))
            try:
                self.sessions[device][vlan] = Session(
                    hostname=device,
                    community=community,
                    version=2,
                    abort_on_nonexistent=True,)
            except easysnmp.exceptions.EasySNMPConnectionError as exception:
                print('Unable to open session with %s vlan %s: %s' % (device, vlan, exception))
                return
            except easysnmp.exceptions.EasySNMPTimeoutError as exception:
                print('Timeout connecting to %s: %s' % (device, exception))
        return self.sessions[device][vlan]

    def create_dict(self, ip=None, vlan=None, oid=None,
                    int_value=False, int_index=False):
        if not oid:
            oid = False
        session = self.get_session(ip, vlan)
        if not session:
            return False
        indexes = dict()

        for item in session.walk(oid):
            index = utils.last_section(item.oid)
            if not index:
                index = item.oid_index
            if int_value:
                value = int(item.value)
            else:
                value = item.value
            if int_index:
                index = int(index)
            indexes[index] = value

        return indexes

    def create_list(self, ip, vlan=None, oid=False):
        session = self.get_session(ip, vlan)
        values = []
        for object in session.walk(oid):
            value = object.value
            values.append(value)

        return values

    # Return key: interfaceIndex
    def interface_alias(self, device=None):
        oid = '.1.3.6.1.2.1.31.1.1.1.18'  # IF-MIB::ifAlias
        if_alias = self.create_dict(device, oid=oid)
        return if_alias

    # Load core information about a switch
    def switch_info(self, ip=None):
        session = self.get_session(ip)
        if not session:
            return
        info = dict()
        try:
            # SNMPv2-MIB::sysName
            info['name'] = session.get('.1.3.6.1.2.1.1.5.0').value
            # SNMPv2-MIB::sysDescr
            info['descr'] = session.get('.1.3.6.1.2.1.1.1.0').value
            # SNMPv2-MIB::sysObjectID
            info['objectID'] = session.get('.1.3.6.1.2.1.1.2.0').value
            # ENTITY-MIB::entPhysicalModelName
            info['model'] =\
                session.get('.1.3.6.1.2.1.47.1.1.1.1.13.1001').value
        except easysnmp.exceptions.EasySNMPNoSuchInstanceError:
            info['model'] = ''
        except easysnmp.exceptions.EasySNMPTimeoutError as exception:
            print('Timeout connecting to %s: %s' % (ip, exception))
            return
        except easysnmp.exceptions.EasySNMPNoSuchObjectError as exception:
            print('Error device %s: %s' % (ip, exception))
        return info

    def uptime(self):
        session = self.get_session()
        return session.get('.1.3.6.1.2.1.1.3.0').value

    def interfaces_rfc(self):
        info = dict()
        # IF-MIB::ifName
        info['name'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.1')
        # IF-MIB::ifAlias
        info['alias'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.18')
        # RFC1213-MIB::ifdescr
        info['descr'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.2')
        # RFC1213-MIB::ifType
        info['type'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.3')
        # ifLastChange
        info['last_change'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.9')
        # ifSpeed
        # info['speed'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.5')
        # ifHighSpeed
        info['high_speed'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.15')
        # adminStatus
        info['admin_status'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.7')
        # operStatus
        info['status'] = self.create_dict(oid='.1.3.6.1.2.1.2.2.1.8', int_value=True)
        # EtherLike-MIB::dot3StatsDuplexStatus
        info['duplex'] = self.create_dict(oid='.1.3.6.1.2.1.10.7.2.1.19')
        return info

    # return value: bridgePort
    def mac_on_port(self, vlan=None):
        session = self.get_session(vlan=vlan)
        oid = '.1.3.6.1.2.1.17.4.3.1.2'  # BRIDGE-MIB::dot1dTpFdbPort
        port = dict()
        for entry in session.walk(oid):
            matches = re.match(r'(?:mib-2|iso\.3\.6\.1\.2\.1)\.17\.4\.3\.1\.([0-9])\.([0-9\.]+)', entry.oid)
            if not matches:
                print('oid %s not parsed' % entry.oid)
                continue
            mac = utils.mac_parse_oid(matches.group(2))
            if not len(mac) == 12:
                print('Invalid MAC %s' % mac)
                continue
            port[mac] = entry.value
        return port

    def ifIndex_to_ifName(self, device=None, vlan=None):
        oid = '.1.3.6.1.2.1.31.1.1.1.1'  # ifName
        return self.create_dict(device, vlan, oid)

    def bridgePort_to_ifIndex(self, device=None, vlan=None):
        oid = '.1.3.6.1.2.1.17.1.4.1.2'  # dot1dBasePortIfIndex
        info = dict()
        if vlan == 'all':
            for vlan in self.vlans(device):
                info_temp = self.create_dict(device, vlan, oid)
                info.update(info_temp)
            return info
        else:
            return self.create_dict(device, vlan, oid)

    # POWER-ETHERNET-MIB

    # Return key: bridgePort
    def interface_poe_status(self, device=None):
        oid = '.1.3.6.1.2.1.105.1.1.1.6'  # pethPsePortDetectionStatus
        bridge_port_poe = self.create_dict(device, oid=oid)
        if not bridge_port_poe:
            return None
        states = dict()
        states['1'] = 'disabled'
        states['2'] = 'searching'
        states['3'] = 'deliveringPower'

        for bridge_port, poe_status in bridge_port_poe.items():
            bridge_port_poe[bridge_port] = states[poe_status]
        return bridge_port_poe

    def port_vlan(self, device=None):
        # Q-BRIDGE-MIB::dot1qPvid
        oid = '.1.3.6.1.2.1.17.7.1.4.5.1.1'
        return self.create_dict(device, oid=oid)

    def vlan_names(self):
        # Q-BRIDGE-MIB::dot1qVlanStaticName
        oid = '.1.3.6.1.2.1.17.7.1.4.3.1.1'
        return self.create_dict(oid=oid)

    def egress_ports(self):
        # Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts
        values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.2.1.4')
        if not values:
            # Q-BRIDGE-MIB::dot1qVlanStaticEgressPorts
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.3.1.2')
        return values

    def untagged_ports(self):
        # Q-BRIDGE-MIB::dot1qVlanCurrentUntaggedPorts
        values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.2.1.5')
        if not values:
            # Q-BRIDGE-MIB::dot1qVlanStaticEgressPorts
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.3.1.2')
        return values

    # Return vlan number or None if the interface is trunk
    def vlan_ports(self):
        # If a port has egress vlan, but not untagged, the port is a trunk port
        # If a port has egress multiple vlans, the port is a trunk port
        egress = self.egress_ports()
        untagged = self.untagged_ports()

        port_vlan = dict()
        tagged_ports = dict()

        for vlan, ports in egress.items():
            egress_ports = utils.parse_port_list(ports)
            untagged_ports = utils.parse_port_list(untagged[vlan])

            for index, port in egress_ports.items():
                # Port has egress, but not untagged
                tagged_ports[index] = []
                # vlan is tagged
                if egress_ports[index] and not untagged_ports[index]:
                    port_vlan[index] = None
                    tagged_ports[index].append(vlan)
                # vlan in untagged
                elif egress_ports[index] and index not in port_vlan:
                    port_vlan[index] = vlan
                # port has egress in multiple vlans, must be tagged
                elif egress_ports[index] and index in port_vlan:
                    port_vlan[index] = None

        return port_vlan

    def vlan_ports_pvid(self, device=None):
        # Q-BRIDGE-MIB::dot1qPvid
        oid = '.1.3.6.1.2.1.17.7.1.4.5.1.1'
        return self.create_dict(device, oid=oid, int_index=True)

    def vlans(self, device=None):
        # Q-BRIDGE-MIB::dot1qVlanFdbId
        oid = '.1.3.6.1.2.1.17.7.1.4.2.1.3'
        vlans = self.create_dict(device, oid=oid)

        vlan_list = []
        for vlan in vlans:
            if int(vlan) < 1000:
                vlan_list.append(int(vlan))
        return vlan_list

    def cdp(self):
        # CISCO-CDP-MIB::cdpCacheAddress
        oid = '.1.3.6.1.4.1.9.9.23.1.2.1.1'
        # return self.create_dict(oid=oid)
        session = self.get_session()
        if not session:
            return False
        platform = dict()
        ip = dict()
        device_id = dict()
        remote_port = dict()

        for object in session.walk(oid):
            match = re.match(r'.+\.([0-9]+)\.[0-9]+', object.oid)
            index = match.group(1)

            if object.oid.find('.9.9.23.1.2.1.1.4') >= 0:
                ip_temp = utils.ip_string(object.value)
                if not ip_temp == '0.0.0.0':
                    ip[index] = ip_temp
            #  cdpCacheDeviceId
            elif object.oid.find('.9.9.23.1.2.1.1.6') >= 0:
                device_id[index] = object.value
            elif object.oid.find('.9.9.23.1.2.1.1.8') >= 0:
                platform[index] = object.value
                # Aruba got a weird deviceId
                if object.value.find('Aruba') >= 0:
                    device_id[index] = None
            elif object.oid.find('.9.9.23.1.2.1.1.7') >= 0 and index not in remote_port:
                remote_port[index] = object.value

        return [ip, platform, device_id, remote_port]

    def cdp_multi(self):

        session = self.get_session()
        if not session:
            return False

        cdp = dict()
        # CISCO-CDP-MIB::cdpCacheAddress
        oid = '.1.3.6.1.4.1.9.9.23.1.2.1.1'
        for object in session.walk(oid):
            match = re.match(r'.+\.([0-9]+)\.([0-9]+)', object.oid)
            if_index = match.group(1)  # cdpCacheIfIndex
            device_index = match.group(2)  # cdpCacheDeviceIndex
            if if_index not in cdp:
                cdp[if_index] = dict()
            if device_index not in cdp[if_index]:
                cdp[if_index][device_index] = dict()

            if object.oid.find('.9.9.23.1.2.1.1.4') >= 0:
                ip_temp = utils.ip_string(object.value)
                if not ip_temp == '0.0.0.0':
                    cdp[if_index][device_index]['ip'] = ip_temp
            #  cdpCacheDeviceId
            elif object.oid.find('.9.9.23.1.2.1.1.6') >= 0:
                cdp[if_index][device_index]['device_id'] = object.value
            elif object.oid.find('.9.9.23.1.2.1.1.8') >= 0:
                cdp[if_index][device_index]['platform'] = object.value
                # Aruba got a weird deviceId
                if object.value.find('Aruba') >= 0:
                    cdp[if_index][device_index]['device_id'] = None
            elif object.oid.find('.9.9.23.1.2.1.1.7') >= 0:
                cdp[if_index][device_index]['remote_port'] = object.value

        return cdp

    def arp(self, device=None):
        oid = '.1.3.6.1.2.1.3.1.1.2'
        session = self.get_session()

        ip = []
        mac = []
        for object in session.walk(oid):

            ip_match = re.search('(?:[0-9]{1,3}\.?){4}$', object.oid)
            if ip_match:
                ip.append(ip_match.group(0))
                mac.append(mac_string(object.value))
            else:
                print('No match: ' + object.oid)

        return dict(zip(mac, ip))
