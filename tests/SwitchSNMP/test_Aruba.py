import unittest

from switchinfo import SwitchSNMP

session = SwitchSNMP.ArubaVSF('aruba_test', '127.0.0.1')
session_lldp = SwitchSNMP.ArubaVSF('lldp_aruba', '127.0.0.2')


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
