import datetime
import unittest

from switchinfo import SwitchSNMP

session = SwitchSNMP.SwitchSNMP('cisco', '127.0.0.1')


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
