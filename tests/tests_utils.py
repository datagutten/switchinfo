from django.test import TestCase
from switchinfo.SwitchSNMP import utils


class UtilsTestCase(TestCase):
    def test_mac_parse_oid(self):
        mac = utils.mac_parse_oid('0.37.69.50.202.174')
        self.assertEqual('00254532caae', mac)

