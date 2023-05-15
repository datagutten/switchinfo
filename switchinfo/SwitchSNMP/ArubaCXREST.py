import math

from switchinfo.SwitchSNMP import ArubaCX


class ArubaCXREST(ArubaCX):

    def __init__(self, *args, **kwargs):
        # Imports are placed here to avoid crash on import if pyaoscx is not installed
        import pyaoscx.session
        from config_backup import ConfigBackup
        from pyaoscx.exceptions.login_error import LoginError

        super().__init__(*args, **kwargs)
        options = ConfigBackup.backup_options(self.switch)
        try:
            self.aos_session = pyaoscx.session.Session(self.switch.ip, '10.09')
            self.aos_session.open(options.username, options.password)
        except LoginError:
            self.aos_session = pyaoscx.session.Session(self.switch.ip, '10.04')
            self.aos_session.open(options.username, options.password)

    def __del__(self):
        self.aos_session.close()

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
            else:
                info['status'][key] = link_status(interface['link_state'])
                info['high_speed'][key] = interface['link_speed'] / math.pow(10, 6)
                info['admin_status'][key] = link_status(interface['admin_state'])

            if interface['vlan_tag'] is not None:
                info['untagged'][key] = int(list(interface['vlan_tag'].keys())[0])

            if interface['vlan_mode'] == 'native-untagged':
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
