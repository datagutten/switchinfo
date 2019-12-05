from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP
from switchinfo.SwitchSNMP import utils


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
        """
        Check if the port is trunk or not
        :param device:
        :return dict: Key interfaceIndex Value:  INTEGER {on(1),
                                                          off(2),
                                                          desirable(3),
                                                          auto(4),
                                                          onNoNegotiate(5)
                                                          }
        """
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.13'  # CISCO-VTP-MIB::vlanTrunkPortDynamicState
        return self.create_dict(device, oid=oid, int_index=True, int_value=True)

    def port_vlan(self, device=None):
        # CISCO-VLAN-MEMBERSHIP-MIB::vmVlan
        oid = '.1.3.6.1.4.1.9.9.68.1.2.2.1.2'
        return self.create_dict(device, oid=oid, int_index=True, int_value=True)

    def native_vlan(self, device=None):
        #  vlanTrunkPortNativeVlan
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.5'
        return self.create_dict(device, oid=oid, int_index=True, int_value=True)

    def tagged_vlans(self):
        # CISCO-VTP-MIB::vlanTrunkPortVlansEnabled
        oid = '.1.3.6.1.4.1.9.9.46.1.6.1.1.4'
        return self.create_dict(oid=oid, int_index=True)

    def vlan_ports(self, debug=False):
        from pprint import pprint

        trunk_status = self.trunk_status()
        native_vlan = self.native_vlan()

        port_vlan = dict()
        tagged_vlans = dict()
        untagged_vlan = dict()
        all_tagged = chr(127) + chr(255)*127

        for index, vlans in self.tagged_vlans().items():
            if trunk_status[index] == 2:
                if debug:  # pragma: no cover
                    print('%s is not trunk' % index)
                continue
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
                    if native_vlan[index] == 1:
                        port_vlan[index] = None
                    else:
                        port_vlan[index] = native_vlan[index]
                        untagged_vlan[index] = native_vlan[index]

        for index, vlan in self.port_vlan().items():
            if index not in untagged_vlan:
                untagged_vlan[index] = vlan

        if debug:  # pragma: no cover
            print('Vlan: ', port_vlan)
            print('Tagged: ')
            pprint(tagged_vlans)
            print('Untagged :', untagged_vlan)

        return [port_vlan, tagged_vlans, untagged_vlan]
