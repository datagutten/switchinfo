from django.test import TestCase
from switchinfo.SwitchSNMP import utils


class UtilsTestCase(TestCase):
    def test_mac_parse_oid(self):
        mac = utils.mac_parse_oid('0.37.69.50.202.174')
        self.assertEqual('00254532caae', mac)

    def test_table_index(self):
        row, col = utils.table_index('.1.3.6.1.2.1.17.4.3.1', 'iso.3.6.1.2.1.17.4.3.1.1.0.29.148.23.138.204')
        self.assertEqual(1, col)
        self.assertEqual('0.29.148.23.138.204', row)

    def test_table_index2(self):
        row, col = utils.table_index('.1.3.6.1.2.1.17.1.4.1', 'iso.3.6.1.2.1.17.1.4.1.1.23')
        self.assertEqual(1, col)
        self.assertEqual(23, row)

    def test_table_index3(self):
        row, col = utils.table_index('.1.3.6.1.2.1.17.4.3.1', '.1.3.6.1.2.1.17.4.3.1.1.108.78.246.48.248.26')
        self.assertEqual(1, col)
        self.assertEqual('108.78.246.48.248.26', row)
