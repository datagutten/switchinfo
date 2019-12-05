from django.test import TestCase

from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP


class SNMPTestCase(TestCase):
    device = None

    def setUp(self):
        self.device = SwitchSNMP(community='aruba_test', device='127.0.0.1')

    def test_switch_info_aruba(self):
        device_aruba = SwitchSNMP(community='aruba_test', device='127.0.0.1')
        info = device_aruba.switch_info()
        self.assertEqual('JL258A', info['model'])
        self.assertEqual('SFswitch', info['name'])
        self.assertIn('Aruba JL258A 2930F-8G-PoE+-2SFP+ Switch', info['descr'])
        device_aruba.sessions = None

    def test_vlan_names(self):
        names = self.device.vlan_names()
        expected_vlans = {'1': 'DEFAULT_VLAN', '9': 'Modem', '12': 'PC',
                          '100': 'Management'}
        self.assertEqual(expected_vlans.items(), names.items())
