from django.test import TestCase

from switchinfo import SwitchSNMP
from switchinfo import models
from switchinfo.SwitchSNMP import select
from switchinfo.load_info.switch_info import switch_type
from tests_unittest.SwitchSNMP.snmp_data import get_file


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

    def test_extreme(self):
        desc = 'ExtremeXOS (X450e-48p) version 15.3.4.6 v1534b6-patch1-10 by release-manager on Sat Dec 6 15:03:37 EST 2014'
        self.assertEqual('Extreme', switch_type(desc))
        community, ip = get_file('extreme')
        switch = models.Switch(ip=ip, community=community, type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.Extreme)

    def test_pfsense(self):
        desc = 'pfSense pfSense.quad.local 2.6.0-RELEASE FreeBSD 12.3-STABLE amd64'
        self.assertEqual('pfSense', switch_type(desc))
        community, ip = get_file('pfsense')
        switch = models.Switch(ip=ip, community=community, type=switch_type(desc))
        self.assertIsInstance(select.get_switch(switch), SwitchSNMP.PfSense)
