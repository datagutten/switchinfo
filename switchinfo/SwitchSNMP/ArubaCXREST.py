import pyaoscx.session
from config_backup import ConfigBackup
from pyaoscx.exceptions.login_error import LoginError

from switchinfo.SwitchSNMP import ArubaCX


class ArubaCXREST(ArubaCX):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = ConfigBackup.backup_options(self.switch)
        try:
            self.aos_session = pyaoscx.session.Session(self.switch.ip, '10.09')
            self.aos_session.open(options.username, options.password)
        except LoginError:
            self.aos_session = pyaoscx.session.Session(self.switch.ip, '10.04')
            self.aos_session.open(options.username, options.password)

    def arp(self):
        arp = self.aos_session.request('GET', 'system/vrfs/*/neighbors?attributes=ip_address,mac&depth=2')
        arp_table = {}
        for vrf, entries in arp.json().items():
            for entry in entries.values():
                mac = entry['mac'].replace(':', '')
                arp_table[mac] = entry['ip_address']

        return arp_table
