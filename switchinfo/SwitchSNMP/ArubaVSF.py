from snmp_compat.snmp_exceptions import SNMPNoData
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class ArubaVSF(SwitchSNMP):
    arp_oid = 'ipNetToMediaPhysAddress'
    static_vlan = False

    def stack_ports(self):
        oid = '.1.3.6.1.4.1.11.2.14.11.5.1.116.1.5.1.2'
        try:
            return self.create_dict(oid=oid, int_index=True)
        except SNMPNoData:
            return []
