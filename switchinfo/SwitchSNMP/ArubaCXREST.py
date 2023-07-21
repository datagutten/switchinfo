import math
import re
from urllib.parse import quote

from switchinfo.SwitchAPI.api_exceptions import LoginFailed
from switchinfo.SwitchSNMP import ArubaCX


class ArubaCXREST(ArubaCX):
    aos_session = None

    def __init__(self, username, password, **kwargs):
        if not username or not password:
            raise LoginFailed('Username or password not set')
        # Imports are placed here to avoid crash on import if pyaoscx is not installed
        import pyaoscx.session
        from pyaoscx.exceptions.login_error import LoginError

        super().__init__(**kwargs)
        try:
            self.aos_session = pyaoscx.session.Session(self.device, '10.09')
            self.aos_session.open(username, password)
        except LoginError:
            self.aos_session = pyaoscx.session.Session(self.device, '10.04')
            self.aos_session.open(username, password)

    def __del__(self):
        if self.aos_session and self.aos_session.s:
            self.aos_session.close()

    def mac_on_port(self, vlan=None, use_q_bridge_mib=None):
        response_mac = self.aos_session.request('GET', 'system/vlans/%d/macs?attributes=port&depth=2' % vlan)
        mac_addresses = {}
        for mac, port in response_mac.json().items():
            mac = re.sub(r'dynamic,(.+)', r'\1', mac)
            mac = mac.replace(':', '')
            port = list(port['port'].keys())[0]
            mac_addresses[mac] = port
        return mac_addresses

    def uptime(self):
        pass

    def cdp_multi(self):
        interfaces = self.aos_session.request('GET', 'system/interfaces?depth=1')
        cdp_neighbors = {}
        for interface in interfaces.json():
            neighbors = self.aos_session.request('GET', 'system/interfaces/%s/cdp_neighbors?depth=2' % quote(interface,
                                                                                                             safe=[]))
            cdp_neighbors[interface] = {}
            for key, neighbor in neighbors.json().items():
                cdp_neighbors[interface][key] = {
                    'device_id': neighbor['device_id'],
                    'ip': neighbor['addresses'][0],
                    'platform': neighbor['platform'],
                    'remote_port': neighbor['port_id'],
                }

        return cdp_neighbors

    def lldp(self):
        interfaces = self.aos_session.request('GET', 'system/interfaces?depth=1')
        lldp_neighbors = {}
        for interface in interfaces.json():
            neighbors = self.aos_session.request('GET', 'system/interfaces/%s/lldp_neighbors?depth=2' % quote(interface,
                                                                                                              safe=[]))
            lldp_neighbors[interface] = {}
            for key, neighbor in neighbors.json().items():
                lldp_neighbors[interface][key] = {
                    'device_id': neighbor['chassis_id'],
                    'platform': neighbor['neighbor_info']['chassis_description'],
                    'remote_port': neighbor['port_id'],
                }
                if 'mgmt_ip_list' in neighbor:
                    lldp_neighbors[interface][key]['ip'] = neighbor['neighbor_info']['mgmt_ip_list']

        return lldp_neighbors

    def arp(self):
        arp = self.aos_session.request('GET', 'system/vrfs/*/neighbors?attributes=ip_address,mac&depth=2')
        arp_table = {}
        for vrf, entries in arp.json().items():
            for entry in entries.values():
                mac = entry['mac'].replace(':', '')
                arp_table[mac] = entry['ip_address']

        return arp_table

    def interfaces_rfc(self):
        info = {'name': {}, 'alias': {}, 'type': {}, 'status': {}, 'admin_status': {}, 'duplex': {},
                'high_speed': {}, 'untagged': {}, 'tagged': {}}
        interfaces = self.aos_session.request('GET', 'system/interfaces?depth=2')
        for interface in interfaces.json().values():
            if interface['name'].find('lag') != 0 and interface['type'] != 'system':
                continue

            key = interface['ifindex']
            info['name'][key] = interface['name']
            info['alias'][key] = interface['description']
            info['type'][key] = '6'
            if interface['name'].find('lag') == 0:
                info['status'][key] = link_status(interface['bond_status']['state'])
                info['high_speed'][key] = interface['bond_status']['bond_speed'] / math.pow(10, 6)
                info['admin_status'][key] = link_status(interface['admin'])
            else:
                info['status'][key] = link_status(interface['link_state'])
                info['high_speed'][key] = interface['link_speed'] / math.pow(10, 6)
                info['admin_status'][key] = link_status(interface['admin_state'])

            if 'lacp_current' in interface and interface['lacp_current']:
                continue

            if 'vlan_tag' in interface and interface['vlan_tag'] is not None:
                info['untagged'][key] = int(list(interface['vlan_tag'].keys())[0])

            if 'vlan_mode' in interface and interface['vlan_mode'] == 'native-untagged':
                if interface['vlan_trunks'] == {}:
                    info['tagged'][key] = ['all']
                else:
                    info['tagged'][key] = []
                    for vlan in interface['vlan_trunks'].keys():
                        info['tagged'][key].append(int(vlan))

        return info


def link_status(status: str) -> int:
    status_mappings = {'up': 1, 'down': 0}
    if status in status_mappings:
        return status_mappings[status]
    else:  # Unmapped link state
        return 0
