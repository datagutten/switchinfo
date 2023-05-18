import unittest

from switchinfo import SwitchSNMP
from .snmp_data import get_file

session = SwitchSNMP.Cisco(*get_file('cisco'))
session_lldp = SwitchSNMP.Cisco(*get_file('lldp_cisco'))


class CiscoIOSTestCase(unittest.TestCase):
    def test_poe_cisco(self):
        poe = session.interface_poe()
        key = list(poe.keys())[0]
        self.assertEqual('1', key)

    def test_cisco(self):
        lldp = session_lldp.lldp()
        self.assertEqual(lldp[4][0]['device_id'], 'SFIKT-34:d2')
        self.assertEqual(lldp[4][0]['local_port_num'], 4)
        self.assertEqual(lldp[4][0]['remote_port'], '3817c3c934d2')


if __name__ == "__main__":
    unittest.main()  # run all tests
