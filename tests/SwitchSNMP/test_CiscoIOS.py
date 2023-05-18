import unittest

from switchinfo import SwitchSNMP

session = SwitchSNMP.Cisco('cisco', '127.0.0.1')


class CiscoIOSTestCase(unittest.TestCase):
    def test_poe_cisco(self):
        poe = session.interface_poe()
        key = list(poe.keys())[0]
        self.assertEqual('1', key)

    def test_cisco(self):
        lldp = session.lldp()
        self.assertEqual(lldp[4][0]['device_id'], 'SFIKT-34:d2')
        self.assertEqual(lldp[4][0]['local_port_num'], 4)
        self.assertEqual(lldp[4][0]['remote_port'], '3817c3c934d2')


if __name__ == "__main__":
    unittest.main()  # run all tests
