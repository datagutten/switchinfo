import unittest

from parameterized import parameterized

from switchinfo.SwitchSNMP import mibs, utils
from switchinfo.SwitchSNMP.EasySNMPCompat import EasySNMPCompat
from switchinfo.SwitchSNMP.NetSNMPCompat import NetSNMPCompat
from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP, select_library
from .snmp_data import get_file


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
        snmp = SwitchSNMP(*get_file(vendor), snmp_library=snmp_library)
        snmp.sessions = {}
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

    @parameterized.expand([['netsnmp'], ['easysnmp']])
    def test_mac(self, snmp_library):
        session_lldp = SwitchSNMP(*get_file('lldp_cisco'), snmp_library=snmp_library)
        session_lldp.sessions = {}
        if snmp_library == 'netsnmp':
            self.assertIsInstance(session_lldp.get_session(), NetSNMPCompat)
        elif snmp_library == 'easysnmp':
            self.assertIsInstance(session_lldp.get_session(), EasySNMPCompat)
        mac = session_lldp.get_session().get('.1.0.8802.1.1.2.1.4.1.1.5.0.4.803')

        self.assertEqual('3817c3c934d2', utils.mac_string(mac.typed_value()))


if __name__ == "__main__":
    unittest.main()  # run all tests

    # @parameterized.expand(
    #     build_combinations(['easysnmp', 'netsnmp'], ['cisco', 'aruba_test'])
    # )
    # def test_timetics(self, snmp_library, vendor, key):
    #     snmp = SwitchSNMP(vendor, '127.0.0.%d' % key, snmp_library=snmp_library)
    #     if_mib = mibs.ifMIB(snmp)
    #     interfaces = if_mib.ifTable()
    #     if vendor == 'cisco':
    #         interface_key = 10101
    #     else:
    #         interface_key = 1
    #     pass
    # def test_uptime(self):
    #     session = SwitchSNMP(*get_file('cisco'))
