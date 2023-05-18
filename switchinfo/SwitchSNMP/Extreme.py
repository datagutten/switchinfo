import re

from switchinfo.SwitchSNMP import exceptions, utils
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Extreme(SwitchSNMP):

    def arp(self, device=None, arp_model=None):
        oid = '.1.3.6.1.4.1.1916.1.16.2.1.2'  # EXTREME-FDB-MIB::extremeFdbIpFdbIPAddress
        ip = self.create_list(device, oid=oid)
        oid = '.1.3.6.1.4.1.1916.1.16.2.1.3'  # EXTREME-FDB-MIB::extremeFdbIpFdbMacAddress
        mac = self.create_list(device, oid=oid)
        return dict(zip(mac, ip))

    def vlan_index(self):
        # EXTREME-VLAN-MIB::extremeVlanIfVlanId
        oid = '.1.3.6.1.4.1.1916.1.2.1.2.1.10'
        return self.create_dict(oid=oid, int_value=True, int_index=True)

    def vlans(self):
        return list(self.vlan_index().values())

    def vlan_names(self):
        oid = '.1.3.6.1.4.1.1916.1.2.1.2.1.2'  # EXTREME-VLAN-MIB::extremeVlanIfTable
        try:
            vlans = self.vlan_index()
            names = self.create_dict(oid=oid, int_index=True)
            return dict(zip(vlans.values(), names.values()))
        except exceptions.SNMPError as e:
            e.message = 'Unable to get VLAN names'
            raise e

    def _create_vlan_dict(self, ip=None, vlan=None, oid=None):
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
            index = re.sub(r'.+\.(\d+)\.\d+', r'\1', item.oid)
            if not index:
                index = item.oid_index
            indexes[int(index)] = item.value

        return indexes

    def egress_ports(self, static=False):
        raise NotImplementedError()

    def tagged_ports(self):
        # extremeVlanOpaqueTaggedPorts
        oid = '.1.3.6.1.4.1.1916.1.2.6.1.1.1'
        return self._create_vlan_dict(oid=oid)

    def untagged_ports(self, static=False):
        # extremeVlanOpaqueUntaggedPorts
        oid = '.1.3.6.1.4.1.1916.1.2.6.1.1.2'
        return self._create_vlan_dict(oid=oid)

    def vlan_ports(self, static=False, **kwargs):
        tagged = self.tagged_ports()
        untagged = self.untagged_ports()
        port_vlan = dict()
        tagged_vlans = dict()
        untagged_vlan = dict()
        vlans = self.vlan_index()

        for vlan_index, ports in tagged.items():
            vlan = vlans[vlan_index]

            tagged_ports = utils.parse_port_list(ports)
            untagged_ports = utils.parse_port_list(untagged[vlan_index])
            for index, port in tagged_ports.items():
                if untagged_ports[index]:
                    port_vlan[index] = vlan
                    untagged_vlan[index] = vlan
                if tagged_ports[index]:
                    if index not in tagged_vlans:
                        tagged_vlans[index] = []
                    tagged_vlans[index].append(vlan)
                    port_vlan[index] = None

        return [port_vlan, tagged_vlans, untagged_vlan]
