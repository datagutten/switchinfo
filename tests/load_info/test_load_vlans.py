from django.test import TestCase

from switchinfo.load_info import switch_info
from switchinfo.load_info.load_vlan import load_vlan
from switchinfo.models import Vlan
from tests_unittest.SwitchSNMP.snmp_data import get_file


class LoadInfoTestCase(TestCase):
    def setUp(self):
        file, ip = get_file('cisco')
        self.switch_cisco = switch_info.switch_info(ip=ip, community=file)
        file, ip = get_file('aruba_test')
        self.switch_aruba = switch_info.switch_info(ip=ip, community=file)

    def testLoadVlans(self):
        load_vlan(self.switch_cisco, silent=False)
        vlan = Vlan.objects.get(vlan=12, on_switch=self.switch_cisco)
        self.assertEqual('PC', vlan.name)
        vlan = Vlan.objects.get(vlan=9, on_switch=self.switch_cisco)
        self.assertEqual('Modem', vlan.name)

    def testRemovedVlan(self):
        bad_vlan = self.switch_cisco.vlan.create(vlan=11)
        self.assertIn(bad_vlan, self.switch_cisco.vlan.all())
        load_vlan(self.switch_cisco, silent=False)
        self.assertNotIn(bad_vlan, self.switch_cisco.vlan.all())
        vlan = Vlan.objects.get(vlan=9)
        self.assertIn(vlan, self.switch_cisco.vlan.all())

    def testUpdatedName(self):
        vlan = self.switch_cisco.vlan.create(vlan=12, name='Klient')
        self.assertEqual('Klient', vlan.name)
        load_vlan(self.switch_cisco)
        vlan = Vlan.objects.get(vlan=12, on_switch=self.switch_cisco)
        self.assertEqual('PC', vlan.name)
