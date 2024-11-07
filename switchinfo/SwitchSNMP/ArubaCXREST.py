import math
import re
import warnings
from urllib.parse import quote

from switchinfo.SwitchAPI.api_exceptions import LoginFailed, APIError
from switchinfo.SwitchSNMP import ArubaCX, utils


class ArubaCXREST(ArubaCX):
    aos_session = None
    lldp_key = 'interface_name'
    interface_key = 'interface_name'

    def __init__(self, username, password, **kwargs):
        if not username or not password:
            raise LoginFailed('Username or password not set')
        # Imports are placed here to avoid crash on import if pyaoscx is not installed
        import pyaoscx.session
        import requests.exceptions
        from pyaoscx.exceptions.login_error import LoginError
        from urllib3.exceptions import InsecureRequestWarning

        warnings.simplefilter("ignore", InsecureRequestWarning)

        super().__init__(**kwargs)
        try:
            try:
                self.aos_session = pyaoscx.session.Session(self.device, '10.09')
                self.aos_session.open(username, password)
            except LoginError:
                self.aos_session = pyaoscx.session.Session(self.device, '10.04')
                self.aos_session.open(username, password)
        except requests.exceptions.RequestException as e:
            raise APIError(e)
        except LoginError as e:
            raise APIError(e)

    def close_sessions(self):
        self.aos_session.close()

    def mac_on_port(self, vlan=None, use_q_bridge_mib=None):
        response_mac = self.aos_session.request('GET', 'system/vlans/%d/macs?attributes=port&depth=2' % int(vlan))
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
                    'platform': neighbor['platform'],
                    'remote_port': neighbor['port_id'],
                }
                if len(neighbor['addresses']) > 0:
                    cdp_neighbors[interface][key]['ip'] = neighbor['addresses'][0]

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
                    'platform': neighbor['neighbor_info']['chassis_description'] or None,
                    'remote_port': neighbor['port_id'],
                }
                if neighbor['neighbor_info']['chassis_name']:
                    lldp_neighbors[interface][key]['device_id'] = neighbor['neighbor_info']['chassis_name']
                else:
                    lldp_neighbors[interface][key]['device_id'] = neighbor['chassis_id']
                if 'mgmt_ip_list' in neighbor['neighbor_info']:
                    for address in neighbor['neighbor_info']['mgmt_ip_list'].split(','):
                        if re.match(r'[\da-f:]{17}', address):
                            lldp_neighbors[interface][key]['mac'] = address
                        elif utils.validate_ip(address):
                            lldp_neighbors[interface][key]['ip'] = address
                        else:
                            lldp_neighbors[interface][key]['unknown'] = address

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
                'high_speed': {}, 'untagged': {}, 'tagged': {}, 'index': {}}
        interfaces = self.aos_session.request('GET', 'system/interfaces?depth=2')
        for interface in interfaces.json().values():
            if interface['name'].find('lag') != 0 and interface['type'] != 'system':
                continue

            key = interface['name']
            info['name'][key] = interface['name']
            info['alias'][key] = interface['description']
            info['type'][key] = '6'
            info['high_speed'][key] = None
            info['index'][key] = interface['ifindex']
            if interface['name'].find('lag') == 0:
                info['status'][key] = link_status(interface['bond_status']['state'])
                if 'bond_speed' in interface['bond_status'] and interface['bond_status']['bond_speed']:
                    info['high_speed'][key] = interface['bond_status']['bond_speed'] / math.pow(10, 6)
                info['admin_status'][key] = link_status(interface['admin'])
            else:
                info['status'][key] = link_status(interface['link_state'])
                if interface['link_speed']:
                    info['high_speed'][key] = interface['link_speed'] / math.pow(10, 6)
                info['admin_status'][key] = link_status(interface['admin_state'])

            if 'lacp_current' in interface and interface['lacp_current']:
                continue
            # applied_vlan is used to get current vlan when using device profiles
            if 'applied_vlan_tag' in interface and interface['applied_vlan_tag'] is not None:
                info['untagged'][key] = int(list(interface['applied_vlan_tag'].keys())[0])

            if 'applied_vlan_mode' in interface and interface['applied_vlan_mode'] == 'native-untagged':
                if not interface['applied_vlan_trunks']:
                    info['tagged'][key] = ['all']
                else:
                    info['tagged'][key] = []
                    for vlan in interface['applied_vlan_trunks'].keys():
                        info['tagged'][key].append(int(vlan))

        return info


def link_status(status: str) -> int:
    status_mappings = {'up': 1, 'down': 0}
    if status in status_mappings:
        return status_mappings[status]
    else:  # Unmapped link state
        return 0
