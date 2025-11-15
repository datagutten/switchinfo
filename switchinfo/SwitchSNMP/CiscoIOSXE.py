from snmp_compat import snmp_exceptions
from switchinfo.SwitchSNMP import Cisco
from . import mibs, utils


class CiscoIOSXE(Cisco):
    """
    Cisco IOS XE
    """
    lldp_key = 'interface_name'
    poe_snmp_key = 'entPhysicalDescr'
    poe_db_key = 'interface'

    def lldp(self):
        lldp_mib = mibs.lldpMIB(self)
        ports = lldp_mib.lldpLocPortTable()
        remotes = lldp_mib.lldpRemTable()
        try:
            addresses = lldp_mib.lldpRemManAddrTable()
        except snmp_exceptions.SNMPError:
            addresses = {}

        neighbors = {}
        for key, remote in remotes.items():
            if key not in ports:
                print('LLDP neighbor %s found on non-existing port %d' % (
                    remotes[key]['lldpRemSysName'], key))
                continue

            neighbor = lldp_mib.remote_helper(remote)
            neighbor['local_port'] = ports[key]

            if key in addresses:
                address_fields = mibs.lldpMIB.remote_address_helper(addresses[key])
                neighbor.update(address_fields)

            port_id = ports[key]['lldpLocPortId']
            neighbors[port_id] = {0: neighbor}  # TODO: Handle multiple neighbors

        return neighbors
