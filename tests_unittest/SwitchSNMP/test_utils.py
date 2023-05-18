import datetime
import unittest

from switchinfo.SwitchSNMP import utils


class SNMPUtilsTestCase(unittest.TestCase):
    def test_timeticks(self):
        interval = utils.timeticks(290678791)
        expected = datetime.timedelta(days=33, hours=15, minutes=26, seconds=27, microseconds=910000)
        self.assertEqual(expected, interval)


if __name__ == "__main__":
    unittest.main()  # run all tests
