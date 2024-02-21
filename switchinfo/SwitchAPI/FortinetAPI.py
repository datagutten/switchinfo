import re

from switchinfo.SwitchSNMP.Fortinet import Fortinet
from . import api_exceptions


class FortinetAPI(Fortinet):
    ignore_unknown_vlans = True
    lldp_key = 'interface_name'

    def __init__(self, username, password, **kwargs):
        if not username or not password:
            raise api_exceptions.LoginFailed('Username or password not set')
        # Imports are placed here to avoid crash on import if requests is not installed
        import requests
        self.device = kwargs['device']

        self.session = requests.sessions.Session()
        self.session.verify = False
        super().__init__(device=kwargs['device'], community=kwargs['community'])
        self._login(username, password)

    def _login(self, username, password):
        payload = "username=%s&password=%s" % (username, password)
        response = self.session.post('https://%s/login' % self.device, data=payload)
        response.raise_for_status()
        if response.text.find('Invalid credentials, please try again.') > -1:
            raise api_exceptions.LoginFailed

    def _get(self, uri):
        return self.session.get('https://%s/api/v2/%s' % (self.device, uri))

    def mac_on_port(self, vlan=None, use_q_bridge_mib=None):
        response = self._get('monitor/switch/mac-address')
        macs = {}
        for entry in response.json()['results']:
            if 'mac' not in entry or entry['interface'] == 'internal':
                continue
            mac = entry['mac'].replace(':', '')
            macs[mac] = entry['interface']
        return macs

    def lldp(self):
        response = self._get('monitor/switch/lldp-state')
        neighbors = {}
        for entry in response.json()['results']:
            if 'port' not in entry.keys():
                continue
            if entry['port'] not in neighbors:
                neighbors[entry['port']] = []

            neighbors[entry['port']].append({
                'device_id': entry['system_name'],
                'platform': entry['system_description'],
                'local_port_num': entry['port'],
                'local_port': entry['port'],
                'remote_port': entry['port_description'],
                'mac': clean_mac(entry['chassis_id']),
                'ip': get_ip(entry['management_ip_address'])
            })
        return neighbors

    def vlans(self):
        response = self._get('cmdb/switch/vlan')
        vlans = []
        for entry in response.json()['results']:
            vlans.append(entry['id'])
        return vlans

    def vlan_names(self):
        response = self._get('cmdb/switch/vlan')
        vlan_names = {}
        for entry in response.json()['results']:
            vlan_names[entry['id']] = entry['description']
        return vlan_names


def clean_mac(mac):
    if mac.find('(mac)') == -1:
        return None
    mac = re.sub(r'([\da-f:]{17}).+', r'\1', mac)
    return mac.replace(':', '')


def get_ip(ip):
    if ip and 'ip_address' in ip[0]:
        return ip[0]['ip_address']
