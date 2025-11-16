from . import SwitchSNMP
from .mibs.RFC1213MIB import RFC1213MIB


class RacomMidge(SwitchSNMP):
    arp_oid = 'ipNetToMediaPhysAddress'

    def mac_on_port(self, *args, **kwargs):
        mib = RFC1213MIB(self)

        table = mib.ipNetToMediaTable(['ipNetToMediaIfIndex', 'ipNetToMediaPhysAddress'])
        interfaces = map(lambda x: x['ipNetToMediaIfIndex'], table.values())
        mac = map(lambda x: x['ipNetToMediaPhysAddress'], table.values())
        macs = dict(zip(mac, interfaces))
        return macs

    def interfaces_rfc(self):
        interfaces = super().interfaces_rfc()
        interfaces['untagged'] = {}
        interfaces['tagged'] = {}

        # We are not able to get vlan and MACs on physical interfaces, assume lan bridges are in vlan 1
        for key, name in interfaces['name'].items():
            if name.startswith('lan'):
                interfaces['untagged'][int(key)] = 1

        return interfaces
