import datetime
import os
import re

from . import exceptions, mibs, utils


def select_library(library):
    if library == 'netsnmp':
        from .NetSNMPCompat import NetSNMPCompat
        return NetSNMPCompat
    elif library == 'easysnmp':
        from .EasySNMPCompat import EasySNMPCompat
        return EasySNMPCompat
    elif library == 'pynetsnmp':
        from .pynetsnmpCompat import PynetsnmpCompat
        return PynetsnmpCompat
    else:
        raise ValueError('Invalid SNMP library "%s"' % library)


class SwitchSNMP:
    switch = None
    sessions = dict()
    session = None
    device = None
    info_dicts = dict()
    community = None
    timeout = 0.5
    snmp_library = None
    ignore_unknown_vlans = False
    """Should tagged vlans not defined on switch be ignored?"""
    poe_absolute_index = True
    """
    POWER-ETHERNET-MIB
    Is pethPsePortIndex in pethPsePortTable absolute for all ports in the stack or relative to the stack member?
    """
    arp_oid = 'atPhysAddress'
    """
    Field in RFC1213-MIB to use for ARP fetching
    """

    # TODO: Make arguments mandatory?
    def __init__(self, community: str = None, device: str = None, switch=None, snmp_library=None):
        self.community = community
        self.device = device
        self.switch = switch
        if snmp_library:
            self.snmp_library = select_library(snmp_library)
        else:
            self.snmp_library = select_library(os.environ.get('SNMP_LIBRARY') or 'netsnmp')

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
            self.sessions[device][vlan] = self.snmp_library(device, community, timeout=self.timeout)
        return self.sessions[device][vlan]

    def close_sessions(self):
        for vlan, session in self.sessions[self.device].items():
            session.close()
        del self.sessions[self.device]

    def walk_keys(self, oid: str, keys: list):
        session = self.get_session()
        if oid[-1] != '.':
            oid = oid + '.'
        values = {}
        for key in keys:
            try:
                alias = session.get(oid + key)
                values[key] = alias.value
            except exceptions.SNMPNoData:
                values[key] = None
        return values

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

        # SNMPv2-MIB::sysName
        info['name'] = session.get('.1.3.6.1.2.1.1.5.0').value
        # SNMPv2-MIB::sysDescr
        info['descr'] = session.get('.1.3.6.1.2.1.1.1.0').value
        # SNMPv2-MIB::sysObjectID
        info['objectID'] = session.get('.1.3.6.1.2.1.1.2.0').value

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
            location = session.get('1.3.6.1.2.1.1.6.0').value
            info['location'] = location.encode('iso-8859-1').decode('utf8')
        except exceptions.SNMPNoData:
            info['location'] = ''

        return info

    def uptime(self) -> datetime.timedelta:
        session = self.get_session()
        return session.get('.1.3.6.1.2.1.1.3.0').typed_value()

    def interface_table(self) -> dict:
        """
        IF-MIB::ifXTable
        :return:
        """
        return self.snmp_table('.1.3.6.1.2.1.31.1.1', {
            1: 'ifName',
            2: 'ifInMulticastPkts',
            3: 'ifInBroadcastPkts',
            4: 'ifOutMulticastPkts',
            5: 'ifOutBroadcastPkts',
            6: 'ifHCInOctets',
            7: 'ifHCInUcastPkts',
            8: 'ifHCInMulticastPkts',
            9: 'ifHCInBroadcastPkts',
            10: 'ifHCOutOctets',
            11: 'ifHCOutUcastPkts',
            12: 'ifHCOutMulticastPkts',
            13: 'ifHCOutBroadcastPkts',
            14: 'ifLinkUpDownTrapEnable',
            15: 'ifHighSpeed',
            16: 'ifPromiscuousMode',
            17: 'ifConnectorPresent',
            18: 'ifAlias',
            19: 'ifCounterDiscontinuityTime',
        })

    def interfaces_rfc(self):
        info = dict()
        # IF-MIB::ifName
        info['name'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.1')
        keys = list(info['name'].keys())
        # IF-MIB::ifAlias
        info['alias'] = self.walk_keys(oid='.1.3.6.1.2.1.31.1.1.1.18', keys=keys)
        # RFC1213-MIB::ifdescr
        info['descr'] = self.walk_keys(oid='.1.3.6.1.2.1.2.2.1.2', keys=keys)
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
        try:
            info['duplex'] = self.create_dict(oid='.1.3.6.1.2.1.10.7.2.1.19')
        except exceptions.SNMPNoData:
            info['duplex'] = {}

        return info

    # return value: bridgePort
    def mac_on_port(self, vlan=None, use_q_bridge_mib=None):
        # TODO: Check if vlan exists on switch
        session = self.get_session(vlan=vlan)
        oid_q_bridge = '.1.3.6.1.2.1.17.7.1.2.2.1.2'  # Q-BRIDGE-MIB::dot1qTpFdbPort
        oid_bridge = '.1.3.6.1.2.1.17.4.3.1.2'  # BRIDGE-MIB::dot1dTpFdbPort

        port = dict()
        if use_q_bridge_mib:
            macs = session.walk(oid_q_bridge)
        else:
            macs = session.walk(oid_bridge)
            if not macs:
                macs = session.walk(oid_q_bridge)

        for entry in macs:
            matches = re.match(r'.+\.([0-9]+)\.((?:[0-9]+\.){5}[0-9]+)$', entry.oid)
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
            try:
                return self.create_dict(vlan=vlan, oid=oid)
            except exceptions.SNMPError as e:
                if not vlan:
                    vlan = 0
                e.message = 'Unable to get bridgePort to ' \
                            'ifIndex conversion table for vlan %d' % vlan
                raise e

    @staticmethod
    def module_to_ifindex(module, index):
        return index

    def interface_poe(self):
        """
        POWER-ETHERNET-MIB::PethPsePortEntry
        Return key: bridgePort
        """
        if self.poe_absolute_index:
            keys = ['pethPsePortIndex']
        else:
            keys = ['pethPsePortGroupIndex', 'pethPsePortIndex']

        ports = self.build_dict_multikeys(
            '.1.3.6.1.2.1.105.1.1.1',
            keys,
            {
                1: 'pethPsePortGroupIndex',
                2: 'pethPsePortIndex',
                3: 'pethPsePortAdminEnable',
                4: 'pethPsePortPowerPairsControlAbility',
                5: 'pethPsePortPowerPairs',
                6: 'pethPsePortDetectionStatus',
                7: 'pethPsePortPowerPriority',
                8: 'pethPsePortMPSAbsentCounter',
                9: 'pethPsePortType',
                10: 'pethPsePortPowerClassifications',
                11: 'pethPsePortInvalidSignatureCounter',
                12: 'pethPsePortPowerDeniedCounter',
                13: 'pethPsePortOverLoadCounter',
                14: 'pethPsePortShortCounter',
            })
        states = {
            0: 'disabled',  # Extreme use 0 for disabled
            1: 'disabled',
            2: 'searching',
            3: 'deliveringPower',
            4: 'fault',
            5: 'test',
            6: 'otherFault'
        }
        for key, value in ports.items():
            # noinspection PyTypeChecker
            ports[key]['pethPsePortDetectionStatus'] = states[value['pethPsePortDetectionStatus']]

        return ports

    def vlan_names(self):
        # Q-BRIDGE-MIB::dot1qVlanStaticName
        oid = '.1.3.6.1.2.1.17.7.1.4.3.1.1'
        try:
            return self.create_dict(oid=oid, int_index=True)
        except exceptions.SNMPError as e:
            e.message = 'Unable to get VLAN names'
            raise e

    def egress_ports(self, static=False):
        values = None
        # Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts
        if not static:
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.2.1.4', int_index=True)
        if not values:
            # Q-BRIDGE-MIB::dot1qVlanStaticEgressPorts
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.3.1.2', int_index=True)
        return values

    def untagged_ports(self, static=False):
        values = None
        # Q-BRIDGE-MIB::dot1qVlanCurrentUntaggedPorts
        if not static:
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.2.1.5', int_index=True)
        if not values:
            # Q-BRIDGE-MIB::dot1qVlanStaticUntaggedPorts
            values = self.create_dict(oid='.1.3.6.1.2.1.17.7.1.4.3.1.4', int_index=True)
        return values

    # Return vlan number or None if the interface is trunk
    def vlan_ports(self, static=False, vlan_index=False):
        # If a port has egress vlan, but not untagged, the port is a trunk port
        # If a port has egress multiple vlans, the port is a trunk port
        egress = self.egress_ports(static)
        untagged = self.untagged_ports(static)
        port_vlan = dict()
        tagged_vlans = dict()
        untagged_vlan = dict()
        if vlan_index:
            q_bridge = mibs.qBridgeMIB(self)
            index_table = q_bridge.dot1qVlanIndex()
        else:
            index_table = {}

        for vlan_key, ports in egress.items():
            if vlan_key in index_table.keys():
                vlan = index_table[vlan_key]
            else:
                vlan = vlan_key

            egress_ports = utils.parse_port_list(ports)
            # Is the port untagged in the current vlan
            is_untagged = utils.parse_port_list(untagged[vlan_key])

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

    def vlan_ports_static(self):
        return self.vlan_ports(static=True)

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

    def build_dict(self, oid, key_names: list, fields, key=None, session=None):
        """

        :param oid: Base OID to walk
        :param key_names: Key fields appended to the oid
        :param fields: Field names
        :param key: Key field to use as key for a returned dict
        :param session:
        """
        if not session:
            session = self.get_session()

        if not key:
            if len(key_names) == 1:
                key = key_names[0]
            else:
                raise NotImplementedError()

        items = {}

        for item in session.walk(oid):
            key_pos = len('iso' + oid[2:])
            matches = re.match(r'\.([0-9]+)\.(.+)', item.oid[key_pos:])
            field = int(matches.group(1))
            sub_key = matches.group(2).split('.')
            keys = dict(zip(key_names, sub_key))

            if not key:
                raise NotImplementedError()
            if keys[key] not in items:
                items[keys[key]] = {}

            items[keys[key]][fields[field]] = item.value

        return items

    def build_dict_multikeys(self, oid, key_names: list, fields, key=None, session=None):
        """

        :param oid: Base OID to walk
        :param key_names: Key fields appended to the oid
        :param fields: Field names
        :param key: Key field to use as key for a returned dict
        :param session:
        """
        if not session:
            session = self.get_session()

        if not key:
            if len(key_names) == 1:
                key = key_names[0]
                join_keys = False
            else:
                join_keys = True
        else:
            join_keys = False

        items = {}

        for item in session.walk(oid):
            # print('%s=%s' % (item.oid, item.value))
            # continue
            keys = {}

            key_pos = len('iso' + oid[2:])
            # print('Keys', item.oid[key_pos:])
            matches = re.match(r'\.([0-9]+)\.(.+)', item.oid[key_pos:])
            # print(item.oid[key_pos:])
            key_values = item.oid[key_pos + 1:].split('.')
            key_values = list(map(int, key_values))

            if key_values[0] not in fields.keys():
                raise IndexError('No name for key %d' % key_values[0])
            column = fields[key_values[0]]

            key_num = 0
            for sub_key in key_values[1:]:
                # sub_key = int(sub_key)
                if key_num < len(key_names):
                    keys[key_names[key_num]] = sub_key
                else:
                    if key_num == len(key_names):
                        keys[key_names[-1]] = sub_key
                    else:
                        keys[key_names[-1]] = '%s.%d' % (str(keys[key_names[-1]]), sub_key)
                key_num += 1

            if join_keys:
                key = '.'.join(map(str, keys.values()))
                if key not in items:
                    items[key] = keys

                # for key_name, value in keys.items():
                #     if key_name not in items[key]:
                #         items[key][key_name] = value
                items[key][column] = item.typed_value()
            else:
                if keys[key] not in items:
                    items[keys[key]] = keys

                items[keys[key]][column] = item.typed_value()

        return items

    def snmp_table(self, oid: str, key_mappings: dict) -> dict:
        """
        Fetch an SNMP table as a dict
        :param oid: Base OID to walk
        :param key_mappings: OID as key, name as value
        :return: Dict with table values
        """
        session = self.get_session()
        data = {}
        for item in session.walk(oid):
            matches = re.match(r'.+\.([0-9]+)\.([0-9]+)', item.oid)
            col = int(matches.group(1))
            row = int(matches.group(2))
            try:
                field_name = key_mappings[col]
            except KeyError:
                field_name = col

            if row not in data.keys():
                data[row] = {}

            data[row][field_name] = item.typed_value()

        return data

    def lldp(self):
        session = self.get_session()
        oid = '.1.0.8802.1.1.2.1.4.1.1'  # LLDP-MIB::lldpRemEntry
        keys = ['lldpRemTimeMark', 'lldpRemLocalPortNum', 'lldpRemIndex']
        fields = {1: 'lldpRemTimeMark',
                  2: 'lldpRemLocalPortNum',
                  3: 'lldpRemIndex',
                  4: 'lldpRemChassisIdSubtype',
                  5: 'lldpRemChassisId',
                  6: 'lldpRemPortIdSubtype',
                  7: 'lldpRemPortId',
                  8: 'lldpRemPortDesc',
                  9: 'lldpRemSysName',
                  10: 'lldpRemSysDesc',
                  11: 'lldpRemSysCapSupported',
                  12: 'lldpRemSysCapEnabled'
                  }

        ports = self.build_dict_multikeys('.1.0.8802.1.1.2.1.3.7.1',  # LLDP::lldpLocPortEntry
                                          key_names=['lldpLocPortNum'],
                                          fields={1: 'lldpLocPortNum',
                                                  2: 'lldpLocPortIdSubtype',
                                                  3: 'lldpLocPortId',
                                                  4: 'lldpLocPortDesc',
                                                  },
                                          )

        lldp_data = self.build_dict_multikeys(oid='.1.0.8802.1.1.2.1.4.1.1',
                                              # LLDP-MIB::lldpRemManAddrTable
                                              key_names=keys,
                                              fields=fields, key='lldpRemLocalPortNum',
                                              session=session)
        try:
            addresses = self.build_dict_multikeys(oid='.1.0.8802.1.1.2.1.4.2.1',
                                                  key_names=['lldpRemTimeMark', 'lldpRemLocalPortNum',
                                                             'lldpRemIndex', 'lldpRemManAddrSubtype',
                                                             'lldpRemManAddr'],
                                                  fields={
                                                      1: 'lldpRemManAddrSubtype',
                                                      2: 'lldpRemManAddr',
                                                      3: 'lldpRemManAddrIfSubtype',
                                                      4: 'lldpRemManAddrIfId',
                                                      5: 'lldpRemManAddrOID',
                                                  },
                                                  key='lldpRemLocalPortNum')
        except exceptions.SNMPError:
            addresses = {}

        neighbors = {}
        for key, value in lldp_data.items():
            if key not in ports:
                print('LLDP neighbor %s found on non-existing port %d' % (
                    lldp_data[key]['lldpRemSysName'], key))
                continue

            if value['lldpRemChassisIdSubtype'] == '4':
                mac = utils.mac_string(value['lldpRemChassisId'])
            else:
                mac = None

            neighbors[key] = {0: {
                'device_id': lldp_data[key]['lldpRemSysName'],
                'platform': lldp_data[key]['lldpRemSysDesc'],
                'local_port_num': lldp_data[key]['lldpRemLocalPortNum'],
                'local_port': ports[key],
                'remote_port': lldp_data[key]['lldpRemPortId'],
                'mac': mac,
            }}

            if key in addresses:
                if addresses[key]['lldpRemManAddr'][0] not in ['1', '2']:
                    neighbors[key][0]['ip'] = utils.ip_string(addresses[key]['lldpRemManAddr'])
                else:
                    neighbors[key][0]['ip'] = addresses[key]['lldpRemManAddr']
            else:
                neighbors[key][0]['ip'] = None

        return neighbors

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

            # Windows computers send their MAC-address as LLDP remote port and device id
            try:
                if len(cdp[if_index][device_index]['remote_port']) == 6 and \
                        cdp[if_index][device_index]['device_id'] == \
                        cdp[if_index][device_index]['remote_port']:
                    mac = ''
                    cdp[if_index][device_index]['device_id'] = utils.mac_string(
                        cdp[if_index][device_index]['device_id'])
                    cdp[if_index][device_index]['remote_port'] = ''
            except KeyError:
                pass
            except TypeError:
                pass

        return cdp

    def aggregations(self):
        oid = '.1.2.840.10006.300.43.1.2.1.1.13'  # IEEE8023-LAG-MIB::dot3adAggPortAttachedAggID
        session = self.get_session()
        aggregations = {}
        try:
            for entry in session.walk(oid):
                interface = int(utils.last_section(entry.oid))
                aggregation = int(entry.value)
                if aggregation == 0:
                    continue  # Interface is not member of an aggregation
                pass
                if aggregation not in aggregations:
                    aggregations[aggregation] = []
                aggregations[aggregation].append(interface)

        except exceptions.SNMPError as e:
            e.message = 'Error fetching aggregations'
            raise e

        return aggregations

    def arp(self):
        if self.arp_oid == 'atPhysAddress':
            oid = '.1.3.6.1.2.1.3.1.1.2'  # RFC1213-MIB::atPhysAddress
        elif self.arp_oid == 'ipNetToMediaPhysAddress':
            oid = '.1.3.6.1.2.1.4.22.1.2'  # RFC1213-MIB::ipNetToMediaPhysAddress
        else:
            raise ValueError('Invalid arp field')

        session = self.get_session()

        ip = []
        mac = []
        try:
            for item in session.walk(oid):
                ip_match = re.search(r'(?:[0-9]{1,3}\.?){4}$', item.oid)
                if ip_match:
                    ip.append(ip_match.group(0))
                    mac.append(utils.mac_string(item.value))
                else:
                    print('No match: ' + item.oid)
        except exceptions.SNMPError as e:
            e.message = 'Error fetching ARP'
            raise e

        return dict(zip(mac, ip))
