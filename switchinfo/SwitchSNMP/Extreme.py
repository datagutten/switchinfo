from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class Extreme(SwitchSNMP):

    # BRIDGE-MIB
    def ports(self, device=None):
        oid = '.1.3.6.1.2.1.17.4.4.1.1'  # dot1dTpPort
        return self.create_dict(device, oid=oid)

    def arp(self, device=None, arp_model=None):
        oid = '.1.3.6.1.4.1.1916.1.16.2.1.2'  # extremeFdbIpFdbIPAddress
        ip = self.create_list(device, oid=oid)
        oid = '.1.3.6.1.4.1.1916.1.16.2.1.3'  # extremeFdbIpFdbMacAddress
        mac = self.create_list(device, oid=oid)
        return dict(zip(mac, ip))

    def interface_poe_status(self):
        return
    #def trunk_status(self):
    #    return dict()