import datetime
import unittest

from switchinfo import SwitchSNMP
from .snmp_data import get_file

session = SwitchSNMP.SwitchSNMP(*get_file('cisco'))


class SwitchSNMPTestCase(unittest.TestCase):
    """
    Tests for generic SNMP calls
    """

    def test_uptime(self):
        uptime = session.uptime()
        self.assertIsInstance(uptime, datetime.timedelta)
        self.assertEqual(116, uptime.days)


if __name__ == "__main__":
    unittest.main()  # run all tests
