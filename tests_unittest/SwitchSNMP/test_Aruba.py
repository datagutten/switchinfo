import unittest

from switchinfo import SwitchSNMP
from .snmp_data import get_file

session = SwitchSNMP.ArubaVSF(*get_file('aruba_test'))
session_lldp = SwitchSNMP.ArubaVSF(*get_file('lldp_aruba'))


class ArubaTestCase(unittest.TestCase):
    def test_lldp_aruba(self):
        lldp = session_lldp.lldp()
        self.assertEqual(lldp[2][0]['device_id'], 'HV-HK-214')
        self.assertEqual(lldp[2][0]['local_port_num'], 2)

    def test_lldp_aruba2(self):
        lldp = session_lldp.lldp()
        self.assertEqual(lldp[42][0]['device_id'], 'cisco WS-C2960L-48T')
        self.assertEqual(lldp[42][0]['local_port_num'], 42)
        self.assertEqual(lldp[42][0]['remote_port'], 'GigabitEthernet0/48')
        self.assertEqual(lldp[42][0]['ip'], '192.168.15.83')


if __name__ == "__main__":
    unittest.main()  # run all tests
