from django.test import TestCase

from switchinfo import SwitchSNMP
from switchinfo import models
from switchinfo.SwitchSNMP import select
from switchinfo.load_info.switch_info import switch_type


class SwitchTypeTestCase(TestCase):
    def test_cisco_ios12(self):
        desc = 'Cisco IOS Software, C2960 Software (C2960-LANLITEK9-M), Version 12.2(55)SE12, RELEASE SOFTWARE (fc2)'
        self.assertEqual('Cisco', switch_type(desc))
        switch = models.Switch(ip='127.0.0.1', community='cisco', type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.Cisco)

    def test_cisco_ios15(self):
        desc = 'Cisco IOS Software, C2960X Software (C2960X-UNIVERSALK9-M), Version 15.2(7)E6, RELEASE SOFTWARE (fc2)'
        self.assertEqual('Cisco', switch_type(desc))
        switch = models.Switch(ip='127.0.0.1', community='cisco', type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.Cisco)

    def test_cisco_ios16(self):
        desc = 'Cisco IOS Software [Fuji], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 16.9.4, RELEASE SOFTWARE (fc2)'
        self.assertEqual('Cisco IOS XE', switch_type(desc))
        switch = models.Switch(ip='127.0.0.1', community='cisco', type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.CiscoIOSXE)

    def test_cisco_ios17(self):
        desc = 'Cisco IOS Software [Bengaluru], Catalyst L3 Switch Software (CAT9K_LITE_IOSXE), Version 17.6.3, RELEASE SOFTWARE (fc4)'
        self.assertEqual('Cisco IOS XE', switch_type(desc))
        switch = models.Switch(ip='127.0.0.1', community='cisco', type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.CiscoIOSXE)
