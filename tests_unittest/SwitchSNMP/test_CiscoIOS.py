import datetime

import unittest

from switchinfo import SwitchSNMP
from .snmp_data import get_file

session = SwitchSNMP.CiscoIOS(*get_file('cisco'))
session_lldp = SwitchSNMP.CiscoIOS(*get_file('lldp_cisco'))


class CiscoIOSTestCase(unittest.TestCase):
    def test_poe_cisco(self):
        poe = session.interface_poe()
        key = list(poe.keys())[0]
        self.assertEqual(10101, key)

    def test_lldp(self):
        lldp = session_lldp.lldp()
        self.assertEqual(lldp[4][0]['device_id'], 'SFIKT-34:d2')
        self.assertEqual(lldp[4][0]['local_port_num'], 4)
        self.assertEqual(lldp[4][0]['remote_port'], '3817c3c934d2')

    def test_switch_info_cisco(self):
        info_cisco = session.switch_info()
        self.assertEqual('WS-C2960S-24PS-L', info_cisco['model'])
        self.assertEqual('ROV-SW-01.switch.ltf.local', info_cisco['name'])
        self.assertIn('Cisco IOS Software, C2960S Software', info_cisco['descr'])

    def test_vlans(self):
        self.assertEqual([1, 9, 12, 100], session.vlans())

    def test_interfaces(self):
        interfaces = session.interfaces_rfc()
        self.assertEqual('Trunk serverswitch', interfaces['alias']['10124'])
        self.assertEqual('GigabitEthernet1/0/24', interfaces['descr']['10124'])

    def test_mac_on_port(self):
        mac = session.mac_on_port()
        self.assertIn('00254532caae', mac)
        self.assertEqual('232', mac['00254532caae'])

    def test_bridgePort_to_ifIndex(self):
        table = session.bridgePort_to_ifIndex()
        self.assertEqual('10124', table['24'])

    def test_interface_poe_status(self):
        status = session.interface_poe()
        self.assertEqual('disabled', status[10110]['pethPsePortDetectionStatus'])
        self.assertEqual('deliveringPower', status[10122]['pethPsePortDetectionStatus'])

    def test_vlan_names(self):
        names = session.vlan_names()
        expected_vlans = {1: 'default', 9: 'Modem', 12: 'PC',
                          100: 'Management', 1002: 'fddi-default',
                          1003: 'token-ring-default',
                          1004: 'fddinet-default', 1005: 'trnet-default'}
        self.assertEqual(expected_vlans.items(), names.items())

    def test_vlan_ports(self):
        ports = session.vlan_ports()
        self.assertEqual(12, ports[2][10101])
        self.assertEqual(1, ports[2][10127])

    def test_uptime(self):
        uptime = session.uptime()
        uptime_expected = datetime.timedelta(hours=2803, minutes=45, seconds=15.73)
        self.assertEqual(uptime, uptime_expected)


if __name__ == "__main__":
    unittest.main()  # run all tests
