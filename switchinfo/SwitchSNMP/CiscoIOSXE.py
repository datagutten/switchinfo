from switchinfo.SwitchSNMP import Cisco
from . import mibs, utils, exceptions


class CiscoIOSXE(Cisco):
    """
    Cisco IOS XE
    """
    poe_absolute_index = False
    lldp_key = 'interface_name'

    def lldp(self):
        lldp_mib = mibs.lldpMIB(self)
        ports = lldp_mib.lldpLocPortTable()
        remotes = lldp_mib.lldpRemTable()
        try:
            addresses = lldp_mib.lldpRemManAddrTable()
        except exceptions.SNMPError:
            addresses = {}

        neighbors = {}
        for key, remote in remotes.items():
            if key not in ports:
                print('LLDP neighbor %s found on non-existing port %d' % (
                    remotes[key]['lldpRemSysName'], key))
                continue
            else:
                port_id = ports[key]['lldpLocPortId']

            if remote['lldpRemChassisIdSubtype'] == '4':
                mac = utils.mac_string(remote['lldpRemChassisId'])
            else:
                mac = None

            neighbors[port_id] = {0: {
                'device_id': remotes[key]['lldpRemSysName'],
                'platform': remotes[key]['lldpRemSysDesc'],
                'local_port_num': remotes[key]['lldpRemLocalPortNum'],
                'local_port': ports[key],
                'remote_port': remotes[key]['lldpRemPortId'],
                'mac': mac,
            }}

            if key in addresses:
                if addresses[key]['lldpRemManAddr'][0] not in ['1', '2']:
                    neighbors[port_id][0]['ip'] = utils.ip_string(addresses[key]['lldpRemManAddr'])
                else:
                    neighbors[port_id][0]['ip'] = addresses[key]['lldpRemManAddr']
            else:
                neighbors[port_id][0]['ip'] = None

        return neighbors
