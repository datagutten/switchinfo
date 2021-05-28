from switchinfo.SwitchSNMP import utils
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP.exceptions import SNMPNoData


class ArubaCX(SwitchSNMP):
    def interfaces_rfc(self):
        info = dict()
        # IF-MIB::ifName
        info['name'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.1')
        # IF-MIB::ifAlias
        # info['alias'] = self.create_dict(oid='.1.3.6.1.2.1.31.1.1.1.18')
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
        # info['duplex'] = self.create_dict(oid='.1.3.6.1.2.1.10.7.2.1.19')
        info['alias'] = {}
        session = self.get_session()
        for key in info['name'].keys():
            try:
                alias = session.get('.1.3.6.1.2.1.31.1.1.1.18.' + key)
                info['alias'][key] = alias.value
            except SNMPNoData:
                info['alias'][key] = None

        return info

    def vlan_names(self):
        # Q-BRIDGE-MIB::dot1qVlanStaticName
        oid = '.1.3.111.2.802.1.1.4.1.4.3.1.3'
        return self.create_dict(oid=oid)

    def egress_ports(self):
        # Qdot1qVlanCurrentEgressPorts
        values = self.create_dict(oid='.1.3.111.2.802.1.1.4.1.4.2.1.5')
        return values

    def untagged_ports(self):
        # ieee8021QBridgeVlanCurrentUntaggedPorts
        values = self.create_dict(oid='.1.3.111.2.802.1.1.4.1.4.2.1.6')
        return values

    def vlans(self, device=None):
        # Q-BRIDGE-MIB::dot1qVlanFdbId
        oid = '.1.3.111.2.802.1.1.4.1.4.2.1.4'
        vlans = self.create_dict(device, oid=oid)

        vlan_list = []
        for vlan in vlans:
            vlan_list.append(int(vlan))
        return vlan_list
