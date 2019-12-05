from pprint import pprint

from django.test import TestCase
from switchinfo.SwitchSNMP.Cisco import Cisco
from switchinfo.load_info import switch_info
from switchinfo.load_info.load_vlan import load_vlan
from switchinfo.models import Vlan


class LoadInfoTestCase(TestCase):
    switch = None

    def setUp(self):
        self.switch = switch_info.switch_info('127.0.0.1', 'public')

    def testLoadInterfaces(self):
        # device = Cisco(community='cisco', device='127.0.0.1')

        pass

    def testLoadVlans(self):
        load_vlan(self.switch)
        vlan = Vlan.objects.get(vlan=12, on_switch=self.switch)
        self.assertEqual('PC', vlan.name)
        vlan = Vlan.objects.get(vlan=9, on_switch=self.switch)
        self.assertEqual('Modem', vlan.name)
