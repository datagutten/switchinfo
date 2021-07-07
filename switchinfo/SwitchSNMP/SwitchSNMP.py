import re

from django.core.exceptions import ImproperlyConfigured

from . import exceptions, utils

try:
    from django.conf import settings
    use_easysnmp = not settings.USE_NETSNMP
except (ImproperlyConfigured, AttributeError):
    use_easysnmp = False
    pass

if not use_easysnmp:
    from .NetSNMPCompat import NetSNMPCompat as SNMPSession
else:
    from .EasySNMPCompat import EasySNMPCompat as SNMPSession


class SwitchSNMP:

    sessions = dict()
    session = None
    device = None
    info_dicts = dict()
    community = None

    # TODO: Make arguments mandatory?
    def __init__(self, community: str = None, device: str = None):
        self.community = community
        self.device = device

    def __del__(self):
        self.sessions = None

    def get_session(self, device: str = None, vlan: int = None):
        if not vlan:
            vlan = 0
            community = self.community
        else:
            vlan = int(vlan)
            community = self.community + '@' + str(vlan)
        if not device:
            if not self.device:
                raise ValueError('No device specified')
            device = self.device
        if device not in self.sessions or self.sessions[device] is None:
            self.sessions[device] = dict()
        if vlan not in self.sessions[device]:
            # print('Creating session for %s vlan %s community %s' %
            #        (device, vlan, community))
            self.sessions[device][vlan] = SNMPSession(device, community)
        return self.sessions[device][vlan]

    def create_dict(self, ip=None, vlan=None, oid=None,
                    int_value=False, int_index=False,
                    value_translator: callable = None):
        if not oid:
            oid = False
        session = self.get_session(ip, vlan)
        if not session:
            return False
        indexes = dict()
        items = session.walk(oid)
        if not items:
            raise exceptions.SNMPNoData(session=session, oid=oid)
        for item in items:
            index = utils.last_section(item.oid)
            if not index:
                index = item.oid_index
            if value_translator:
                value = value_translator(item.value)
            elif int_value:
                value = int(item.value)
            else:
                value = item.value
            if int_index:
                index = int(index)
            indexes[index] = value

        return indexes

    def create_list(self, ip: str = None, vlan=None, oid=None):
        session = self.get_session(ip, vlan)
        values = []
        for item in session.walk(oid):
            value = item.value
            values.append(value)

        return values

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
        except exceptions.SNMPError as e:
            print(e)
            return
        try:
            # ENTITY-MIB::entPhysicalModelName
            model_strings = self.create_list(oid='.1.3.6.1.2.1.47.1.1.1.1.13')
            for model in model_strings:
                if not model.strip() == '':
                    info['model'] = model
                    break
            # info['model'] =\
            #    session.get('.1.3.6.1.2.1.47.1.1.1.1.13.1001').value
        except exceptions.SNMPNoData:
            info['model'] = ''
        try:
            info['location'] = session.get('1.3.6.1.2.1.1.6.0').value
        except exceptions.SNMPNoData:
            info['location'] = ''

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
        info['admin_status'] = \
            self.create_dict(oid='.1.3.6.1.2.1.2.2.1.7',
                             value_translator=utils.translate_status)
        # operStatus
        info['status'] = \
            self.create_dict(oid='.1.3.6.1.2.1.2.2.1.8',
                             value_translator=utils.translate_status)
        # EtherLike-MIB::dot3StatsDuplexStatus
        info['duplex'] = self.create_dict(oid='.1.3.6.1.2.1.10.7.2.1.19')
        return info

    # return value: bridgePort
    def mac_on_port(self, vlan=None):
        # TODO: Check if vlan exists on switch
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

    def bridgePort_to_ifIndex(self, vlan=None):
        oid = '.1.3.6.1.2.1.17.1.4.1.2'  # dot1dBasePortIfIndex
        info = dict()
        if vlan == 'all':
            for vlan in self.vlans():
                info_temp = self.create_dict(vlan=vlan, oid=oid)
                info.update(info_temp)
            return info
        else:
            return self.create_dict(vlan=vlan, oid=oid)

    # POWER-ETHERNET-MIB

    # Return key: bridgePort
    def interface_poe_status(self, device=None):
        oid = '.1.3.6.1.2.1.105.1.1.1.6'  # pethPsePortDetectionStatus
        try:
            bridge_port_poe = self.create_dict(device, oid=oid)
            if not bridge_port_poe:
                return None
        except exceptions.SNMPNoData:
            print('Switch has no PoE')
            return None

        states = dict()
        states['1'] = 'disabled'
        states['2'] = 'searching'
        states['3'] = 'deliveringPower'
        states['4'] = 'fault'
        states['5'] = 'test'
        states['6'] = 'otherFault'

        for bridge_port, poe_status in bridge_port_poe.items():
            bridge_port_poe[bridge_port] = states[poe_status]
        return bridge_port_poe

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
        tagged_vlans = dict()
        untagged_vlan = dict()

        for vlan, ports in egress.items():
            egress_ports = utils.parse_port_list(ports)
            # Is the port untagged in the current vlan
            is_untagged = utils.parse_port_list(untagged[vlan])

            for index, port in egress_ports.items():
                # Port has egress, but not untagged
                if index not in tagged_vlans:
                    tagged_vlans[index] = []

                # vlan is tagged
                if egress_ports[index] and not is_untagged[index]:
                    port_vlan[index] = None
                    tagged_vlans[index].append(vlan)
                # vlan in untagged
                elif egress_ports[index] and index not in port_vlan:
                    port_vlan[index] = vlan
                if is_untagged[index]:
                    untagged_vlan[index] = vlan
                # port has egress in multiple vlans, must be tagged
                elif egress_ports[index] and index in port_vlan:
                    port_vlan[index] = None

        return [port_vlan, tagged_vlans, untagged_vlan]

    def vlan_ports_pvid(self):
        # Q-BRIDGE-MIB::dot1qPvid
        oid = '.1.3.6.1.2.1.17.7.1.4.5.1.1'
        return self.create_dict(oid=oid, int_index=True)

    def vlans(self):
        # Q-BRIDGE-MIB::dot1qVlanFdbId
        oid = '.1.3.6.1.2.1.17.7.1.4.2.1.3'
        vlans = self.create_dict(oid=oid)

        vlan_list = []
        for vlan in vlans:
            vlan_list.append(int(vlan))
        return vlan_list

    # TODO: Rename to something including LLDP
    def cdp_multi(self):
        session = self.get_session()

        cdp = dict()
        cdp_high_index = False
        # CISCO-CDP-MIB::cdpCacheAddress
        oid = '.1.3.6.1.4.1.9.9.23.1.2.1.1'

        for item in session.walk(oid):
            match = re.match(r'.+\.([0-9]+)\.([0-9]+)', item.oid)
            if_index = int(match.group(1))  # cdpCacheIfIndex
            device_index = int(match.group(2))  # cdpCacheDeviceIndex
            if if_index > 10000:
                cdp_high_index = True

            if if_index not in cdp or not cdp[if_index]:
                cdp[if_index] = dict()
            if device_index not in cdp[if_index]:
                cdp[if_index][device_index] = dict()

            if item.oid.find('.9.9.23.1.2.1.1.4') >= 0:
                ip_temp = utils.ip_string(item.value)
                if not ip_temp == '0.0.0.0':
                    cdp[if_index][device_index]['ip'] = ip_temp
            #  cdpCacheDeviceId
            elif item.oid.find('.9.9.23.1.2.1.1.6') >= 0:
                cdp[if_index][device_index]['device_id'] = item.value
            elif item.oid.find('.9.9.23.1.2.1.1.8') >= 0:
                cdp[if_index][device_index]['platform'] = item.value
                # Aruba got a weird deviceId
                if item.value.find('Aruba') >= 0:
                    cdp[if_index][device_index]['device_id'] = None
            elif item.oid.find('.9.9.23.1.2.1.1.7') >= 0:
                cdp[if_index][device_index]['remote_port'] = item.value
            if not cdp[if_index][device_index]:
                cdp[if_index] = None

        oid = '.1.0.8802.1.1.2.1.4.1'

        for entry in session.walk(oid):
            match = re.match(r'.+\.([0-9]+)\.([0-9]+)', entry.oid)
            if_index = int(match.group(1))  # cdpCacheIfIndex

            if cdp_high_index and if_index < 10000:
                if_index = 10100 + if_index

            device_index = int(match.group(2))  # cdpCacheDeviceIndex
            if if_index not in cdp:
                cdp[if_index] = dict()
            if device_index not in cdp[if_index]:
                cdp[if_index][device_index] = dict()

            # if entry.oid.find('.0.8802.1.1.2.1.4.1.1.8') >= 0:
            #    cdp[if_index][device_index]['remote_port'] = entry.value
            utils.check_and_set(cdp[if_index][device_index], entry,
                                '.0.8802.1.1.2.1.4.1.1.8', 'remote_port')
            utils.check_and_set(cdp[if_index][device_index], entry,
                                '.0.8802.1.1.2.1.4.1.1.9', 'device_id')
            # if entry.oid.find('.0.8802.1.1.2.1.4.1.1.9') >= 0:
            #    cdp[if_index][device_index]['device_id'] = entry.value
            # elif entry.oid.find('.0.8802.1.1.2.1.4.1.1.10') >= 0:
            #    cdp[if_index][device_index]['platform'] = entry.value
            utils.check_and_set(cdp[if_index][device_index], entry,
                                '.0.8802.1.1.2.1.4.1.1.10', 'platform')

        return cdp

    def arp(self, device=None):
        oid = '.1.3.6.1.2.1.3.1.1.2'
        session = self.get_session()

        ip = []
        mac = []
        for item in session.walk(oid):

            ip_match = re.search(r'(?:[0-9]{1,3}\.?){4}$', item.oid)
            if ip_match:
                ip.append(ip_match.group(0))
                mac.append(utils.mac_string(item.value))
            else:
                print('No match: ' + item.oid)

        return dict(zip(mac, ip))
