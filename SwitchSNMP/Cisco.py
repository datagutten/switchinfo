from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Cisco(SwitchSNMP):

    def vlans(self, device=None):
        # CISCO-VTP-MIB::vtpVlanState
        oid = '.1.3.6.1.4.1.9.9.46.1.3.1.1.2'
        vlans = self.create_dict(oid=oid, ip=device)
        if not vlans:
            return False
        vlan_list = []
        for vlan in vlans:
            if int(vlan) < 1000:
                vlan_list.append(int(vlan))
        return vlan_list

    # Return key: vlan number
    def vlan_names(self, device=None):
        oid = '.1.3.6.1.4.1.9.9.46.1.3.1.1.4'  # vtpVlanName
        return self.create_dict(device, oid=oid)

    # Return key: interfaceIndex
    def trunk_status(self, device=None):
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.14'  # vlanTrunkPortDynamicStatus
        return self.create_dict(device, oid=oid)

    def port_vlan(self, device=None):
        # CISCO-VLAN-MEMBERSHIP-MIB::vmVlan
        oid = '.1.3.6.1.4.1.9.9.68.1.2.2.1.2'
        return self.create_dict(device, oid=oid)

    # Return vlan number or None if the interface is trunk
    def vlan_ports(self):
        port_vlan = dict()
        # CISCO-VTP-MIB::vlanTrunkPortDynamicStatus
        oid_trunk = '.1.3.6.1.4.1.9.9.46.1.6.1.1.14'
        # CISCO-VTP-MIB::vmVlanType
        oid_vlans = '.1.3.6.1.4.1.9.9.68.1.2.2.1.2'
        vlans = self.create_dict(oid=oid_vlans)
        for ifindex, trunk in self.create_dict(oid=oid_trunk).items():
            key = int(ifindex)

            if trunk == '1' or ifindex not in vlans:
                port_vlan[key] = None
            else:
                port_vlan[key] = vlans[ifindex]
        return port_vlan
