from django.test import TestCase

from switchinfo import load_info
from switchinfo.load_info import switch_info
from switchinfo.models import Interface
from tests.load_info.LoadInfoCommon import LoadInfoCommon


class LoadInfoTestCase(LoadInfoCommon):
    def testLoadInterfacesCisco(self):
        load_info.load_interfaces(self.switch_cisco)
        interface = Interface.objects.get(interface='Gi1/0/16', switch=self.switch_cisco)
        self.assertEqual(12, interface.vlan.vlan)
        self.assertEqual(10116, interface.index)
        self.assertEqual('Vanlig patchepunkt vlan 12', interface.description)
        self.assertEqual('disabled', interface.poe_status)

    def testLoadInterfacesAruba(self):
        load_info.load_interfaces(self.switch_aruba)
        interface = self.switch_aruba.interfaces.first()
        self.assertEqual(12, interface.vlan.vlan)
        self.assertEqual(1, interface.index)
        self.assertEqual(1000, interface.speed)
        self.assertEqual('searching', interface.poe_status)

    def testLoadInterfacesExtreme(self):
        load_info.load_interfaces(self.switch_extreme)
        interface = self.switch_extreme.interfaces.first()
        self.assertIsNotNone(interface)
        self.assertEqual(11, interface.vlan.vlan)
        self.assertEqual(1001, interface.index)
        self.assertEqual(100, interface.speed)
        self.assertEqual('searching', interface.poe_status)
