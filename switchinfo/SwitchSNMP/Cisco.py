from abc import ABC

from snmp_compat import snmp_exceptions
from switchinfo.SwitchSNMP import utils
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from . import mibs


class Cisco(SwitchSNMP, ABC):
    """
    Common stuff for Cisco IOS and IOS XE
    """
    lldp_key = 'bridge_port'

    poe_snmp_key = None
    """Field in entityMIB::entPhysicalTable containing the key to use to match interface"""

    poe_db_key = None
    """Database field that matches the key for the PoE value from SNMP"""

    mac_per_vlan = True

    def vlans(self):
        # CISCO-VTP-MIB::vtpVlanState
        oid = '.1.3.6.1.4.1.9.9.46.1.3.1.1.2'
        vlans = self.create_dict(oid=oid)
        if not vlans:
            return False
        vlan_list = []
        for vlan in vlans:
            if vlan not in [1002, 1003, 1004, 1005, 4095]:
                vlan_list.append(vlan)
        return vlan_list

    # Return key: vlan number
    def vlan_names(self):
        oid = '.1.3.6.1.4.1.9.9.46.1.3.1.1.4'  # vtpVlanName
        return self.create_dict(oid=oid, int_index=True)

    # Return key: interfaceIndex
    def trunk_status(self):
        """
        Check if the port is trunk or not
        :return dict: Key interfaceIndex Value:  INTEGER {on(1),
                                                          off(2),
                                                          desirable(3),
                                                          auto(4),
                                                          onNoNegotiate(5)
                                                          }
        """
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.13'  # CISCO-VTP-MIB::vlanTrunkPortDynamicState
        return self.create_dict(oid=oid, int_index=True)

    def port_vlan(self):
        # CISCO-VLAN-MEMBERSHIP-MIB::vmVlan
        oid = '.1.3.6.1.4.1.9.9.68.1.2.2.1.2'
        return self.create_dict(oid=oid, int_index=True)

    def native_vlan(self):
        #  vlanTrunkPortNativeVlan
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.5'
        return self.create_dict(oid=oid, int_index=True)

    def tagged_vlans(self):
        # CISCO-VTP-MIB::vlanTrunkPortVlansEnabled
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.4'
        return self.create_dict(oid=oid, int_index=True)

    def vlan_ports(self, debug=False, **kwargs):
        vtp_mib = mibs.CiscoVTP(self)
        vlans = vtp_mib.vlanTrunkPortTable(
            ['vlanTrunkPortNativeVlan', 'vlanTrunkPortVlansEnabled', 'vlanTrunkPortDynamicState'])

        from pprint import pprint

        trunk_status = self.trunk_status()
        native_vlan = self.native_vlan()

        port_vlan = dict()
        tagged_vlans = dict()
        untagged_vlan = dict()
        all_tagged = chr(127) + chr(255) * 127

        for index, vlans in self.tagged_vlans().items():
            if trunk_status[index] == 2:
                if debug:  # pragma: no cover
                    print('%s is not trunk' % index)
                continue
            if native_vlan[index] == 1:
                port_vlan[index] = None
            else:
                port_vlan[index] = native_vlan[index]
                untagged_vlan[index] = native_vlan[index]
                tagged_vlans[index] = ['all']

            if vlans == all_tagged:
                if debug:  # pragma: no cover
                    print('All vlans are tagged on port %s' % index)
                continue

            for vlan_id, tagged in utils.parse_port_list(vlans, zero_count=True).items():
                if tagged:
                    if debug:  # pragma: no cover
                        print('Vlan %s is tagged on port %s' % (vlan_id, index))
                    if index not in tagged_vlans:
                        tagged_vlans[index] = []
                    tagged_vlans[index].append(vlan_id)

        try:
            for index, vlan in self.port_vlan().items():
                if index not in untagged_vlan:
                    untagged_vlan[index] = vlan
        except snmp_exceptions.SNMPError:
            print('No untagged vlans')
            pass

        if debug:  # pragma: no cover
            print('Vlan: ', port_vlan)
            print('Tagged: ')
            pprint(tagged_vlans)
            print('Untagged :', untagged_vlan)

        return [port_vlan, tagged_vlans, untagged_vlan]

    def interface_poe(self):
        cisco_poe_mib = mibs.CiscoPowerEthernetMIB(self)
        poe_mib = mibs.powerEthernetMIB(self)
        entity_mib = mibs.entityMIB(self)
        poe_ports_cisco = cisco_poe_mib.cpeExtPsePortTable(['cpeExtPsePortEntPhyIndex'])
        poe_ports = poe_mib.pethPsePortTable()
        phys_ports = entity_mib.entPhysicalTable([self.poe_snmp_key])

        ports = {}
        for key, port in poe_ports.items():
            if key not in poe_ports_cisco:
                continue
            cisco_port = poe_ports_cisco[key]
            if cisco_port['cpeExtPsePortEntPhyIndex'] not in phys_ports:
                continue
            phys_port = phys_ports[cisco_port['cpeExtPsePortEntPhyIndex']]
            port['pethPsePortDetectionStatus'] = poe_mib.states[port['pethPsePortDetectionStatus']]
            if phys_port[self.poe_snmp_key]:
                try:  # TODO: No need to convert value when new SNMP compat is implemented
                    ports[int(phys_port[self.poe_snmp_key])] = port
                except ValueError:
                    ports[phys_port[self.poe_snmp_key]] = port

        return ports
