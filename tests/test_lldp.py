import unittest

from switchinfo.SwitchSNMP.SwitchSNMP import SwitchSNMP

device_aruba = SwitchSNMP(community='lldp_aruba', device='127.0.0.1')
device_cisco = SwitchSNMP(community='lldp_cisco', device='127.0.0.2')


class LLDPTestCase(unittest.TestCase):
    def test_lldp_aruba(self):
        lldp = device_aruba.lldp()
        self.assertEqual(lldp[2][0]['device_id'], 'HV-HK-214')
        self.assertEqual(lldp[2][0]['local_port_num'], 2)

    def test_lldp_aruba2(self):
        lldp = device_aruba.lldp()

        self.assertEqual(lldp[42][0]['device_id'], 'cisco WS-C2960L-48T')
        self.assertEqual(lldp[42][0]['local_port_num'], 42)
        self.assertEqual(lldp[42][0]['remote_port'], 'GigabitEthernet0/48')
        self.assertEqual(lldp[42][0]['ip'], '192.168.15.83')

    def test_cisco(self):
        lldp = device_cisco.lldp()
        self.assertEqual(lldp[4][0]['device_id'], 'SFIKT-34:d2')
        self.assertEqual(lldp[4][0]['local_port_num'], 4)
        self.assertEqual(lldp[4][0]['remote_port'], '3817c3c934d2')


if __name__ == "__main__":
    unittest.main()  # run all tests
