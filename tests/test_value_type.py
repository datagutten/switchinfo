import os
import unittest

from parameterized import parameterized

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
        interfaces = snmp.if_table()

        self.assertEqual(select_library(snmp_library), type(snmp.get_session()))
        if vendor == 'cisco':
            interface_key = 10101
        else:
            interface_key = 1

        self.assertEqual(int, type(interfaces[interface_key]['ifHighSpeed']))
        self.assertEqual(str, type(interfaces[interface_key]['ifAlias']))
        self.assertEqual(int, type(interfaces[interface_key]['ifInMulticastPkts']))


if __name__ == "__main__":
    unittest.main()  # run all tests
