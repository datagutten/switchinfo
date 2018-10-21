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

    def create_dict(self, ip=None, vlan=None, oid=None, int_value=False):
        if not oid:
            oid = False
        session = self.get_session(ip, vlan)
        if not session:
            return False
        indexes = dict()
        try:
            for object in session.walk(oid):
                index = utils.last_section(object.oid)
                if not index:
                    index = object.oid_index
                if int_value:
                    value = int(object.value)
                else:
                    value = object.value
                indexes[index] = value

            return indexes
        except easysnmp.exceptions.EasySNMPTimeoutError as exception:
            print(exception)
            return False

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

    def switch_info(self, ip=None):
        session = self.get_session(ip)
        info = dict()
        info['name'] = session.get('.1.3.6.1.2.1.1.5.0').value  # sysName.0
        info['descr'] = session.get('.1.3.6.1.2.1.1.1.0').value  # sysDescr.0
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

    # BRIDGE-MIB
    def mac_on_port(self, device=None, vlan=None):
        # https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/44800-mactoport44800.html
        # Step 2: Mac to bridge port number
        oid = '.1.3.6.1.2.1.17.4.3.1.1'
        macId_to_macAddress = self.create_dict(device, vlan, oid)

        # Step 3: bridge port number
        oid = '.1.3.6.1.2.1.17.4.3.1.2' # BRIDGE-MIB::dot1dTpFdbAddress
        macId_to_bridgePort = self.create_dict(device, vlan, oid)

        # Step 4: bridge port to ifIndex
        oid = '.1.3.6.1.2.1.17.1.4.1.2' # BRIDGE-MIB::dot1dBasePortIfIndex
        bridgePort_to_ifIndex = self.create_dict(device, vlan, oid)
        # pprint(bridgePort_to_ifIndex)
        # ifName to ifIndex
        oid = '.1.3.6.1.2.1.31.1.1.1.1'
        ifIndex_to_ifName = self.create_dict(device, vlan, oid)
        if not ifIndex_to_ifName:
            return
        ifName_to_macAddress = dict()
        for macId, macAddress in macId_to_macAddress.items():
            if macId not in macId_to_bridgePort:
                print('macId %s not in macId_to_bridgePort' % macId)
                continue
            bridgePort = macId_to_bridgePort[macId]
            if bridgePort not in bridgePort_to_ifIndex:
                continue

            ifIndex = bridgePort_to_ifIndex[bridgePort]
            ifName = ifIndex_to_ifName[ifIndex]
            if not ifName in ifName_to_macAddress:
                ifName_to_macAddress[ifName] = []
            ifName_to_macAddress[ifName].append(macAddress)

        return ifName_to_macAddress        

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
        oid = '.1.3.6.1.2.1.17.7.1.4.2.1.4'
        return self.create_dict(oid=oid)

    def untagged_ports(self):
        # Q-BRIDGE-MIB::dot1qVlanCurrentUntaggedPorts
        oid = '.1.3.6.1.2.1.17.7.1.4.2.1.5'
        return self.create_dict(oid=oid)

    def trunk_status(self, limit=None):
        # limit = 24
        # from pprint import pprint
        # If a port has egress vlan, but not untagged the port is a trunk port
        egress = self.egress_ports()
        if not egress:
            return False
        untagged = self.untagged_ports()
        # pprint(egress)
        trunk = dict()
        for vlan, ports in egress.items():
            # print('Vlan %s' % vlan)
            egress_ports = utils.parse_port_list(ports, limit)
            untagged_ports = utils.parse_port_list(untagged[vlan], limit)
            for index, port in egress_ports.items():
                # print('Vlan %s port %d untagged: %s' % (vlan, index, untagged_ports[index]))
                # print('Vlan %s port %d egress: %s' % (vlan, index, egress_ports[index]))
                # Port has egress, but not untagged
                if egress_ports[index] and not untagged_ports[index]:
                    trunk[index] = True

        # pprint(egress_ports)
        # pprint(untagged_ports)
        return trunk

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
