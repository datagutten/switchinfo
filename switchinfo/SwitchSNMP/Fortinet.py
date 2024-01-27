import re

from . import SwitchSNMP, mibs


class Fortinet(SwitchSNMP):
    def interfaces_rfc(self):
        interfaces = super().interfaces_rfc()
        interfaces['alias'] = interfaces['descr']
        return interfaces

    def vlans(self):
        mib = mibs.qBridgeMIB(self)
        return mib.dot1qVlanIndex().values()

    def aggregations(self):
        oid = '.1.3.6.1.4.1.12356.106.3.1.0'  # fsTrunkMember.0
        session = self.get_session()
        data = session.get(oid)
        aggregations = {}
        for match in re.findall(r'(.+?):\s(.+?)\s::', data.value):
            aggregations[match[0]] = match[1].split('  ')

        return aggregations

    def mac_on_port(self, vlan=None, use_q_bridge_mib=None):
        oid = '.1.3.6.1.2.1.17.4.3'  # BRIDGE-MIB::dot1dTpFdbTable
        data = self.snmp_table(oid, {
            1: 'dot1dTpFdbAddress',
            2: 'dot1dTpFdbPort',
            3: 'dot1dTpFdbStatus'
        })
        macs = {}

        for entry in data.values():
            macs[entry['dot1dTpFdbAddress']] = int(entry['dot1dTpFdbPort'])
        return macs
