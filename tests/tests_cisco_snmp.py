from django.test import TestCase
from switchinfo.SwitchSNMP.Cisco import Cisco


class CiscoSNMPTestCase(TestCase):
    device = None

    def setUp(self):
        self.device = Cisco(community='cisco', device='127.0.0.1')

    def test_switch_info_cisco(self):
        info_cisco = self.device.switch_info()
        self.assertEqual('WS-C2960S-24PS-L', info_cisco['model'])
        self.assertEqual('ROV-SW-01.switch.ltf.local', info_cisco['name'])
        self.assertIn('Cisco IOS Software, C2960S Software', info_cisco['descr'])

    def test_vlans(self):
        self.assertEqual([1, 9, 12, 100], self.device.vlans())

    def test_uptime(self):
        uptime = self.device.uptime()
        self.assertEqual('1009351573', uptime)

    def test_interfaces(self):
        interfaces = self.device.interfaces_rfc()
        self.assertEqual('Trunk serverswitch', interfaces['alias']['10124'])
        self.assertEqual('GigabitEthernet1/0/24', interfaces['descr']['10124'])

    def test_mac_on_port(self):
        mac = self.device.mac_on_port()
        self.assertIn('00254532caae', mac)
        self.assertEqual('232', mac['00254532caae'])

    def test_bridgePort_to_ifIndex(self):
        table = self.device.bridgePort_to_ifIndex()
        self.assertEqual('10124', table['24'])

    def test_interface_poe_status(self):
        status = self.device.interface_poe_status()
        self.assertEqual('disabled', status['10'])
        self.assertEqual('deliveringPower', status['22'])

    def test_vlan_names(self):
        names = self.device.vlan_names()
        expected_vlans = {'1': 'default', '9': 'Modem', '12': 'PC',
                          '100': 'Management', '1002': 'fddi-default',
                          '1003': 'token-ring-default',
                          '1004': 'fddinet-default', '1005': 'trnet-default'}
        self.assertEqual(expected_vlans.items(), names.items())

    def test_vlan_ports(self):
        ports = self.device.vlan_ports()
        self.assertEqual(12, ports[2][10101])
        self.assertEqual(1, ports[2][10127])
