import unittest

from parameterized import parameterized

from switchinfo.SwitchSNMP import mibs, utils
from switchinfo.SwitchSNMP.EasySNMPCompat import EasySNMPCompat
from switchinfo.SwitchSNMP.NetSNMPCompat import NetSNMPCompat
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP, select_library


def build_combinations(libraries, vendors):
    combinations = []
    key = 1
    for library in libraries:
        for vendor in vendors:
            combinations.append([library, vendor, key])
            key += 1

    return combinations


class SNMPValueTypeTestCase(unittest.TestCase):
    @parameterized.expand(
        build_combinations(['easysnmp', 'netsnmp'], ['cisco', 'aruba_test'])
    )
    def test_value(self, snmp_library, vendor, key):
        snmp = SwitchSNMP(vendor, '127.0.0.%d' % key, snmp_library=snmp_library)
        if_mib = mibs.ifMIB(snmp)
        interfaces = if_mib.ifXTable()

        self.assertEqual(select_library(snmp_library), type(snmp.get_session()))
        if vendor == 'cisco':
            interface_key = 10101
        else:
            interface_key = 663

        self.assertEqual(int, type(interfaces[interface_key]['ifHighSpeed']))
        self.assertEqual(str, type(interfaces[interface_key]['ifAlias']))
        self.assertEqual(int, type(interfaces[interface_key]['ifInMulticastPkts']))

    @parameterized.expand([['netsnmp', 1], ['easysnmp', 2]])
    def test_mac(self, snmp_library, key):
        session_lldp = SwitchSNMP('lldp_cisco', '127.0.0.%d' % key, snmp_library=snmp_library)
        if snmp_library == 'netsnmp':
            self.assertIsInstance(session_lldp.get_session(), NetSNMPCompat)
        elif snmp_library == 'easysnmp':
            self.assertIsInstance(session_lldp.get_session(), EasySNMPCompat)
        mac = session_lldp.get_session().get('.1.0.8802.1.1.2.1.4.1.1.5.0.4.803')

        self.assertEqual('3817c3c934d2', utils.mac_string(mac.typed_value()))


if __name__ == "__main__":
    unittest.main()  # run all tests
