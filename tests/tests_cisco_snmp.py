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

    def test_vlan_names(self):
        names = self.device.vlan_names()
        expected_vlans = {'1': 'default', '9': 'Modem', '12': 'PC',
                          '100': 'Management', '1002': 'fddi-default',
                          '1003': 'token-ring-default',
                          '1004': 'fddinet-default', '1005': 'trnet-default'}
        self.assertEqual(expected_vlans.items(), names.items())

